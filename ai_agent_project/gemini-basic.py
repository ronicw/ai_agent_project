import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except KeyError:
    print("Error : GEMINI_API_KEY not found in environment variables.")
    exit()

client = genai.GenerativeModel("gemini-2.5-flash")

print("Chat with Gemini! Type 'exit' or 'quit' to end.\n")

while True:
    user_query = input("You: ")
    if user_query.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break
    try:
        response = client.generate_content(user_query)
        print("--- Gemini's Response ---")
        print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")