# AI Voice Agent System - User Manual

## 📖 Complete Guide to Using Your AI Voice Agent

This manual will help you get the most out of your AI Voice Agent System. Whether you're a business owner, manager, or staff member, this guide covers everything you need to know.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Your Business](#managing-your-business)
4. [Testing Voice Processing](#testing-voice-processing)
5. [Understanding Analytics](#understanding-analytics)
6. [Phone Integration](#phone-integration)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Getting Started

### Accessing Your Dashboard

1. Open your Heroku app URL (e.g., `https://your-app-name.herokuapp.com`)
2. Click "🚀 Open Dashboard" on the homepage
3. You'll see the main dashboard with four tabs: Overview, Business, Test Voice, and Settings

### First-Time Setup

Before your AI agent can handle calls, you need to:

1. **Create your business profile**
2. **Add your services and pricing**
3. **Test the voice processing**
4. **Configure your phone number** (optional)

## Dashboard Overview

### Overview Tab

The Overview tab shows your system's current status and key metrics:

**System Status Section:**
- **API Status**: Shows if your system is online and ready
- **Voice Processing**: Indicates if AI conversation is working
- **Phone Integration**: Shows phone system readiness

**Quick Stats Section:**
- **Total Businesses**: Number of businesses configured
- **Total Calls Today**: Calls received today
- **Appointments Booked**: Successful bookings today

**Quick Actions:**
- Create new business
- Test voice AI
- Refresh system status

### Navigation Tips

- Click any tab to switch between sections
- Green indicators mean systems are working
- Orange indicators mean limited functionality
- Red indicators mean there's an issue that needs attention

## Managing Your Business

### Creating a New Business

1. Go to the **Business** tab
2. Fill in the business information:
   - **Business Name**: Your business name (required)
   - **Phone Number**: Your business phone (optional)
   - **Email**: Contact email (optional)
   - **Description**: Brief description of your business
3. Click **Create Business**

### Business Information Best Practices

**Business Name:**
- Use your actual business name
- Include location if you have multiple branches
- Example: "Al-Noor Medical Clinic - Riyadh"

**Phone Number:**
- Use international format: +966501234567
- This will be used for customer confirmations

**Description:**
- Keep it brief but informative
- Include your main services
- Example: "General medical clinic offering consultations, checkups, and specialist referrals"

### Managing Multiple Businesses

If you manage multiple businesses:
1. Create separate business profiles for each location
2. Each business can have its own phone number
3. Analytics are tracked separately for each business

## Testing Voice Processing

### Using Quick Test Messages

The Test Voice tab includes pre-built test messages:

**Arabic Tests:**
- "مرحبا، أريد حجز موعد" (Book appointment)
- "ما هي ساعات العمل؟" (Business hours)

**English Tests:**
- "Hello, what are your prices?" (Ask about pricing)
- "What services do you offer?" (Service inquiry)

### Custom Message Testing

1. Select your business from the dropdown
2. Type your custom message in Arabic or English
3. Click "Test Message"
4. Review the AI response and intent detection

### Understanding Test Results

Each test shows:
- **Customer Message**: What the customer said
- **AI Response**: How your agent responded
- **Intent Detected**: What the AI understood (booking, pricing, hours)
- **Confidence Level**: How sure the AI is about the intent
- **Action Required**: Whether follow-up is needed

### Testing Best Practices

**Test Regularly:**
- Test after making any changes
- Try different ways of asking the same question
- Test both Arabic and English

**Common Test Scenarios:**
- Appointment booking requests
- Pricing inquiries
- Business hours questions
- Service availability
- Cancellation requests

## Understanding Analytics

### System Health Monitoring

The dashboard continuously monitors:
- API connectivity
- Voice processing capability
- Phone system status
- Database performance

### Call Analytics (Future Feature)

Once you start receiving calls, you'll see:
- Hourly call distribution
- Peak calling times
- Appointment booking success rates
- Customer satisfaction metrics

### Performance Metrics

Key metrics to monitor:
- **Response Time**: How quickly the AI responds
- **Intent Accuracy**: How well it understands customers
- **Booking Success Rate**: Percentage of successful appointments
- **Customer Satisfaction**: Based on call completion

## Phone Integration

### Setting Up Your Phone Number

1. **Purchase a Twilio Phone Number**:
   - Log into your Twilio console
   - Buy a Saudi phone number (+966)
   - Choose a memorable number for your business

2. **Configure Webhook**:
   - In Twilio console, go to Phone Numbers
   - Click on your number
   - Set webhook URL to: `https://your-app-name.herokuapp.com/api/voice/webhook/twilio/voice`
   - Set HTTP method to POST

3. **Test the Integration**:
   - Call your new number
   - The AI should answer and respond to your voice
   - Try booking an appointment

### Phone System Features

**Automatic Call Handling:**
- AI answers within 2-3 rings
- Greets customers in Arabic or English
- Handles multiple calls simultaneously

**Appointment Booking:**
- Checks availability in real-time
- Books appointments automatically
- Sends SMS confirmations

**Call Routing:**
- Routes complex queries to human staff
- Escalates when needed
- Maintains conversation context

## Troubleshooting

### Common Issues and Solutions

**Dashboard Won't Load:**
- Check your internet connection
- Try refreshing the page
- Clear your browser cache

**Voice Processing Shows "Error":**
- Verify your OpenAI API key is correct
- Check you have sufficient OpenAI credits
- Test with a simple message first

**Phone Calls Not Working:**
- Confirm Twilio webhook URL is correct
- Check Twilio account balance
- Verify phone number configuration

**Business Creation Fails:**
- Ensure business name is not empty
- Check for special characters in fields
- Try with minimal information first

### Getting Help

**Self-Service Options:**
1. Check the system status in Overview tab
2. Review error messages carefully
3. Try the suggested solutions above

**When to Contact Support:**
- Persistent system errors
- API key configuration issues
- Phone integration problems
- Billing or account questions

## Best Practices

### Optimizing AI Responses

**Train Your AI:**
- Test common customer questions
- Review AI responses regularly
- Update business information as needed

**Business Information:**
- Keep services and pricing current
- Update business hours seasonally
- Add special offers or promotions

### Customer Experience

**Phone Etiquette:**
- AI is programmed to be polite and professional
- Handles both Arabic and English naturally
- Escalates complex requests appropriately

**Appointment Management:**
- Review bookings daily
- Confirm appointments with customers
- Update availability regularly

### Security and Privacy

**Data Protection:**
- Customer information is encrypted
- Call recordings are stored securely
- GDPR compliance maintained

**Access Control:**
- Use strong passwords for all accounts
- Limit dashboard access to authorized staff
- Regular security updates applied automatically

### Performance Monitoring

**Daily Checks:**
- Review system status
- Check for missed calls
- Monitor appointment bookings

**Weekly Reviews:**
- Analyze call patterns
- Review AI response quality
- Update business information

**Monthly Optimization:**
- Review analytics trends
- Optimize peak hour coverage
- Plan capacity improvements

## Advanced Features

### Custom Voice Training

For businesses with specific terminology:
- Contact support for custom voice training
- Provide sample conversations
- Industry-specific vocabulary can be added

### Multi-Language Support

Currently supports:
- Arabic (Saudi dialect)
- English (international)
- Additional languages available on request

### Integration Options

**CRM Integration:**
- Connect with existing customer databases
- Sync appointment data
- Export call logs and analytics

**Calendar Integration:**
- Sync with Google Calendar
- Outlook integration available
- Real-time availability checking

## Support and Resources

### Documentation
- Setup Guide: Step-by-step deployment
- API Documentation: Technical reference
- Video Tutorials: Visual learning resources

### Contact Support
- Email: support@your-domain.com
- WhatsApp: +966-XXX-XXXX
- Live Chat: Available in dashboard
- Response Time: Within 24 hours

### Community
- User Forum: Share tips and experiences
- Best Practices Guide: Learn from other businesses
- Feature Requests: Suggest improvements

---

This manual is regularly updated. Check back for new features and improvements to your AI Voice Agent System.

