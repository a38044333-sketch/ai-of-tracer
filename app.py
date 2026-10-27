from groq import Groq

# Initialize the Groq client
client = Groq(
    api_key="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"
)

# Send a chat completion request
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful and concise AI assistant."
        },
        {
            "role": "user",
            "content": "Hello! Introduce yourself briefly."
        }
    ],
    temperature=0.7,
    max_tokens=256
)

# Print the response text
print("Response from Groq:")
print(response.choices[0].message.content)
