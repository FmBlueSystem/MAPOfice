# Multi-LLM Setup Guide for Music Analyzer Pro Enhanced

## Overview

Music Analyzer Pro Enhanced now supports multiple LLM providers with automatic cost optimization and fallback support. You can use either **Google Gemini** (recommended for cost) or **OpenAI** (higher quality) for AI music analysis.

## Cost Comparison (per 1 million tokens)

| Provider | Model | Input Cost | Output Cost | Total Cost* |
|----------|-------|------------|-------------|-------------|
| **🏆 Gemini** | gemini-1.5-flash | $0.075 | $0.30 | **$0.38** |
| Gemini | gemini-1.5-pro | $2.50 | $10.00 | $12.50 |
| OpenAI | gpt-4o-mini | $0.15 | $0.60 | $0.75 |
| OpenAI | gpt-4o | $2.50 | $10.00 | $12.50 |

*Approximate cost for typical music analysis (500 input + 200 output tokens)

## Quick Setup

### Option 1: Google Gemini (Recommended - 95% cheaper!)

1. **Get a Gemini API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Click "Get API key" → "Create API key in new project"
   - Copy your API key

2. **Configure .env file:**
   ```bash
   # Update these lines in your .env file:
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```

### Option 2: OpenAI

1. **Get an OpenAI API Key:**
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Copy your API key (starts with `sk-`)

2. **Configure .env file:**
   ```bash
   # Update these lines in your .env file:
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

## Advanced Configuration

### Dual Provider Setup (Automatic Fallback)

Configure both providers for maximum reliability:

```bash
# Primary provider (will try this first)
LLM_PROVIDER=gemini
LLM_FALLBACK_ENABLED=true

# Gemini configuration
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-1.5-flash

# OpenAI configuration (fallback)
OPENAI_API_KEY=sk-your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Available Models

**Gemini Models:**
- `gemini-1.5-flash` - Fastest and cheapest ⭐
- `gemini-1.5-pro` - Higher quality, more expensive
- `gemini-pro` - Legacy model

**OpenAI Models:**
- `gpt-4o-mini` - Most cost-effective OpenAI option ⭐
- `gpt-4o` - Balanced performance
- `gpt-4` - Highest quality, most expensive

## Getting API Keys

### Google Gemini (Free tier available)
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Click "Get API key"
4. Create a new project or select existing
5. Copy the generated API key

**Free Tier:** 15 requests per minute, 1 million tokens per day

### OpenAI (Pay per use)
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

**Pricing:** Pay per token used, minimum $5 credit

## Verification

After configuration, run the application and check the console output:

```
✅ Multi-LLM initialized with providers: gemini
💰 Cost estimates per 1M tokens:
  Gemini: $0.075 input / $0.300 output
```

## Troubleshooting

### "No LLM providers configured"
- Check that your API key is correctly added to the `.env` file
- Ensure the key doesn't contain extra spaces or quotes
- For Gemini: Install dependencies with `pip install google-generativeai`

### "API key invalid" 
- Verify the API key is correct and active
- For OpenAI: Ensure key starts with `sk-`
- For Gemini: Check key was generated correctly

### "Rate limit exceeded"
- Wait a few minutes before retrying
- Consider switching providers in `.env`: change `LLM_PROVIDER=gemini` to `LLM_PROVIDER=openai`

## Benefits of Multi-LLM Architecture

✅ **Cost Optimization**: Automatically uses cheapest available provider  
✅ **High Availability**: Falls back to secondary provider if primary fails  
✅ **Easy Switching**: Change providers by updating one environment variable  
✅ **Provider Diversity**: No vendor lock-in, compare results across models  

## Example Analysis Output

With AI analysis enabled, you'll get enhanced metadata:

```
🎵 Track: Song.mp3
🎯 Genre: Electronic / Deep House
🎭 Mood: Uplifting, Energetic
📅 Era: 2020s
🏷️ Tags: progressive, melodic, dancefloor
🤖 Analyzed with: Gemini (gemini-1.5-flash)
💰 Cost: ~$0.0003 per track
```

---

Need help? The application provides detailed console output about provider status and any configuration issues.