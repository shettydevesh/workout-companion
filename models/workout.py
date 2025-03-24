"""
Workout model for generating personalized fitness plans.
Handles preparation of exercise data and coordinates with the AI service.
"""
import logging
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor
from config import PromptManager
from utils import FitnessCalculator

logger = logging.getLogger(__name__)

class WorkoutModel:
    """Model for generating personalized workout plans."""
    
    def __init__(self, weight, exercise_data=None):
        """
        Initialize the workout model.
        
        Args:
            weight (float): User's weight in kilograms
            exercise_data (DataFrame, optional): DataFrame of exercise data
        """
        self.weight = weight
        self.df = exercise_data
        
        if self.df is not None:
            # Calculate total calories burned for this user's weight
            self.df['total_calories_burned'] = self.df['calories_burned_per_kg'] * weight
            
        self.prompt_manager = PromptManager()
        self.calculator = FitnessCalculator()
        
    def prepare_user_preferences(self, height, weight, goal_weight, duration_weeks, 
                                location, diet_preference, time_constraint, age, 
                                gender, activity_level, food_type='Maharashtrian'):
        """
        Prepare user preferences for the AI service.
        
        Args:
            height (float): User's height in centimeters
            weight (float): User's current weight in kilograms
            goal_weight (float): User's target weight in kilograms
            duration_weeks (int): Target timeframe in weeks
            location (str): User's location
            diet_preference (str): User's dietary preference
            time_constraint (int): Available workout time in minutes
            age (int): User's age in years
            gender (str): User's gender
            activity_level (str): User's activity level
            food_type (str, optional): Preferred cuisine type
            
        Returns:
            dict: User preferences formatted for the AI service
        """
        # Calculate BMI
        bmi = self.calculator.calculate_bmi(weight, height)
        bmi_category = self.calculator.get_bmi_category(bmi)
        
        # Calculate calorie deficit
        calorie_data = self.calculator.calculate_weight_loss_calories(
            weight, goal_weight, duration_weeks
        )
        
        # Calculate BMR
        bmr = self.calculator.calculate_bmr(weight, height, age, gender)
        
        # Calculate TDEE
        tdee = self.calculator.calculate_tdee(bmr, activity_level)
        
        # Calculate target daily intake
        diet_portion = calorie_data["diet_portion_calories"]
        food_calories = tdee - diet_portion
        
        # Calculate macronutrient distribution based on activity level
        activity_multiplier = self.calculator.get_activity_multiplier(activity_level)
        
        if activity_multiplier <= 1.55:  # Low to moderate activity
            protein_pct = 0.3
            carbs_pct = 0.45
            fat_pct = 0.25
        else:  # High activity
            protein_pct = 0.3
            carbs_pct = 0.5
            fat_pct = 0.2
            
        amount_of_protein = round((food_calories * protein_pct) / 4, 2)  # 4 cal/g
        amount_of_carbs = round((food_calories * carbs_pct) / 4, 2)      # 4 cal/g
        amount_of_fat = round((food_calories * fat_pct) / 9, 2)          # 9 cal/g
        
        # Compile user preferences
        user_preferences = {
            'weight': weight,
            'height_cm': height,
            'time_constraint_in_mins': time_constraint,
            'BMI': bmi,
            'bmi_category': bmi_category,
            'dietary_type': diet_preference,
            'cusine_type': food_type, 
            'location': location,
            'goal_weight': goal_weight,
            'duration_weeks': duration_weeks,
            'age': age,
            'gender': gender,
            'activity_level': activity_level,
            'daily_maintenance_calories': tdee,
            'total_calories_to_burn': calorie_data["total_calories_to_burn"],
            'daily_calorie_deficit': calorie_data["daily_calorie_deficit"],
            'exercise_portion_calories': calorie_data["exercise_portion_calories"],
            'diet_portion_calories': calorie_data["diet_portion_calories"],
            'target_daily_intake': food_calories,
            'protein_target': amount_of_protein,
            'carbs_target': amount_of_carbs,
            'fat_target': amount_of_fat
        }
        
        logger.info(f"Prepared user preferences for workout plan")
        return user_preferences
    
    def generate_workout_plan(self, user_preferences, ai_service):
        """
        Generate only the workout portion of the plan.
        
        Args:
            user_preferences (dict): User preferences and information
            ai_service (AnthropicService): Service for AI interactions
            
        Returns:
            dict: Workout plan data or error information
        """
        try:
            if self.df is None:
                return {"error": "Exercise data not available"}
                
            # Prepare exercise data
            exercise_data = self.df.to_dict(orient='records')
            
            # Create cache key based on relevant preferences
            cache_data = {
                'weight': user_preferences['weight'],
                'height_cm': user_preferences['height_cm'],
                'BMI': user_preferences['BMI'],
                'goal_weight': user_preferences['goal_weight'],
                'duration_weeks': user_preferences['duration_weeks'],
                'time_constraint_in_mins': user_preferences['time_constraint_in_mins'],
                'activity_level': user_preferences['activity_level'],
                'exercise_portion_calories': user_preferences['exercise_portion_calories']
            }
            cache_key = f"workout_{hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()}"
            
            # Get workout-specific prompt
            system_message = self.prompt_manager.format_workout_prompt(
                exercise_data, user_preferences
            )
            
            # Create user message
            user_message = (
                "Please create a personalized WORKOUT PLAN ONLY based on these "
                f"user preferences. Focus exclusively on the exercise plan with a 5-day schedule. "
                "Do not include any nutrition or diet information."
            )
            
            # Log the request
            logger.info(f"Generating workout plan for user with BMI {user_preferences['BMI']}, " 
                       f"time constraint {user_preferences['time_constraint_in_mins']} minutes")
            
            # Get response from AI service
            response = ai_service.send_message(
                system_message=system_message,
                user_message=user_message,
            )        
            # Check for errors
            if not response.get("success", False):
                logger.error(f"Workout plan generation error: {response.get('error', 'Unknown error')}")
                return response
            
            logger.info("Successfully generated workout plan")
            return response
            
        except Exception as e:
            logger.error(f"Error generating workout plan: {e}", exc_info=True)
            return {"error": f"Error generating workout plan: {str(e)}"}
    
    def validate_workout_plan(self, plan_data, user_preferences):
        """
        Validate the workout plan against user constraints.
        
        Args:
            plan_data (dict): Generated workout plan
            user_preferences (dict): User preferences and constraints
            
        Returns:
            tuple: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check if required sections exist
        if "workout_plan" not in plan_data:
            issues.append("Workout plan section missing from response")
            return False, issues
            
        workout_plan = plan_data["workout_plan"]
        
        # Check if weekly plan exists
        if "weekly_plan" not in workout_plan:
            issues.append("Weekly plan missing from workout plan")
            return False, issues
            
        weekly_plan = workout_plan["weekly_plan"]
        
        # Validate time constraints
        time_constraint = user_preferences["time_constraint_in_mins"]
        max_allowed_time = time_constraint + 5  # 5 minute buffer
        
        for day, day_plan in weekly_plan.items():
            if "total_time" not in day_plan:
                issues.append(f"Total time missing for {day}")
                continue
                
            total_time = day_plan["total_time"]
            
            if total_time > max_allowed_time:
                issues.append(f"{day}'s workout exceeds time constraint: {total_time} mins > {max_allowed_time} mins")
        
        # Check if at least one workout is included for each day
        for day, day_plan in weekly_plan.items():
            if "workouts" not in day_plan or not day_plan["workouts"]:
                issues.append(f"No workouts specified for {day}")
        
        return len(issues) == 0, issues