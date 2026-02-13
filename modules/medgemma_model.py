"""
This module provides a LangChain-integrated interface to Ollama language models
for generating personalized nutrition advice. It supports streaming, caching, and
enterprise-level error handling.

Uses Ollama with MedAIBase/MedGemma1.5:4b model for optimal medical domain performance.
"""

import os
import logging
from typing import Dict, Any, Optional, List
import warnings
import json

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class MedGemmaModel:
    """Production-grade handler for MedGemma medical language model using Ollama."""
    
    def __init__(self):
        """Initialize the MedGemma model with LangChain-Ollama integration."""
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'MedAIBase/MedGemma1.5:4b')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.temperature = float(os.getenv('MODEL_TEMPERATURE', '0.4')) 
        self.top_p = float(os.getenv('MODEL_TOP_P', '0.9'))
        self.top_k = int(os.getenv('MODEL_TOP_K', '50'))
        self.max_length = int(os.getenv('MODEL_MAX_LENGTH', '3000'))
        self.num_predict = int(os.getenv('NUM_PREDICT', '3000'))
        
        self.llm = None
        
        logger.info(f"MedGemmaModel (Ollama) configuration:")
        logger.info(f"  Model: {self.ollama_model}")
        
        self._load_ollama_model()
    
    def _load_ollama_model(self) -> None:
        """Load the Ollama model with LangChain ChatOllama integration."""
        try:
            from langchain_ollama import ChatOllama
            
            logger.info(f"Connecting to Ollama server: {self.ollama_base_url}")
            
            self.llm = ChatOllama(
                base_url=self.ollama_base_url,
                model=self.ollama_model,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                num_predict=self.num_predict,
                repeat_penalty=1.1,
                keep_alive="5m",
            )
            
            logger.info("Ollama ChatOllama initialized successfully")
            
        except ImportError as e:
            logger.error(f"Required dependency missing: {e}")
            self.llm = None
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            self.llm = None
    
    def get_langchain_model(self):
        """Get the LangChain ChatOllama model for use in chains and agents."""
        if self.llm is None:
            raise RuntimeError("ChatOllama model not initialized.")
        return self.llm
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference."""
        return self.llm is not None
    
    def _create_nutrition_prompt(
        self,
        patient_data: Dict[str, Any],
        query: str,
        context: Optional[str] = None,
        strict_mode: bool = False,
    ) -> str:
        """Create a nutrition advice prompt with patient data and clinical context."""
        name = patient_data.get('name', 'Patient')
        age = patient_data.get('age', 'Not specified')
        gender = patient_data.get('gender', 'Not specified')
        weight = patient_data.get('weight_kg', 'Not specified')
        condition = patient_data.get('condition', 'General Health')
        goal = patient_data.get('health_goal', 'Better Health')
        
        metrics_str = "None"
        raw_metrics = patient_data.get('specific_metrics', {})
        if isinstance(raw_metrics, str):
            try:
                metrics_dict = json.loads(raw_metrics)
                metrics_str = ", ".join([f"{k}: {v}" for k, v in metrics_dict.items()])
            except:
                metrics_str = raw_metrics
        elif isinstance(raw_metrics, dict):
            metrics_str = ", ".join([f"{k}: {v}" for k, v in raw_metrics.items()])

        # --- THE FLEXIBLE SYSTEM PROMPT ---
        system_prompt = f"""You are Dr. MedGemma, an expert Clinical Nutritionist specializing in Indian diets.

PATIENT {name} ({age}y / {gender})
- Condition: {condition} (CRITICAL)
- Markers: {metrics_str}
- Goal: {goal}

CLINICAL GUIDELINES:
{context if context else "Use standard medical knowledge."}

**RESPONSE STRATEGY (ADAPT TO USER):**
First Mention which information You are using to respond:
example:Based on the clinical guidelines provided, including the InSH Consensus Guideline for the Hypertension, 2023, and the ICMR Guidelines for Management of Type 2 Diabetes, I can give you specific advice regarding your diet.
Do not show your thinking process do the thinking in background and repond to the user query with relevent information.

