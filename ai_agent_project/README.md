# AI_AGENT_PROJECT

This project provides command-line interfaces for interacting with OpenAI and Google Gemini AI models. It includes both basic chat interfaces and an advanced interactive tool with weather information and knowledge base search capabilities.

## Project Structure

- **openai-basic.py**  
  A Python script for chatting with OpenAI's GPT models (e.g., GPT-3.5 Turbo).  
  - Prompts the user for input in a loop
  - Maintains conversation history
  - Streams the assistant's response character by character
  - Saves chat logs to `chat_log.txt`
  - Exits when the user types `exit` or `quit`

- **gemini-basic.py**  
  A basic Python script for chatting with Google's Gemini model.  
  - Prompts the user for input in a loop
  - Sends each query to Gemini and prints the response
  - Exits when the user types `exit` or `quit`

- **gemini-tools.py**
  Core implementation of the Gemini API with function calling capabilities.
  - Demonstrates function calling with Gemini API
  - Implements weather and knowledge base search functions
  - Shows how to structure function schemas for Gemini
  - Serves as the foundation for the interactive version

- **gemini-tools-interactive.py**
  An advanced interactive AI assistant based on gemini-tools.py.
  - Get weather information for any city worldwide
  - Search through a local knowledge base
  - Interactive menu-driven interface
  - Displays temperatures in both Celsius and Fahrenheit
  - Shows wind speed information
  - Handles multiple location matches

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ronicw/ai_agent_project.git
   cd ai_agent_project
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   python -m venv gemini_agent_env
   # On Windows:
   .\gemini_agent_env\Scripts\activate
   # On Unix or MacOS:
   source gemini_agent_env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Required packages:
   - openai
   - google-generativeai
   - python-dotenv
   - requests

4. **Set up environment variables:**
   Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Usage

### Function Calling Example
```bash
python gemini-tools.py
```
This demonstrates the basic implementation of function calling with the Gemini API. It shows how to:
- Define function schemas
- Handle function calls from Gemini
- Process weather and knowledge base queries
- Structure responses for the AI model

### Interactive Tools Interface
```bash
python gemini-tools-interactive.py
```
This enhanced version adds a user-friendly menu interface with the following options:
1. Check weather for a city
2. Search knowledge base
3. Exit

#### Checking Weather
- Enter a city name when prompted
- If multiple locations match, select the correct one
- View current temperature (in both °C and °F) and wind speed

#### Searching Knowledge Base
- Enter your search query
- Get results from the local knowledge base (data/knowledge_base.json)

### Basic Chat Interfaces

- **OpenAI Chat:**
  ```bash
  python openai-basic.py
  ```
- **Basic Gemini Chat:**
  ```bash
  python gemini-basic.py
  ```

For the basic chat interfaces:
- Type your questions at the prompt
- Type `exit` or `quit` to end the chat

## APIs Used

- **Google Gemini API**: For AI-powered interactions
- **OpenAI API**: For GPT model interactions
- **OpenStreetMap Nominatim API**: For geocoding city names
- **Open-Meteo API**: For weather data

## Notes

- Ensure your API keys are valid and have sufficient quota
- Chat logs for OpenAI are saved in `chat_log.txt`
- All scripts require an active internet connection
- The weather feature uses free public APIs with no key required
- Keep your API keys secure and never commit them to the repository

## License

This project is for educational purposes. See [LICENSE](LICENSE) for details.