import requests
import speech_recognition as sr
import json
import time
import os
from logger import logger
from modules.tools import *
from modules.memory import Memory
import re

class Agent:
    def __init__(self, local=False, openrouter_api=None, input_method="voice", local_model_name="gemma3:latest", cloud_model_name="mistralai/mixtral-8x7b-instruct", http_referer="https://nesarpy.github.io/"):
        self.local = local
        self.openrouter_api = openrouter_api
        self.input_method = input_method
        self.local_model_name = local_model_name
        self.cloud_model_name = cloud_model_name
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.memory = Memory()  # Initialize session memory
        if self.local:
            self.headers = {
                "Content-Type": "application/json"
            }
        else:
            self.headers = {
                "Authorization": f"Bearer {self.openrouter_api}",
                "Content-Type": "application/json",
                "HTTP-Referer": http_referer,
                "X-Title": "AI Computer Agent"
            }
        
        # Command mappings - simplified set for workflow execution
        self.command_handlers = {
            "Volume": volume_control,
            "Type": type_text,
            "Shortcut": shortcut,
            "Play": play,
            "Website": Website
        }
    
    def extract_json(self, text):
        """Extract JSON content from text using 2-pointer method to find outermost curly brackets"""
        # First try to find code blocks
        match = re.search(r'```json(.*?)```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
        else:
            match = re.search(r'```(.*?)```', text, re.DOTALL)
            if match:
                text = match.group(1).strip()
        
        # Use 2-pointer method to find outermost curly brackets
        start = -1
        end = -1
        brace_count = 0
        found_start = False
        
        for i, char in enumerate(text):
            if char == '{':
                if not found_start:
                    start = i
                    found_start = True
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if found_start and brace_count == 0:
                    end = i
                    break
        
        # If we found valid JSON brackets, extract the content
        if start != -1 and end != -1 and start < end:
            return text[start:end + 1]
        
        # Fallback to original text if no valid JSON found
        return text.strip()
    
    def get_text_input(self) -> str:
        """Get text input from user"""
        try:
            text = input("Type your command: ").strip()
            if text:
                print(f"You typed: {text}")
                logger.info(f"You typed: {text}")
            return text
        except KeyboardInterrupt:
            return ""
        except Exception as e:
            logger.error(f"Error getting text input: {e}")
            return ""
    
    def listen_for_voice(self) -> str:
        """Listen for voice input and convert to text"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source)
                
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            logger.info(f"You said: {text}")
            return text
            
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            logger.error(f"Could not request results; {e}")
            return ""
    
    def send_to_ai(self, command: str) -> dict:
        """Send command to AI and get structured response"""
        try:
            # Add user message to memory
            self.memory.add_user_message(command)
            
            # Read system prompt from file
            with open('systemprompt.txt', 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
        except FileNotFoundError:
            print("systemprompt.txt not found")
            logger.warning("systemprompt.txt not found")

        if self.local:
            model = self.local_model_name
        else:
            model = self.cloud_model_name
        
        # Build messages with memory context
        messages = [
            {"role": "system", "content": system_prompt + "\n\n## Current Session State\n" + self.memory.get_state_summary()}
        ]
        messages.extend(self.memory.get_context_messages())
        messages.append({"role": "user", "content": f"User command: {command}"})
        
        data = {
            "model": model,
            "messages": messages
        }

        try:

            if self.local:
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    headers={"Content-Type": "application/json"},
                    json=data,
                    stream=False
                )
                response.raise_for_status()
                ai_response = response.json()
                content = ai_response['message']['content']
            else:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions", 
                    headers=self.headers, 
                    json=data,
                    timeout=30
                )

                response.raise_for_status()
                ai_response = response.json()
                content = ai_response['choices'][0]['message']['content']


            # Parse JSON response
            try:
                logger.debug(f"Raw response: {content}")
                extracted_content = self.extract_json(content)
                logger.debug(f"Extracted content: {extracted_content}")
                parsed_response = json.loads(extracted_content)
                return parsed_response
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from AI: {content}")
                logger.debug(f"Raw response: {content}")
                logger.debug(f"Extracted content: {extracted_content}")
                logger.exception(f"JSON decode error: {e}")
                return {"command": "Error", "parameters": "Invalid response format"}

        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"command": "Error", "parameters": "API request failed"}
    
    def execute_command(self, command_data: dict):
        """Execute a single command or a workflow with multiple steps."""
        # Prefer workflow array if present
        workflow = command_data.get("workflow")
        if isinstance(workflow, list) and len(workflow) > 0:
            for idx, step in enumerate(workflow):
                try:
                    command = (step.get("command") or "").strip()
                    parameters = step.get("parameters", "")
                    delay_secs = step.get("delay")
                    logger.info(f"Step {idx+1}/{len(workflow)}: {command} -> {parameters}")
                    handler = self.command_handlers.get(command)
                    if handler:
                        handler(parameters)
                    else:
                        logger.warning(f"Unknown command in workflow: {command}")
                except Exception as e:
                    logger.error(f"Error executing step {idx+1}: {e}")
                # Per-step delay: use provided delay if present, otherwise default to 10s
                try:
                    pause = float(delay_secs) if delay_secs is not None else 10.0
                except Exception:
                    pause = 10.0
                time.sleep(pause)
            return

        # Fallback: single command structure { command, parameters }
        command = (command_data.get("command") or "").strip()
        parameters = command_data.get("parameters", "")
        logger.info(f"Executing single command: {command} -> {parameters}")
        handler = self.command_handlers.get(command)
        if handler:
            try:
                handler(parameters)
            except Exception as e:
                logger.error(f"Error executing command '{command}': {e}")
        else:
            print(f"Unknown command: {command}")
            logger.warning(f"Unknown command: {command}")
    

    def run(self):
        """Main loop for the AI agent"""
        if self.input_method == "voice":
            print("AI Voice Control Agent Started!")
            print("Say 'exit' to quit")
        else:
            print("AI Text Control Agent Started!")
            print("Type 'exit' to quit")
        
        logger.info("="*50)
        logger.info(f"Agent started with {self.input_method} input method")
        print("-"*50)
        
        while True:
            # Get input based on selected method
            if self.input_method == "voice":
                input_text = self.listen_for_voice()
            else:
                input_text = self.get_text_input()
            
            if not input_text:
                continue
            
            # Check for exit command
            if "exit" in input_text.lower() or "quit" in input_text.lower():
                print("Goodbye!")
                logger.info("Exited")
                logger.info("="*50)
                break
            
            # Send to AI for processing
            command_data = self.send_to_ai(input_text)
            
            # Execute the command
            self.execute_command(command_data)
            
            # Add response to memory after execution
            self.memory.add_assistant_response(command_data)
            
            print("-" * 50)