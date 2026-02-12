"""
MedGemma-Nutritionist Setup Script
Auto-generates project structure and initializes components
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary project directories."""
    directories = [
        'data',
        'assets/guidelines',
        'modules',
        'notebooks'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created/Verified directory: {directory}")

def create_env_template():
    """Create .env template file."""
    env_content = """# MedGemma-Nutritionist Configuration
# Copy this file to .env and fill in your API keys

# HuggingFace API Key (for model access)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# LangSmith API Key (optional, for debugging)
LANGSMITH_API_KEY=your_langsmith_api_key_here

# Database Configuration
DATABASE_PATH=data/patients.db
VECTOR_DB_PATH=data/chroma_db

# Model Configuration
MODEL_NAME=medgemma-7b
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env template file")
    else:
        print("⚠️ .env file already exists, skipping creation")

def verify_structure():
    """Verify complete project structure."""
    required_files = [
        'app.py',
        'setup_project.py',
        '.env',
        'requirements.txt',
        'README.md'
    ]
    
    required_dirs = [
        'assets/guidelines',
        'data',
        'modules'
    ]
    
    required_modules = [
        'modules/__init__.py',
        'modules/database.py',
        'modules/medgemma_model.py',
        'modules/rag_engine.py'
    ]
    
    print("\n📋 Project Structure Verification:")
    print("=" * 50)
    
    # Check files
    print("\n📄 Files:")
    for file in required_files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"{exists} {file}")
    
    # Check directories
    print("\n📁 Directories:")
    for dir_path in required_dirs:
        exists = "✅" if os.path.exists(dir_path) else "❌"
        print(f"{exists} {dir_path}")
    
    # Check modules
    print("\n🐍 Modules:")
    for module in required_modules:
        exists = "✅" if os.path.exists(module) else "❌"
        print(f"{exists} {module}")

def main():
    print("🚀 MedGemma-Nutritionist Setup")
    print("=" * 50)
    
    try:
        create_directories()
        create_env_template()
        verify_structure()
        
        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        print("\n📝 Next Steps:")
        print("1. Fill in your API keys in .env file")
        print("2. Add PDF guidelines to assets/guidelines/")
        print("3. Run: streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
