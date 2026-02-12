import streamlit as st
import os
from modules import database
from modules.medgemma_model import stream_nutrition_advice, is_model_ready
from modules.rag_engine import RAGEngine
from dotenv import load_dotenv


load_dotenv()
st.set_page_config(
    page_title="NutriMED AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure Database is Initialized
database.init_db()
rag=RAGEngine()

# Initialize Session State for Login
if 'user' not in st.session_state:
    st.session_state['user'] = None

# --- 2. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=80)
    st.title("NutriMED AI")
    st.caption("AI Clinical Nutritionist")
    st.markdown("---")
    
    # Model Status
    st.subheader("🤖 Model Status")
    if is_model_ready():
        st.success("✅ AI Model Ready (Ollama)")
    else:
        st.warning("⚠️ Model Loading... (Using Fallback)")
        st.caption("Make sure Ollama is running: `ollama serve`")
    
    st.markdown("---")
    
    # Vector Store Management
    st.subheader("📚 Clinical Guidelines")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📥 Load Guidelines", key="load_docs_btn", help="Load PDF guidelines into vector store (one-time)"):
            with st.spinner("Loading documents..."):
                try:
                    rag.load_pdf_guidelines()
                    st.success("✅ Guidelines loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error loading guidelines: {str(e)}")
    
    with col2:
        st.caption("Load PDFs once")
    
    st.markdown("---")
    
    # Menu Selection
    menu = st.radio("Navigate", ["📝 Register Patient", "🔐 Patient Login", "💬 AI Consultation"])
    
    st.markdown("---")
    if st.session_state['user']:
        st.success(f"Logged in as: **{st.session_state['user']['name']}**")
        if st.button("Logout"):
            st.session_state['user'] = None
            st.rerun()

# --- 3. PAGE: REGISTER PATIENT ---
if menu == "📝 Register Patient":
    st.title("📝 Patient Registration")
    st.markdown("Enter clinical details to generate a personalized diet plan.")
    
    # Initialize session state for condition
    if 'selected_condition' not in st.session_state:
        st.session_state['selected_condition'] = "General Health"
    
    st.markdown("---")
    st.subheader("🏥 Clinical Profile")
    
    # --- THE SMART DISEASE SELECTOR (Outside Form for Dynamic Display) ---
    st.session_state['selected_condition'] = st.selectbox(
        "Primary Medical Condition", 
        ["General Health", "Type 2 Diabetes", "Hypertension", "Anaemia", "PCOS", "Obesity"],
        index=["General Health", "Type 2 Diabetes", "Hypertension", "Anaemia", "PCOS", "Obesity"].index(st.session_state['selected_condition'])
    )
    
    # Display Dynamic Fields based on Selection (Before Form)
    specific_metrics_preview = {}
    health_goal_preview = "Maintain Health"
    
    if st.session_state['selected_condition'] == "Type 2 Diabetes":
        st.info("🩸 **Diabetes Specifics**")
        specific_metrics_preview['hba1c'] = st.number_input("Latest HbA1c (%)", 4.0, 15.0, 6.5, key="hba1c_preview")
        specific_metrics_preview['medication'] = st.selectbox("Medication Status", ["None (Diet Control)", "Metformin/Tablets", "Insulin"], key="med_preview")
        health_goal_preview = "Blood Sugar Control & Insulin Sensitivity"

    elif st.session_state['selected_condition'] == "Hypertension":
        st.info("❤️ **Heart Health Specifics**")
        c1, c2 = st.columns(2)
        specific_metrics_preview['bp_systolic'] = c1.number_input("Systolic BP (Top)", 90, 220, 120, key="bp_sys_preview")
        specific_metrics_preview['bp_diastolic'] = c2.number_input("Diastolic BP (Bottom)", 60, 130, 80, key="bp_dias_preview")
        health_goal_preview = "Manage Blood Pressure & Sodium Intake"

    elif st.session_state['selected_condition'] == "Anaemia":
        st.info("🩸 **Iron Deficiency Specifics**")
        specific_metrics_preview['hemoglobin'] = st.number_input("Hemoglobin Level (g/dL)", 5.0, 18.0, 11.0, key="hemo_preview")
        specific_metrics_preview['symptoms'] = st.multiselect("Symptoms", ["Fatigue", "Pale Skin", "Dizziness", "Hair Loss"], key="symp_preview")
        health_goal_preview = "Increase Iron Levels & Hemoglobin"

    elif st.session_state['selected_condition'] == "PCOS":
        st.info("🌸 **Hormonal Health Specifics**")
        specific_metrics_preview['periods'] = st.selectbox("Menstrual Cycle", ["Regular", "Irregular", "Absent"], key="periods_preview")
        specific_metrics_preview['weight_gain'] = st.checkbox("Difficulty losing weight?", value=True, key="wg_preview")
        health_goal_preview = "Hormonal Balance & Weight Management"

    elif st.session_state['selected_condition'] == "Obesity":
        st.info("⚖️ **Weight Management Specifics**")
        st.write(f"**Calculated BMI:** (Will be calculated from weight and height below)")
        specific_metrics_preview['target_weight_temp'] = st.number_input("Target Weight (kg)", 40.0, 150.0, 65.0, key="target_weight_preview")
        health_goal_preview = "Sustainable Weight Loss (Caloric Deficit)"

    st.markdown("---")
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        # --- Basic Demographics ---
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", 10, 100, 25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
        with col2:
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
            activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])

        # Prepare specific_metrics from preview data
        specific_metrics = {}
        health_goal = "Maintain Health"
        condition = st.session_state['selected_condition']
        
        if condition == "Type 2 Diabetes":
            specific_metrics['hba1c'] = specific_metrics_preview.get('hba1c', 6.5)
            specific_metrics['medication'] = specific_metrics_preview.get('medication', "None (Diet Control)")
            health_goal = specific_metrics_preview.get('health_goal', "Blood Sugar Control & Insulin Sensitivity")

        elif condition == "Hypertension":
            specific_metrics['bp_systolic'] = specific_metrics_preview.get('bp_systolic', 120)
            specific_metrics['bp_diastolic'] = specific_metrics_preview.get('bp_diastolic', 80)
            health_goal = specific_metrics_preview.get('health_goal', "Manage Blood Pressure & Sodium Intake")

        elif condition == "Anaemia":
            specific_metrics['hemoglobin'] = specific_metrics_preview.get('hemoglobin', 11.0)
            specific_metrics['symptoms'] = specific_metrics_preview.get('symptoms', [])
            health_goal = specific_metrics_preview.get('health_goal', "Increase Iron Levels & Hemoglobin")

        elif condition == "PCOS":
            specific_metrics['periods'] = specific_metrics_preview.get('periods', "Regular")
            specific_metrics['weight_gain'] = specific_metrics_preview.get('weight_gain', True)
            health_goal = specific_metrics_preview.get('health_goal', "Hormonal Balance & Weight Management")

        elif condition == "Obesity":
            bmi = weight / ((height/100)**2)
            specific_metrics['bmi'] = round(bmi, 1)
            specific_metrics['target_weight'] = specific_metrics_preview.get('target_weight_temp', weight-5)
            health_goal = specific_metrics_preview.get('health_goal', "Sustainable Weight Loss (Caloric Deficit)")

        # Submit Button
        submit = st.form_submit_button("Create Patient Profile")
        
        if submit:
            if name:
                success = database.add_patient(
                    name, age, gender, weight, height, activity, 
                    condition, specific_metrics, health_goal
                )
                if success:
                    st.success(f"✅ Profile created for **{name}**! Please go to Login.")
                    st.balloons()
                else:
                    st.error("User with this name already exists.")
            else:
                st.warning("Please enter a name.")

