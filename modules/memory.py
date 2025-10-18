import json
from typing import List, Dict, Any, Optional
from logger import logger

class Memory:
    """Session memory manager for conversation history and system state tracking."""
    
    def __init__(self, max_interactions: int = 10):
        """
        Initialize memory with conversation history and system state.
        
        Args:
            max_interactions: Maximum number of user-assistant exchanges to keep (default: 10)
        """
        self.max_interactions = max_interactions
        self.conversation_history: List[Dict[str, str]] = []
        self.system_state: Dict[str, Any] = {
            "brave_open": False,
            "cmd_open": False,
            "spotify_active": False,
            "open_tabs": [],
            "last_volume": None,
            "recent_websites": []
        }
        
    def add_user_message(self, command: str) -> None:
        """Add user command to conversation history."""
        self.conversation_history.append({
            "role": "user",
            "content": command
        })
        logger.debug(f"Added user message to memory: {command}")
        
    def add_assistant_response(self, response: Dict[str, Any]) -> None:
        """Add AI response to conversation history and extract state changes."""
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant", 
            "content": json.dumps(response)
        })
        
        # Extract state changes from workflow
        workflow = response.get("workflow", [])
        if workflow:
            self.extract_state_from_workflow(workflow)
            
        # Maintain sliding window
        self._maintain_sliding_window()
        
        logger.debug(f"Added assistant response to memory and updated state")
        
    def get_context_messages(self) -> List[Dict[str, str]]:
        """Return conversation history within the sliding window for API context."""
        return self.conversation_history.copy()
        
    def get_state_summary(self) -> str:
        """Return human-readable summary of current system state."""
        summary_parts = []
        
        if self.system_state["brave_open"]:
            summary_parts.append("Brave browser is currently open")
            
        if self.system_state["cmd_open"]:
            summary_parts.append("Command prompt (CMD) is currently open")
            
        if self.system_state["spotify_active"]:
            summary_parts.append("Spotify is currently active in browser")
            
        if self.system_state["open_tabs"]:
            tabs_str = ", ".join(self.system_state["open_tabs"])
            summary_parts.append(f"Open browser tabs: {tabs_str}")
            
        if self.system_state["last_volume"] is not None:
            summary_parts.append(f"System volume is set to {self.system_state['last_volume']}%")
            
        if self.system_state["recent_websites"]:
            recent_str = ", ".join(self.system_state["recent_websites"][-3:])  # Last 3 websites
            summary_parts.append(f"Recently visited: {recent_str}")
            
        if not summary_parts:
            return "No applications or browser tabs are currently open."
            
        return " | ".join(summary_parts)
        
    def extract_state_from_workflow(self, workflow: List[Dict[str, Any]]) -> None:
        """Parse workflow commands to update system state."""
        try:
            for step in workflow:
                command = step.get("command", "").strip()
                parameters = step.get("parameters", "")
                
                if command == "Shortcut" and parameters == "win":
                    # Windows key pressed - might be opening something
                    continue
                    
                elif command == "Type":
                    if parameters.lower() == "brave":
                        # Brave is being opened
                        self.system_state["brave_open"] = True
                        logger.debug("State updated: Brave browser opened")
                        
                    elif parameters.lower() == "cmd":
                        # CMD is being opened
                        self.system_state["cmd_open"] = True
                        logger.debug("State updated: CMD opened")
                        
                elif command == "Shortcut" and parameters == "enter":
                    # Enter pressed - confirm previous Type command
                    continue
                    
                elif command == "Website":
                    if isinstance(parameters, str) and parameters.startswith("https://"):
                        # Track opened website
                        self.system_state["open_tabs"].append(parameters)
                        self.system_state["recent_websites"].append(parameters)
                        
                        # Check if it's Spotify
                        if "spotify.com" in parameters.lower():
                            self.system_state["spotify_active"] = True
                            logger.debug("State updated: Spotify activated")
                            
                        logger.debug(f"State updated: Website opened - {parameters}")
                        
                elif command == "Volume":
                    if isinstance(parameters, (int, float)):
                        self.system_state["last_volume"] = int(parameters)
                        logger.debug(f"State updated: Volume set to {parameters}%")
                        
                elif command == "Type" and "taskkill" in str(parameters).lower():
                    # App is being closed
                    if "brave" in str(parameters).lower():
                        self.system_state["brave_open"] = False
                        self.system_state["open_tabs"] = []
                        self.system_state["spotify_active"] = False
                        logger.debug("State updated: Brave browser closed")
                        
                    elif "cmd" in str(parameters).lower():
                        self.system_state["cmd_open"] = False
                        logger.debug("State updated: CMD closed")
                        
        except Exception as e:
            logger.error(f"Error extracting state from workflow: {e}")
            
    def _maintain_sliding_window(self) -> None:
        """Keep only the last max_interactions user-assistant exchanges."""
        max_messages = self.max_interactions * 2  # user + assistant pairs
        
        if len(self.conversation_history) > max_messages:
            # Remove oldest messages
            messages_to_remove = len(self.conversation_history) - max_messages
            self.conversation_history = self.conversation_history[messages_to_remove:]
            logger.debug(f"Trimmed conversation history to last {self.max_interactions} interactions")
            
    def clear_memory(self) -> None:
        """Clear all conversation history and reset system state."""
        self.conversation_history = []
        self.system_state = {
            "brave_open": False,
            "cmd_open": False,
            "spotify_active": False,
            "open_tabs": [],
            "last_volume": None,
            "recent_websites": []
        }
        logger.info("Memory cleared")
        
    def get_memory_stats(self) -> Dict[str, Any]:
        """Return statistics about current memory usage."""
        return {
            "conversation_messages": len(self.conversation_history),
            "max_interactions": self.max_interactions,
            "system_state": self.system_state.copy()
        }
