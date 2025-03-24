from constant import system_message_template
import pandas as pd
import numpy as np
import re
import json
import anthropic
from dotenv import load_dotenv
import os
import streamlit as st

class WorkoutCompanion:
    def __init__(self, weight, df=None):
        self.df = df
        if self.df is not None:
            self.df['total_calories_burned'] = self.df['calories_burned_per_kg'] * weight
        
        self.client = None
        api_key = os.getenv('ANTHROPIC_KEY')
        if api_key:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                st.error(f"Error initializing Anthropic client: {e}")
        
        self.pal_score = {
            'sedentary': 1.2,
            'lightly active': 1.375,
            'moderately active': 1.55,
            'very active': 1.725,
            'extra active': 1.9
        }
    
    def bmr_calculator(self, weight, height_cm, age, gender, activity_level='sedentary'):
        # Harris-Benedict formula
        if gender.lower() == 'male':
            bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) - 161
        
        return bmr * self.pal_score.get(activity_level.lower(), 1.2)
    
    def calculate_bmi(self, weight, height_cm):
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 2)

    def get_system_message(self, user_preferences):
        # Format DataFrame as a clean JSON string for the system message
        exercise_data = self.df.to_dict(orient='records')
        
        system_message = system_message_template.replace("{exercise_data}", json.dumps(exercise_data))
        system_message = system_message.replace("{user}", json.dumps(user_preferences))
        return system_message

    def recommend_exercises(self, height, weight, goal, duration, location, preference, time_constraint, age, gender, activity_level, food_type = 'Maharashtrian'):
        if not self.client:
            return {"error": "Anthropic API key not provided or invalid"}
        total_calories_to_burn = (weight - goal) * 7700
        daily_calorie_deficit = total_calories_to_burn / (duration * 7)
        exercise_portion_calories = ((total_calories_to_burn * 0.3) / 7) / 5
        diet_portion_calories = daily_calorie_deficit - exercise_portion_calories
        bmr = self.bmr_calculator(weight, height, age, gender, activity_level)
        food_calories = bmr - diet_portion_calories
        amount_of_protein = round((food_calories * 0.3 ) / 4, 2)
        amount_of_carbs = round((food_calories * 0.5 ) / 4, 2)
        amount_of_fat = round((food_calories * 0.2 ) / 9, 2)
        user_preferences = {
            'weight': weight,
            'height_cm': height,
            'time_constraint_in_mins': time_constraint,
            'BMI': self.calculate_bmi(weight, height),
            'dietary_type': preference,
            'cusine_type': food_type, 
            'location': location,
            'goal_weight': goal,
            'duration_weeks': duration,
            'age': age,
            'gender': gender,
            'activity_level': activity_level,
            'daily_maintenance_calories': bmr,
            'total_calories_to_burn': total_calories_to_burn,
            'daily_calorie_deficit': daily_calorie_deficit,
            'exercise_portion_calories': exercise_portion_calories,
            'diet_portion_calories': diet_portion_calories,
            'amount_of_protein': amount_of_protein,
            'amount_of_carbs': amount_of_carbs,
            'amount_of_fat': amount_of_fat
        }
        print(user_preferences)
        system_message = self.get_system_message(user_preferences)
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                temperature=0,
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please create a personalized fitness and nutrition plan based on these user preferences: {json.dumps(user_preferences)}"
                    },
                ])
            
            message = response.content[0].text
            print("Response from Anthropic API:", message)
            cost = (
            (response.usage.input_tokens / 1_000_000) * 0.80 +
            (response.usage.output_tokens / 1_000_000) * 4
            ) * 86.93
            print('Cost: Rs', cost)
            # Attempt to parse the JSON response
            try:
                # Clean the response to ensure it's valid JSON
                # This handles cases where there might be markdown formatting or other text
                json_pattern = re.compile(r'<output>([\s\S]*?)<\/output>', re.DOTALL)
                matches = json_pattern.findall(message)
                
                if matches:
                    # Use the first JSON block found
                    clean_json = matches[0]
                else:
                    # If no JSON blocks in markdown, try to clean the entire text
                    clean_json = message.strip()
                    # Remove any markdown or text before JSON opening brace
                    if '{' in clean_json:
                        clean_json = clean_json[clean_json.find('{'):]
                    # Remove any text after the JSON closing brace
                    if '}' in clean_json:
                        clean_json = clean_json[:clean_json.rfind('}')+1]
                
                plan_data = json.loads(clean_json)  
                return plan_data
            except json.JSONDecodeError as e:
                st.error(f"Error parsing JSON response: {e}")
                st.text("Raw response:")
                st.text(message)
                return {"error": f"Failed to parse JSON response: {e}", "raw_response": message}
                
        except Exception as e:
            return {"error": f"Error calling Anthropic API: {e}"}
