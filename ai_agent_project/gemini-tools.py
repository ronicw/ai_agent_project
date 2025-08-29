import os
import requests
import json
from dotenv import load_dotenv
# import google.generativeai as genai
# from google.generativeai import types
from google import genai
from google.genai import types

# Configure the API key from environment variables
load_dotenv()
try:
    # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error : GEMINI_API_KEY not found in environment variables.")
    exit()

# Define tools as functions
def get_weather(latitude, longitude):
    """Invoke the publicly available API to return the weather for a given location."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)
    return response.json()["current"]

def search_kb(query):
    """Search the knowledge base for information about the given query."""
    with open("knowledge_base.json", "r") as f:
        return json.load(f)

def call_function(name ,args):
    if name == "get_weather":
        return get_weather(**args)
    elif name == "search_kb":
        return search_kb(**args)
    else:
        raise ValueError(f"Function {name} not found")
    
def run_model(model_name, contents, config):    
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=config
    )
    return response

def gen_final_response(model_name, contents, config):
    response = run_model(model_name, contents, config)
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        result = call_function(function_call.name, function_call.args)

        function_response_part = types.Part.from_function_response(
            name=function_call.name,
            response={"result": result},
        )

        contents.append(response.candidates[0].content)
        contents.append(types.Content(role="user", parts=[function_response_part]))

        final_response = run_model(model_name, contents, config)
        return final_response.text
    else:
        return response.text


# Set the tools
get_weather_function =  {
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

tools = types.Tool(function_declarations=[get_weather_function, search_kb_function])
config = types.GenerateContentConfig(
# config = types.GenerationConfig(
    tools=[tools],
    system_instruction="You are a helpful assistant who can answer questions about the current weather in a city by invoking the right tools and about policies by looking up a knowledge base"
)

# Define user prompt
prompt = f"What is the weather like in Paris?"
contents = [
    types.Content(
        role="user", parts=[types.Part(text=prompt)]
    )
]

model_name = "gemini-2.5-flash"
# model = genai.GenerativeModel(
#     model_name="gemini-2.5-flash",
#     tools=[tools]
# )
try:
    final_response = gen_final_response(model_name, contents, config)
    print(final_response)
except Exception as e:
    print(f"An error occurred: {e}")      

prompt = f"Will Fanniemae aquire an ARM loan?"
contents = [
    types.Content(
        role="user", parts=[types.Part(text=prompt)]
    )
]

try:
    final_response = gen_final_response(model_name, contents, config)
    print(final_response)
except Exception as e:
    print(f"An error occurred: {e}")      