import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Send a test message
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Say hello and tell me you're ready to help with movie recommendations!"}
    ]
)

print("✅ Claude API is working!")
print(f"Response: {message.content[0].text}")
