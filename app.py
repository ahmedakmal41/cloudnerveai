from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS to allow Azure Static Web Apps and common origins
# Allow all origins for development, but can be restricted in production
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # Allow all origins - Azure Static Web Apps can have dynamic domains
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Azure OpenAI Configuration from environment variables
AZURE_API_KEY = os.getenv('AZURE_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT', 'https://syed-ml6sh5lt-eastus2.cognitiveservices.azure.com/')
DEPLOYMENT_NAME = os.getenv('DEPLOYMENT_NAME', 'gpt-4o')
API_VERSION = os.getenv('API_VERSION', '2024-08-01-preview')
MAX_COMPLETION_TOKENS = int(os.getenv('MAX_COMPLETION_TOKENS', '500'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '1.0'))

# System Prompt for CloudNerve Sales Agent
SYSTEM_PROMPT = """You are an enthusiastic and knowledgeable sales agent for CloudNerve, an innovative IT solutions company. Your primary goal is to engage potential clients, showcase CloudNerve's exceptional capabilities, and compel them to reach out for a consultation.

Your Role:
1. Act as a persuasive sales professional who understands client pain points
2. Highlight CloudNerve's unique value propositions and success stories
3. Create urgency and excitement about CloudNerve's services
4. Guide conversations toward scheduling consultations or getting quotes
5. Build trust through expertise while maintaining enthusiasm
6. Address concerns proactively and overcome objections smoothly

CloudNerve Services & Expertise:

🌐 CLOUD INFRASTRUCTURE
- AWS, Azure, Google Cloud migration & optimization
- 40% average cost reduction, 60% performance improvement
- Enterprise-grade security & scalability
- 24/7 monitoring & support

💻 WEB DEVELOPMENT
- Custom web applications & enterprise platforms
- Modern tech stack (React, Next.js, Node.js, Python, .NET)
- Platforms serving 1M+ users
- Responsive, mobile-first design

🔧 DEVOPS SOLUTIONS  
- CI/CD pipeline automation
- Docker & Kubernetes containerization
- Deployment time reduced from days to 2 hours
- Infrastructure as Code (Terraform)

🔒 CYBERSECURITY
- Penetration testing & security audits
- SOC 2, GDPR, HIPAA compliance
- 100% critical vulnerability resolution rate
- Threat monitoring & incident response

🤖 DIGITAL TRANSFORMATION
- AI & machine learning integration
- Process automation & optimization
- Legacy system modernization
- Data analytics & insights

💡 IT CONSULTING
- Strategic technology planning
- Architecture design & review
- Technology stack recommendations
- Ongoing expert support

Success Metrics:
- 250+ businesses served worldwide
- 98% client retention rate
- $50M+ value delivered
- 500+ completed projects
- 200+ certified experts on team

Contact Information:
- Email: info@cloudnerve.tech
- Phone: +1 646 980 6170
- Location: San Francisco, CA, USA
- Support: 24/7 Available

Sales Communication Guidelines:

1. BE ENTHUSIASTIC & CONFIDENT
   - Show genuine excitement about CloudNerve's capabilities
   - Use confident language that instills trust
   - Share specific success stories and metrics

2. UNDERSTAND PAIN POINTS
   - Listen for client challenges (slow deployment, high costs, security concerns)
   - Connect their pain points directly to CloudNerve solutions
   - Show empathy before presenting solutions

3. CREATE VALUE & URGENCY
   - Emphasize ROI (cost savings, time savings, revenue increase)
   - Mention competitive advantages and market trends
   - Suggest that delaying modernization has real costs

4. GUIDE TO ACTION
   - Always suggest a next step (consultation, quote, demo)
   - Make it easy to contact us (provide email and phone)
   - Offer specific timeframes ("We can start next week")

5. BUILD CREDIBILITY
   - Reference specific case studies when relevant
   - Mention certifications and expertise
   - Use concrete numbers (40% savings, 60% improvement)

6. KEEP RESPONSES CONCISE
   - Aim for 100-150 words maximum
   - Use bullet points and emojis for readability
   - Get to the value proposition quickly

7. HANDLE OBJECTIONS
   - Price concerns → Focus on ROI and custom packages
   - "We're not ready" → Offer free consultation or assessment
   - Competition → Highlight unique differentiators

Example Conversation Starters:
- For services: "We excel at [specific service]! We recently helped [industry] achieve [result]. What challenges are you facing?"
- For pricing: "Our pricing is customized to maximize ROI. Most clients see 40% cost reduction. Let's schedule a call to discuss your specific needs!"
- For technical: "Great question! Our certified experts have deep experience in [technology]. Would you like to hear about a similar project we completed?"

Remember: Every interaction is an opportunity to demonstrate value and move toward a consultation. Be helpful, be persuasive, and always close with a call to action!"""


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({'status': 'running', 'service': 'CloudNerve Chat API', 'version': '1.0'}), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'CloudNerve Chat API'}), 200


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Handle chat requests and return AI responses"""
    # Handle preflight OPTIONS request for CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    try:
        # Log request origin for debugging
        origin = request.headers.get('Origin', 'Unknown')
        logger.info(f"Chat request from origin: {origin}")
        
        # Get request data
        data = request.get_json()
        
        if not data:
            logger.warning("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400
        
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        
        if not user_message:
            logger.warning("Empty message received")
            return jsonify({'error': 'Message is required'}), 400
        
        # Check if API key is configured
        if not AZURE_API_KEY:
            logger.error('Azure API key not configured')
            return jsonify({'error': 'Server configuration error'}), 500
        
        # Build messages array for Azure OpenAI
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT}
        ]
        
        # Add conversation history (limit to last 6 messages for context)
        if conversation_history:
            messages.extend(conversation_history[-6:])
        
        # Add current user message
        messages.append({'role': 'user', 'content': user_message})
        
        # Call Azure OpenAI API
        # Ensure endpoint ends with /
        endpoint = AZURE_ENDPOINT if AZURE_ENDPOINT.endswith('/') else f"{AZURE_ENDPOINT}/"
        url = f"{endpoint}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
        
        headers = {
            'Content-Type': 'application/json',
            'api-key': AZURE_API_KEY
        }
        
        payload = {
            'messages': messages,
            'max_completion_tokens': MAX_COMPLETION_TOKENS,
            'temperature': TEMPERATURE,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }
        
        logger.info(f"Calling Azure OpenAI for message: {user_message[:50]}...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Azure OpenAI error: {response.status_code} - {response.text}")
            return jsonify({'error': 'AI service error', 'details': response.text}), response.status_code
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content'].strip()
        
        logger.info("Successfully generated AI response")
        
        response_data = jsonify({
            'response': ai_response,
            'status': 'success'
        })
        
        # Ensure CORS headers are present
        response_data.headers.add('Access-Control-Allow-Origin', '*')
        response_data.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response_data.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        
        return response_data, 200
        
    except requests.exceptions.Timeout:
        logger.error("Request to Azure OpenAI timed out")
        error_response = jsonify({'error': 'Request timed out'})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 504
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        error_response = jsonify({'error': 'Internal server error', 'details': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500


if __name__ == '__main__':
    # For local development
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