# --- 4. PAGE: LOGIN ---
elif menu == "🔐 Patient Login":
    st.title("🔐 Patient Login")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("Enter Full Name")
        if st.button("Login"):
            patient = database.get_patient(username)
            if patient:
                # Convert sqlite3.Row to dictionary
                st.session_state['user'] = database.row_to_dict(patient)
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Patient not found. Please Register.")

# --- 5. PAGE: AI CONSULTATION (Main Chat) ---
elif menu == "💬 AI Consultation":
    if st.session_state['user']:
        user = st.session_state['user']
        
        # --- HEADER ---
        st.title(f"👋 Hello, {user['name']}")
        st.markdown("Chat with **MedGemma AI** - Your AI Clinical Nutritionist")
        
        # Clinical Dashboard
        with st.expander("📄 View My Clinical Profile", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.metric("Condition", user['condition'])
            c2.metric("Weight", f"{user['weight_kg']} kg")
            c3.metric("Goal", user['health_goal'])
            st.caption(f"Medical Context: {database.get_patient_context_string(user['name'])}")

        st.markdown("### 🥗 AI Nutrition Chat")
        
        # Info about the model
        info_col1, info_col2 = st.columns([3, 1])
        with info_col1:
            st.info(f"🎯 Focused on: **{user['condition']}** guidelines | 🧠 Powered by: **MedGemma (Ollama)**")
        with info_col2:
            model_status = "✅ Online" if is_model_ready() else "⚠️ Fallback"
            st.caption(f"Model: {model_status}")

        # --- CHAT INTERFACE ---
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    st.markdown(f"<div style='font-size: 16px; line-height: 1.6;'>{message['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])

        # Input
        if prompt := st.chat_input("Ask about your diet (e.g., 'Can I eat mangoes?')"):
            # 1. User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # 2. AI Response with Streaming
            with st.chat_message("assistant"):
                try:
                    # Get patient context from database
                    patient_context = database.get_patient_context_string(user['name'])
                    
                    # Retrieve clinical documents from vector store with spinner
                    with st.spinner("🔍 Retrieving clinical guidelines..."):
                        
                        retrieved_context, retrieved_docs =rag.retrieve_context (
                            query=prompt,
                            max_results=4
                        )
                    
                    # Combine patient data + retrieved documents as context
                    combined_context = f"""{patient_context}

RELEVANT CLINICAL GUIDELINES:
{retrieved_context}"""
                    
                    # Prepare patient data for the model
                    patient_data = {
                        'age': user.get('age', 'Not specified'),
                        'weight_kg': user.get('weight_kg', 'Not specified'),
                        'medical_history': user.get('condition', 'General Health'),
                        'dietary_preference': user.get('dietary_preference', 'Not specified'),
                    }
                    
                    # Stream the response from medgemma_model in real-time with larger font
                    st.markdown("<div style='font-size: 16px; line-height: 1.6;'>", unsafe_allow_html=True)
                    response_text = st.write_stream(
                        stream_nutrition_advice(
                            patient_data=patient_data,
                            query=prompt,
                            context=combined_context,
                            strict_mode=True  
                        )
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    # Display retrieved sources in an expander
                    if retrieved_docs:
                        with st.expander("📚 Clinical Sources Used", expanded=False):
                            for i, doc in enumerate(retrieved_docs, 1):
                                st.caption(f"**Source {i}:** {doc.metadata.get('source', 'Unknown')}")
                                st.text(doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content)
                                st.divider()
                    else:
                        st.info("ℹ️ No clinical documents found for this query in the guidelines database.")
                    
                except Exception as e:
                    st.error(f"⚠️ An error occurred: {str(e)}")
                    st.info("💡 Fallback: Using default nutrition guidance")

    else:
        st.warning("Please **Login** to access the AI Consultation.")