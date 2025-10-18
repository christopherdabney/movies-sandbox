from anthropic import Anthropic
from models import ChatMessage
from config import Config
import os

# Pricing constants (per token)
INPUT_TOKEN_COST = 0.000003  # $3 per million
OUTPUT_TOKEN_COST = 0.000015  # $15 per million
MAX_OUTPUT_TOKENS = 300  # from ClaudeClient

def estimate_message_cost(member_id, user_message):
    """
    Estimate the cost of sending a message to Claude
    
    Args:
        member_id: Member's ID
        user_message: The user's message text
        
    Returns:
        float: Estimated cost in USD
    """
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    # Build the messages array (same as RS does)
    chat_history = ChatMessage.query\
        .filter_by(member_id=member_id, active=True)\
        .order_by(ChatMessage.created_at.asc())\
        .all()
    
    messages = []
    for msg in chat_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})
    
    # Count input tokens (would need system context too, but approximating)
    # For accurate count, you'd need to pass the full system context
    # For now, estimate: ~3875 tokens for system + message history
    input_tokens = 3875 + client.count_tokens(str(messages))
    
    # Estimate cost
    input_cost = input_tokens * INPUT_TOKEN_COST
    output_cost = MAX_OUTPUT_TOKENS * OUTPUT_TOKEN_COST
    
    return input_cost + output_cost