1. **IF USER ASKS ABOUT A SPECIFIC FOOD (e.g., "Can I eat X?"):**
   - **Verdict**: Start with a clear "Yes", "No", or "Limit".
   - **Science**: Explain the specific impact on their {condition} (e.g., blood sugar spike, sodium load).
   - **Swap**: Suggest a specific, tasty Indian alternative.

2. **IF USER ASKS FOR A PLAN/ROUTINE/DIET:**
   - **Structure**: Create a detailed daily schedule (Breakfast, Lunch, Evening Snack, Dinner).
   - **Foods**: Suggest specific Indian dishes (e.g., Moong Dal Chilla, Ragi Roti, Curd).
   - **Details**: Mention portion sizes and why this helps their goals.

3. **IF USER ASKS A GENERAL QUESTION:**
   - Provide a comprehensive, detailed explanation using bullet points.
   - Be educational and encouraging.

**CRITICAL RULES:**
- Always address the patient by name.
- Do NOT be vague. Do NOT just say "Eat healthy." Give examples.
- Use the provided Clinical Guidelines as the primary source of truth.
"""

        full_prompt = f"""<start_of_turn>user
{system_prompt}

PATIENT REQUEST: "{query}"

ANSWER:<end_of_turn>
<start_of_turn>model"""
        
        return full_prompt
    
    def generate_nutrition_advice(
        self,
        patient_data: Dict[str, Any],
        query: str,
        context: Optional[str] = None,
        strict_mode: bool = False,
    ) -> str:
        """Generate personalized nutrition advice using the Ollama ChatOllama model."""
        try:
            if not self.is_ready():
                return self._fallback_response(patient_data, query, context)
            
            prompt = self._create_nutrition_prompt(patient_data, query, context, strict_mode)
            
            logger.info(f"Generating advice for {patient_data.get('name', 'Patient')}...")
            
            response = self.llm.invoke(prompt)
            advice = response.content if hasattr(response, 'content') else str(response)
            
            return advice
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return self._fallback_response(patient_data, query, context)
    
    def stream_nutrition_advice(
        self,
        patient_data: Dict[str, Any],
        query: str,
        context: Optional[str] = None,
        strict_mode: bool = False,
    ):
        """Stream nutrition advice token by token for real-time output using Ollama."""
        try:
            if not self.is_ready():
                yield self._fallback_response(patient_data, query, context)
                return
            
            prompt = self._create_nutrition_prompt(patient_data, query, context, strict_mode)
            
            logger.info(f"Streaming advice for {patient_data.get('name', 'Patient')}...")
            
            for chunk in self.llm.stream(prompt):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                yield content
                
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield self._fallback_response(patient_data, query, context)
    
    def _fallback_response(
        self,
        patient_data: Dict[str, Any],
        query: str,
        context: Optional[str] = None
    ) -> str:
        """Provide informative fallback response when model is unavailable."""
        return "⚠️ AI Model Unavailable. Please ensure Ollama is running (`ollama serve`)."


# Singleton instance for model management
_model_instance = None


def get_model() -> MedGemmaModel:
    """Get or create the global MedGemmaModel instance (singleton pattern)."""
    global _model_instance
    if _model_instance is None:
        _model_instance = MedGemmaModel()
    return _model_instance


def get_langchain_model():
    """Get the LangChain model wrapper for use in chains and agents."""
    model = get_model()
    return model.get_langchain_model()


def is_model_ready() -> bool:
    """Check if the model is ready for inference."""
    model = get_model()
    return model.is_ready()


def generate_nutrition_advice(
    patient_data: Dict[str, Any],
    query: str,
    context: Optional[str] = None,
    strict_mode: bool = False,
) -> str:
    """Convenience function to generate nutrition advice."""
    model = get_model()
    return model.generate_nutrition_advice(patient_data, query, context, strict_mode)


def stream_nutrition_advice(
    patient_data: Dict[str, Any],
    query: str,
    context: Optional[str] = None,
    strict_mode: bool = False,
):
    """Stream nutrition advice token by token for real-time output."""
    model = get_model()
    yield from model.stream_nutrition_advice(patient_data, query, context, strict_mode)


if __name__ == "__main__":
    # Example usage test
    logging.basicConfig(level=logging.INFO)
    model = get_model()
    if model.is_ready():
        print("✅ Model Ready")
    else:
        print("❌ Model Failed")