from anthropic import Anthropic
from models import ChatMessage
import os

# Pricing constants
INPUT_TOKEN_COST = 0.000003
OUTPUT_TOKEN_COST = 0.000015
ESTIMATED_SYSTEM_TOKENS = 3875
MAX_OUTPUT_TOKENS = 300

def estimate_message_cost(member_id, user_message):
    """
    Estimate cost before sending message to Claude
    
    Returns:
        float: Estimated cost in USD
    """
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    # Get active chat history
    history = ChatMessage.query\
        .filter_by(member_id=member_id, active=True)\
        .order_by(ChatMessage.created_at.asc())\
        .all()
    
    # Build messages for token counting
    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": user_message})
    
    # Count tokens using the beta method
    history_tokens = client.beta.messages.count_tokens(
        model="claude-sonnet-4-20250514",
        messages=messages
    ).input_tokens
    
    total_input_tokens = ESTIMATED_SYSTEM_TOKENS + history_tokens
    
    # Calculate cost
    input_cost = total_input_tokens * INPUT_TOKEN_COST
    output_cost = MAX_OUTPUT_TOKENS * OUTPUT_TOKEN_COST
    
    return input_cost + output_cost