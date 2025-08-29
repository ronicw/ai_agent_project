import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from openai import RateLimitError, AuthenticationError
from dotenv import load_dotenv
from datetime import datetime
import time
import sys

def stream_text(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Newline after streaming


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


load_dotenv()
# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Conversation history
messages: list[ChatCompletionMessage] = [
    {"role": "system", "content": "You are a witty and insightful assistant who loves helping people learn and explore ideas. Keep the tone friendly, clever, and curious."}
]

print("Chat with your AI assistant! Type 'exit' to quit.\n")  # ▶ symbol


while True:
    try:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Add user message to history
        timestamp = get_timestamp()
        messages.append({"role": "user", "content": user_input, "timestamp": timestamp})

        # Call the model; Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Extract and print assistant reply
        reply = response.choices[0].message.content
        with open("chat_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] You: {user_input}\n")
            f.write(f"[{timestamp}] Assistant: {reply}\n\n")

        stream_text(f"Assistant: {reply}")


        # Save assistant reply to history
        messages.append({"role": "assistant", "content": reply})

    except RateLimitError:
        print("You're sending requests too quickly. Try again in a moment.\n")
    except AuthenticationError:
        print("Missing or invalid API key. Please check your environment settings.\n")
    except Exception as e:
        print(f"An unexpected error occurred: {e}\n")
