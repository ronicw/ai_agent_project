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

def get_city_coordinates(city_name):
    """Get latitude and longitude for a city using Nominatim API."""
    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {
        'User-Agent': 'WeatherApp/1.0',  # Required by Nominatim's terms of service
        'Accept-Charset': 'utf-8'  # Explicitly request UTF-8 encoding
    }
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 5,  # Get up to 5 matching locations
        'accept-language': 'en'  # Request English results when available
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        locations = response.json()
        
        if not locations:
            return None, "No locations found for this city."
        
        if len(locations) == 1:
            # If only one location found, return it directly
            location = locations[0]
            return {
                'latitude': float(location['lat']),
                'longitude': float(location['lon']),
                'display_name': location['display_name']
            }, None
        
        # If multiple locations found, let user choose
        print("\nMultiple locations found:")
        for idx, loc in enumerate(locations, 1):
            print(f"{idx}. {loc['display_name']}")
        
        while True:
            try:
                choice = int(input("\nSelect a location (enter number): "))
                if 1 <= choice <= len(locations):
                    location = locations[choice - 1]
                    return {
                        'latitude': float(location['lat']),
                        'longitude': float(location['lon']),
                        'display_name': location['display_name']
                    }, None
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            
    except requests.RequestException as e:
        return None, f"Error fetching city coordinates: {str(e)}"

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32

def get_weather(latitude, longitude):
    """Invoke the publicly available API to return the weather for a given location."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    response = requests.get(url)
    current = response.json()["current"]
    
    # Create a new dictionary with formatted weather data
    weather_data = {}
    
    # Add Celsius and Fahrenheit temperatures
    if "temperature_2m" in current:
        celsius = current["temperature_2m"]
        fahrenheit = celsius_to_fahrenheit(celsius)
        weather_data["temperature_2m_celsius"] = round(celsius, 1)
        weather_data["temperature_2m_fahrenheit"] = round(fahrenheit, 1)
    
    # Add wind speed if available
    if "wind_speed_10m" in current:
        weather_data["wind_speed_10m"] = round(current["wind_speed_10m"], 1)
    # print(weather_data["temperature_2m_celsius"])
    # print(weather_data["temperature_2m_fahrenheit"])
    # print(weather_data["wind_speed_10m"])
    return weather_data

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
    """Call the appropriate function with given arguments."""
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

            # Format temperature display for weather results
            if function_call.name == "get_weather":
                try:
                    # Use eval to convert the string result to a dictionary
                    result_dict = eval(function_result)
                    
                    # Check if we have temperature data
                    if "temperature_2m_celsius" in result_dict and "temperature_2m_fahrenheit" in result_dict:
                        temp_c = result_dict["temperature_2m_celsius"]
                        temp_f = result_dict["temperature_2m_fahrenheit"]
                        formatted_result = f"Current temperature: {temp_c}°C ({temp_f}°F)"
                        
                        # Add wind speed if available
                        if "wind_speed_10m" in result_dict:
                            wind_speed = result_dict["wind_speed_10m"]
                            formatted_result += f"\nWind speed: {wind_speed} m/s"
                        
                        function_result = formatted_result
                except Exception as e:
                    function_result = f"Error formatting weather data: {str(e)}"

            # Append both the original response with function call and the function result
            contents.append({
                "role": "model",
                "parts": [{"function_call": {
                    "name": function_call.name,
                    "args": function_call.args
                }}]
            })
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

def process_weather_query(model, city):
    """Process a weather query for a given city."""
    location, error = get_city_coordinates(city)
    if error:
        return f"Error: {error}"
    
    print(f"\nUsing location: {location['display_name']}")
    weather_prompt = f"What is the weather like in {city} whose latitude is {location['latitude']} and longitude is {location['longitude']}?"
    contents = [{"role": "user", "parts": [{"text": weather_prompt}]}]
    
    return gen_final_response(model, contents)

def process_kb_query(model, query):
    """Process a knowledge base query."""
    contents = [{"role": "user", "parts": [{"text": query}]}]
    return gen_final_response(model, contents)

def main():
    # Initialize the model with tools
    tools = {
        "function_declarations": [get_weather_function, search_kb_function]
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools=[tools]
    )
    
    while True:
        print("\n=== AI Assistant ===")
        print("1. Check weather for a city")
        print("2. Search knowledge base")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            city = input("Enter city name: ")
            print("\nFetching weather information...")
            response = process_weather_query(model, city)
            print(f"\nResponse: {response}")
            
        elif choice == "2":
            query = input("Enter your question: ")
            print("\nSearching knowledge base...")
            response = process_kb_query(model, query)
            print(f"\nResponse: {response}")
            
        elif choice == "3":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
