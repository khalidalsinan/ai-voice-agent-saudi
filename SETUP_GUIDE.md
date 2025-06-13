# AI Voice Agent System - Simple Setup Guide

## 🚀 One-Click Deployment to Heroku

This guide will help you deploy your AI Voice Agent System to Heroku with just a few clicks. No technical expertise required!

### What You'll Get

Your AI Voice Agent System includes:

- **Bilingual Voice Processing**: Handles customer calls in Arabic and English
- **Smart Appointment Booking**: Automatically schedules appointments
- **Business Management**: Complete business configuration system
- **Professional Dashboard**: Beautiful web interface to manage everything
- **Phone Integration**: Ready for Twilio phone number integration
- **Analytics**: Detailed insights into customer interactions

### Prerequisites

Before you start, you'll need:

1. **Heroku Account** (free): Sign up at https://heroku.com
2. **API Keys** (you'll get these during setup):
   - OpenAI API key for conversation processing
   - ElevenLabs API key for voice synthesis
   - Twilio credentials for phone integration

### Step 1: Deploy to Heroku

Click this button to deploy your AI Voice Agent System:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/your-username/ai-voice-agent-saudi)

**What happens when you click:**
1. Heroku will create a new app for you
2. It will automatically install all required components
3. A PostgreSQL database will be set up
4. Your system will be ready to configure

### Step 2: Configure Your API Keys

After deployment, you'll need to add your API keys:

#### 2.1 Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### 2.2 Get ElevenLabs API Key
1. Go to https://elevenlabs.io/speech-synthesis
2. Sign up for an account
3. Go to your profile settings
4. Copy your API key

#### 2.3 Get Twilio Credentials
1. Go to https://console.twilio.com
2. Sign up for an account
3. From your dashboard, copy:
   - Account SID
   - Auth Token

#### 2.4 Add Keys to Heroku
1. Go to your Heroku dashboard
2. Click on your app name
3. Go to "Settings" tab
4. Click "Reveal Config Vars"
5. Add these variables:
   - `OPENAI_API_KEY`: Your OpenAI key
   - `ELEVENLABS_API_KEY`: Your ElevenLabs key
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token

### Step 3: Test Your System

1. **Open Your App**: Click "Open app" in Heroku dashboard
2. **Access Dashboard**: Click "🚀 Open Dashboard" on the homepage
3. **Create a Business**: Go to the "Business" tab and create your first business
4. **Test Voice Processing**: Go to "Test Voice" tab and try the sample messages

### Step 4: Set Up Phone Integration (Optional)

To receive real customer calls:

1. **Buy a Phone Number** in Twilio console
2. **Configure Webhook**: Set webhook URL to `https://your-app-name.herokuapp.com/api/voice/webhook/twilio/voice`
3. **Test**: Call your new number to test the voice agent

### Troubleshooting

**App won't start?**
- Check that all API keys are correctly set in Config Vars
- Look at the logs in Heroku dashboard for error messages

**Voice processing not working?**
- Verify your OpenAI and ElevenLabs API keys are valid
- Check you have sufficient credits in both accounts

**Phone calls not working?**
- Ensure Twilio webhook URL is correctly configured
- Verify your Twilio account has sufficient balance

### Cost Breakdown

**Heroku Hosting**: $7-25/month (depending on plan)
**API Costs per month** (estimated for 1000 calls):
- OpenAI: $10-30
- ElevenLabs: $20-50
- Twilio: $15-40

**Total Monthly Cost**: $50-150 per business

### Support

If you need help:
1. Check the troubleshooting section above
2. Review the logs in your Heroku dashboard
3. Test individual components using the dashboard

Your AI Voice Agent System is now ready to handle customer calls and book appointments automatically!

