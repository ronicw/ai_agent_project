# AI_AGENT_PROJECT

This project provides simple command-line chat interfaces for interacting with OpenAI and Google Gemini AI models. It is designed for easy experimentation and learning with generative AI APIs.

## Project Structure

- **openai-basic.py**  
  A Python script for chatting with OpenAI's GPT models (e.g., GPT-3.5 Turbo).  
  - Prompts the user for input in a loop.
  - Maintains conversation history.
  - Streams the assistant's response character by character.
  - Saves chat logs to `chat_log.txt`.
  - Exits when the user types `exit` or `quit`.

- **gemini-basic.py**  
  A Python script for chatting with Google's Gemini model.  
  - Prompts the user for input in a loop.
  - Sends each query to Gemini and prints the response.
  - Exits when the user types `exit` or `quit`.

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/AI_AGENT_PROJECT.git
   cd AI_AGENT_PROJECT
   ```

2. **Create and activate a Python virtual environment:**
   ```
   python -m venv gemini_agent_env
   source gemini_agent_env/Scripts/activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
   *(If `requirements.txt` is missing, install manually: `pip install openai google-generativeai python-dotenv`)*

4. **Set up environment variables:**
   - Create a `.env` file in the project root.
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

## Usage

- **OpenAI Chat:**
  ```
  python openai-basic.py
  ```
- **Gemini Chat:**
  ```
  python gemini-basic.py
  ```

Type your questions at the prompt.  
Type `exit` or `quit` to end the chat.

## Notes

- Make sure your API keys are valid and have sufficient quota.
- Chat logs for OpenAI are saved in `chat_log.txt`.
- Both scripts require an active internet connection.

## License

This project is for educational purposes. See [LICENSE](LICENSE) for details.