# CloudNerve Chat Backend

Simple Flask API backend for the CloudNerve AI chat widget.

## Features

- Secure Azure OpenAI integration
- CORS enabled for frontend
- Environment variable configuration
- Health check endpoint
- Sales-focused AI agent

## Setup

### Local Development

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Add your Azure OpenAI API key to `.env`:
```
AZURE_API_KEY=your_actual_api_key_here
```

5. Run locally:
```bash
python app.py
```

Server runs on http://localhost:8000

### Deploy to Azure App Service

1. Create Azure App Service (Python 3.11)

2. Configure environment variables in Azure Portal:
   - Go to Configuration → Application settings
   - Add:
     - `AZURE_API_KEY` = your Azure OpenAI key
     - `AZURE_ENDPOINT` = https://zuse1-ai-foundry-t1-01.cognitiveservices.azure.com/
     - `DEPLOYMENT_NAME` = gpt-4.1
     - `API_VERSION` = 2024-12-01-preview

3. Deploy using Azure CLI:
```bash
az webapp up --name cloudnerve-chat-api --resource-group YourResourceGroup --runtime "PYTHON:3.11"
```

Or deploy from GitHub:
   - Go to Deployment Center
   - Connect to GitHub repository
   - Select branch and folder (backend/)
   - Azure will auto-deploy

## API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "CloudNerve Chat API"
}
```

### POST /chat
Send message and get AI response

**Request:**
```json
{
  "message": "What services do you offer?",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! Welcome to CloudNerve!"}
  ]
}
```

**Response:**
```json
{
  "response": "CloudNerve offers comprehensive IT solutions...",
  "status": "success"
}
```

## Frontend Integration

Update `chat-widget.js` to use this backend:

```javascript
const BACKEND_URL = 'https://your-app-name.azurewebsites.net';

async function callBackend(userMessage, conversationHistory = []) {
    const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: userMessage,
            history: conversationHistory
        })
    });
    const data = await response.json();
    return data.response;
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| AZURE_API_KEY | Azure OpenAI API key | Required |
| AZURE_ENDPOINT | Azure OpenAI endpoint URL | https://zuse1-ai-foundry-t1-01... |
| DEPLOYMENT_NAME | Model deployment name | gpt-4.1 |
| API_VERSION | Azure OpenAI API version | 2024-12-01-preview |
| MAX_TOKENS | Maximum response tokens | 500 |
| TEMPERATURE | Response creativity (0-1) | 0.7 |
| PORT | Server port | 8000 |

## Security

- API key stored in environment variables (never in code)
- CORS configured for your frontend domain
- Request timeout set to 30 seconds
- Proper error handling and logging

## License

Proprietary - CloudNerve 2024
