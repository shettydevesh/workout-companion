import json
from datetime import datetime
from constants import workout_prompt, nutrition_plan
import logging


logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self):
        self.prompts = {
            "workout_plan": {
                "v1": {
                    "created": "2025-03-01",
                    "description": "Initial workout plan prompt",
                    "template": workout_prompt
                },
                "current": "v1"  # Points to the version that should be used
            },
            "nutrition_plan": {
                "v1": {
                    "created": "2025-03-01",
                    "description": "Initial nutrition plan prompt",
                    "template": nutrition_plan
                },
                "current": "v1"  # Points to the version that should be used
            }
        }
    
    def get_prompt(self, prompt_name, version=None):
        """Get a specific prompt template by name and optionally version."""
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt '{prompt_name}' not found")
            
        # Use specified version or default to current
        version = version or self.prompts[prompt_name]["current"]
        
        if version not in self.prompts[prompt_name]:
            raise ValueError(f"Version '{version}' not found for prompt '{prompt_name}'")
            
        return self.prompts[prompt_name][version]["template"]
    
    def get_current_prompt(self, prompt_name):
        """Get the current version of a prompt template."""
        return self.get_prompt(prompt_name)
    
    def format_workout_prompt(self, exercise_data, user_data, custom_data = None):
        """Format the workout prompt with exercise data and user preferences."""
        prompt = self.get_current_prompt("workout_plan")
        
        # Replace placeholders in the template
        formatted_prompt = prompt.replace(
            "{exercise_data}", 
            json.dumps(exercise_data)
        ).replace(
            "{user_preferences}", 
            json.dumps(user_data)
        )
        if custom_data:
          for key, value in custom_data.items():
              placeholder = f"{{{key}}}"
              
              if isinstance(value, (int, float)):
                  str_value = str(value)
              elif isinstance(value, bool):
                  str_value = str(value).lower()
              elif isinstance(value, (list, dict)):
                  str_value = json.dumps(value)
              else:
                  str_value = str(value)
                  
              formatted_prompt = formatted_prompt.replace(placeholder, str_value)
        return formatted_prompt
    
    def format_nutrition_prompt(self, user_data, custom_data = None):
        """Format the nutrition prompt with user preferences."""
        prompt = self.get_current_prompt("nutrition_plan")
        
        # Replace placeholders in the template
        formatted_prompt = prompt.replace(
            "{user_preferences}", 
            json.dumps(user_data)
        )
        if custom_data:
          for key, value in custom_data.items():
              placeholder = f"{{{key}}}"
              
              if isinstance(value, (int, float)):
                  str_value = str(value)
              elif isinstance(value, bool):
                  str_value = str(value).lower()
              elif isinstance(value, (list, dict)):
                  str_value = json.dumps(value)
              else:
                  str_value = str(value)
                  
              formatted_prompt = formatted_prompt.replace(placeholder, str_value)
              
        return formatted_prompt
