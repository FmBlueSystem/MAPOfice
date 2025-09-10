#!/bin/bash

echo "🔧 Installing Gemini dependencies..."

# Activate virtual environment
source .venv/bin/activate

# Install google-generativeai with force reinstall
pip install --force-reinstall google-generativeai

# Verify installation
python -c "
try:
    import google.generativeai as genai
    print('✅ Gemini successfully installed and available')
    
    # Configure with your API key
    genai.configure(api_key='AIzaSyAfBzRWiaoGzVOGwHvvb7kALZW8_UruYhk')
    models = list(genai.list_models())
    print(f'✅ API key verified - Found {len(models)} models')
    print('🎯 Ready for Multi-LLM with 95% cost savings!')
    
except Exception as e:
    print(f'❌ Error: {e}')
"

echo "🚀 Installation complete! You can now run the app with Gemini support."