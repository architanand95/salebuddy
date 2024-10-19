# backend/app.py

import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from transformers import GPT2Tokenizer

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI API
openai.api_key = "your_openai_api_key"
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        conversation_log = []  # Maintain a conversation log for analysis
        while True:
            data = await websocket.receive_text()
            conversation_log.append(data)  # Add message to conversation log
            # Process received message
            response_data = await process_message(data, conversation_log)
            await manager.broadcast(response_data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def process_message(message: str, conversation_log: list):
    # Call GPT-4 API to analyze message and determine sentiment
    sentiment, response_text = await analyze_sentiment(message)
    
    # Track token usage
    token_count = len(tokenizer.tokenize(message))
    
    # Calculate metrics based on conversation log
    lead_interest = determine_lead_interest(sentiment)
    conversion_likelihood = calculate_conversion_likelihood(conversation_log, token_count, sentiment)
    
    metrics = {
        "lead_interest": lead_interest,
        "engagement_level": min(100, token_count),  # Engagement depends on token count
        "conversion_likelihood": conversion_likelihood
    }
    
    return f"GPT-4 Response: {response_text}\nMetrics: {metrics}"

async def analyze_sentiment(message: str):
    """
    Uses GPT-4 to analyze the sentiment of the conversation message.
    Returns the sentiment as positive, negative, or neutral.
    """
    response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Analyze the sentiment of the following text:\n{message}",
        max_tokens=50,
        temperature=0.5
    )
    
    # Extract the sentiment from GPT-4's response (you can tailor the prompt to fit the output)
    response_text = response.choices[0].text.strip()
    if "positive" in response_text:
        sentiment = "positive"
    elif "negative" in response_text:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return sentiment, response_text

def determine_lead_interest(sentiment: str):
    """
    Determines lead interest based on sentiment.
    Positive sentiment means positive lead interest, negative sentiment means negative lead interest.
    """
    if sentiment == "positive":
        return "positive"
    else:
        return "negative"

def calculate_conversion_likelihood(conversation_log: list, token_count: int, sentiment: str):
    """
    Calculate conversion likelihood based on conversation sentiment and token count.
    Sentiment is a stronger factor in determining the likelihood of conversion.
    """
    positive_message_count = sum(1 for message in conversation_log if "positive" in message)
    
    # Adjust conversion likelihood based on sentiment strength
    if sentiment == "positive":
        likelihood = min((positive_message_count / len(conversation_log)) * 90, 90)
    elif sentiment == "negative":
        likelihood = max(10, (positive_message_count / len(conversation_log)) * 40)
    else:
        likelihood = max(20, (positive_message_count / len(conversation_log)) * 60)

    return likelihood
