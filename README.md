# AI Agent

A powerful voice-controlled AI assistant that uses natural language processing to control your computer. Simply speak commands and watch as the AI executes them automatically.

## 🎯 Features

- **Voice Recognition**: Listen to voice commands using your microphone
- **AI Processing**: Uses OpenRouter to send a prompt to an AI to understand natural language
- **JSON Response Format**: AI responds with structured JSON containing command and parameters
- **Computer Control**: Execute various actions based on voice commands
- **Spotify Integration**: Open and play music/playlists automatically
- **Website Navigation**: Open specific websites with voice commands
- **Application Management**: Open and close applications using Windows+R commands
- **Web Search**: Perform web searches
- **Volume Control**: Control system volume
- **Screenshots**: Take screenshots
- **Todo List**: Open Google Calendar tasks

## 🚀 Supported Commands

### Music/Spotify
- "Open Spotify and play Mac DeMarco"
- "Play some jazz music"
- "Start Spotify playlist"

### Websites
- "Open YouTube"
- "Open Facebook"
- "Open Twitter"
- "Open Instagram"
- "Open Reddit"
- "Open GitHub"
- "Open Wikipedia"
- "Open Amazon"
- "Open Netflix"
- "Open Twitch"
- "Open LinkedIn"

### Applications
- "Open Notepad"
- "Open Calculator"
- "Open Chrome"
- "Open Discord"
- "Open Steam"
- "Open VS Code"
- "Open Excel"
- "Open Word"
- "Open PowerPoint"
- "Open Task Manager"
- "Open Control Panel"
- "Open Command Prompt"

### System Control
- "Turn volume up"
- "Mute the volume"
- "Take a screenshot"
- "Open todo list"

### Web Search
- "Search for weather today"
- "Google how to make pasta"

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
pip install requests python-dotenv SpeechRecognition PyAudio pyautogui Pillow
```

**Note**: If you encounter issues installing PyAudio on Windows, try:
```bash
pip install pipwin
pipwin install pyaudio
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 3. Configure Settings

Edit the configuration variables at the top of `main.py`:

```python
# Simple configuration - edit these as needed
PLAY_BUTTON_COORDS = (431, 543)  # First click position (for search results)
SECOND_CLICK_COORDS = (426, 599)  # Second click position (for play button)
```

### 4. Find Play Button Coordinates

To find the correct coordinates for the play button:

1. Open Spotify in your browser
2. Navigate to a song/playlist
3. Run this simple script to get coordinates:

```bash
python mouse_coordinates.py
```

4. Update `PLAY_BUTTON_COORDS` and `SECOND_CLICK_COORDS` in `main.py`

## 🎮 Usage

### Basic Usage

```bash
python main.py
```

The agent will start listening for voice commands. Say "exit" to quit.

### Example Voice Commands

1. **Music**: "Open Spotify and play some Mac DeMarco"
   - AI Response: `{"command": "Spotify", "parameters": "mac de marco"}`
   - Action: Opens browser, navigates to Spotify search, clicks play

2. **Website**: "Open YouTube"
   - AI Response: `{"command": "Website", "parameters": "https://www.youtube.com"}`
   - Action: Opens YouTube in default browser

3. **Application**: "Open Notepad"
   - AI Response: `{"command": "Open", "parameters": "notepad"}`
   - Action: Opens Notepad using Windows+R

4. **Web Search**: "Search for Python tutorials"
   - AI Response: `{"command": "Search", "parameters": "Python tutorials"}`
   - Action: Opens browser and searches Google

## 🔧 How It Works

1. **Voice Input**: The agent listens to your voice using your microphone
2. **AI Processing**: Sends the voice command to AI via OpenRouter
3. **JSON Response**: AI responds with structured JSON like `{"command": "Spotify", "parameters": "mac de marco"}`
4. **Command Execution**: The agent parses the JSON and executes the appropriate function

## 🎵 Spotify Integration

### Search-Based Playback
- Opens Spotify search for any artist, genre, or playlist name
- Automatically clicks to select and play the first search result
- No need to configure preset playlists - works with any music request

## 🌐 Website Navigation

The AI can open popular websites directly:
- YouTube, Facebook, Twitter, Instagram, Reddit
- GitHub, Wikipedia, Amazon, Netflix, Twitch
- LinkedIn, Stack Overflow

## 💻 Application Management

Uses Windows+R commands to open applications:
- **Basic**: Notepad, Calculator, Paint, WordPad
- **Browsers**: Chrome, Firefox, Brave, Edge
- **Media**: Spotify, Discord, Steam, VLC
- **Development**: VS Code, Notepad++, Sublime Text
- **Office**: Excel, Word, PowerPoint, Outlook
- **System**: Task Manager, Control Panel, Command Prompt

## ⚙️ Customization

### Adding New Commands

1. **Edit `systemprompt.txt`** to add new commands
2. **Add handler** in `modules/Agent.py` if needed
3. **Update command mappings** in the Agent class

## 📦 Dependencies

- `requests`: HTTP requests to AI API
- `python-dotenv`: Environment variable management
- `SpeechRecognition`: Voice recognition
- `PyAudio`: Audio input/output
- `pyautogui`: Screen automation and control
- `Pillow`: Image processing for screenshots
---

**Enjoy controlling your computer with just your voice! 🎤✨**
