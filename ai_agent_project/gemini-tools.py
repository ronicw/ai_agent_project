import os
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Configure the API key from environment variables
load_dotenv()
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit()

# Define tools as functions
def get_weather(latitude, longitude):
    """Invoke the publicly available API to return the weather for a given location."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)
    return response.json()["current"]

def search_kb(query):
    """Search the knowledge base for information about the given query."""
    try:
        kb_path = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json")
        with open(kb_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return "Error: Knowledge base file not found"
    except json.JSONDecodeError:
        return "Error: Invalid JSON in knowledge base file"
    except Exception as e:
        return f"Error: {str(e)}"

def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)
    elif name == "search_kb":
        return search_kb(**args)
    else:
        raise ValueError(f"Function {name} not found")

# Define the function schemas for tools
get_weather_function = {
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
        },
        "required": ["latitude", "longitude"],
    },
}

search_kb_function = {
    "name": "search_kb",
    "description": "Search the knowledge base for information about the given query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
        },
        "required": ["query"],
    },
}

def gen_final_response(model, contents):
    """Generate a response and handle any function calls with context memory."""
    generation_config = {
        "temperature": 0.9,
        "candidate_count": 1,
        "max_output_tokens": 2048,
    }
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    try:
        response = model.generate_content(
            contents,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        if hasattr(response.candidates[0].content.parts[0], 'function_call'):
            function_call = response.candidates[0].content.parts[0].function_call
            result = call_function(function_call.name, function_call.args)

            # Create function response part
            function_result = str(result)

            # Append both the original response with function call and the function result
            contents.append({
                "role": "model",
                "parts": [{"function_call": {
                    "name": function_call.name,
                    "args": function_call.args
                }}]
            })

            # Append the function result as a user message
            contents.append({
                "role": "user",
                "parts": [{"text": f"Function {function_call.name} returned: {function_result}"}]
            })

            # Make second call with full context
            final_response = model.generate_content(
                contents,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            return final_response.text
        else:
            return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    # Initialize the model with tools
    tools = {
        "function_declarations": [get_weather_function, search_kb_function]
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools=[tools]
    )
    
    # Test weather query with specific coordinates
    city = "Hyderabad"
    latitude = 17.3850
    longitude = 78.4867
    weather_prompt = f"What is the weather like in {city} whose latitude is {latitude} and longitude is {longitude}?"
    contents = [{"role": "user", "parts": [{"text": weather_prompt}]}]
    
    print("\nWeather Query:")
    print(f"Prompt: {weather_prompt}")
    print(f"Response: {gen_final_response(model, contents)}")
    
    # Test knowledge base query
    kb_prompt = "Will Fanniemae aquire an ARM loan?"
    contents = [{"role": "user", "parts": [{"text": kb_prompt}]}]
    
    print("\nKnowledge Base Query:")
    print(f"Prompt: {kb_prompt}")
    print(f"Response: {gen_final_response(model, contents)}")

if __name__ == "__main__":
    main()
