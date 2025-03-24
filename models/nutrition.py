import logging
import json
import hashlib
from config import PromptManager

logger = logging.getLogger(__name__)

class NutritionModel:
    """Model for generating personalized nutrition plans."""
    
    def __init__(self):
        """Initialize the nutrition model."""
        self.prompt_manager = PromptManager()
        
        # Standard calorie values per gram
        self.calories_per_gram = {
            "protein": 4,
            "carbs": 4,
            "fat": 9
        }
        
        # Meal distribution percentages (default)
        self.meal_distribution = {
            "Breakfast": 0.25,
            "Morning_Snack": 0.10,
            "Lunch": 0.30,
            "Evening_Snack": 0.10,
            "Dinner": 0.25
        }
        
    def calculate_macro_targets(self, daily_calories, activity_level):
        """
        Calculate macronutrient targets based on daily calories and activity level.
        
        Args:
            daily_calories (float): Total daily calorie target
            activity_level (str): Activity level descriptor
            
        Returns:
            dict: Macronutrient targets in grams
        """
        # Determine macronutrient percentages based on activity level
        if activity_level.lower() in ["sedentary", "lightly active", "moderately active"]:
            protein_pct = 0.30
            carbs_pct = 0.45
            fat_pct = 0.25
        else:
            protein_pct = 0.30
            carbs_pct = 0.50
            fat_pct = 0.20
            
        # Calculate grams for each macronutrient
        protein_calories = daily_calories * protein_pct
        carbs_calories = daily_calories * carbs_pct
        fat_calories = daily_calories * fat_pct
        
        protein_grams = round(protein_calories / self.calories_per_gram["protein"], 1)
        carbs_grams = round(carbs_calories / self.calories_per_gram["carbs"], 1)
        fat_grams = round(fat_calories / self.calories_per_gram["fat"], 1)
        
        return {
            "protein": protein_grams,
            "carbs": carbs_grams,
            "fat": fat_grams,
            "protein_pct": round(protein_pct * 100),
            "carbs_pct": round(carbs_pct * 100),
            "fat_pct": round(fat_pct * 100)
        }
        
    def calculate_meal_calories(self, daily_calories):
        """
        Calculate calorie allocation for each meal.
        
        Args:
            daily_calories (float): Total daily calorie target
            
        Returns:
            dict: Calorie targets for each meal
        """
        meal_calories = {}
        for meal, percentage in self.meal_distribution.items():
            meal_calories[meal] = round(daily_calories * percentage)
            
        return meal_calories
    
    def generate_nutrition_plan(self, user_preferences, ai_service):
        try:
            # Create cache key based on relevant preferences
            cache_data = {
                'weight': user_preferences['weight'],
                'goal_weight': user_preferences['goal_weight'],
                'dietary_type': user_preferences['dietary_type'],
                'cusine_type': user_preferences['cusine_type'],
                'location': user_preferences['location'],
                'target_daily_intake': user_preferences['target_daily_intake'],
                'protein_target': user_preferences['protein_target'],
                'carbs_target': user_preferences['carbs_target'],
                'fat_target': user_preferences['fat_target']
            }
            cache_key = f"nutrition_{hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()}"
            
            # Calculate macro distribution
            macros = self.calculate_macro_targets(
                user_preferences['target_daily_intake'],
                user_preferences['activity_level']
            )
            
            # Calculate meal distribution
            meal_calories = self.calculate_meal_calories(
                user_preferences['target_daily_intake']
            )
            
            # Add calculated values to user preferences
            user_preferences['macro_targets'] = macros
            user_preferences['meal_calories'] = meal_calories
            
            # Get nutrition-specific prompt
            system_message = self.prompt_manager.format_nutrition_prompt(
                user_preferences
            )
            
            # Create user message
            user_message = (
                "Please create a personalized NUTRITION PLAN ONLY based on these "
                f"user preferences. Focus exclusively on meal planning and macronutrient distribution. "
                "Do not include any workout or exercise information."
            )
            
            # Log the request
            logger.info(f"Generating nutrition plan for user with diet preference {user_preferences['dietary_type']}, " 
                       f"cuisine type {user_preferences['cusine_type']}, target calories {user_preferences['target_daily_intake']}")
            
            # Get response from AI service
            response = ai_service.send_message(
                system_message=system_message,
                user_message=user_message,
            )
            
            # Check for errors
            if not response.get("success", False):
                logger.error(f"Nutrition plan generation error: {response.get('error', 'Unknown error')}")
                return response
                
            logger.info("Successfully generated nutrition plan")
            return response
            
        except Exception as e:
            logger.error(f"Error generating nutrition plan: {e}", exc_info=True)
            return {"error": f"Error generating nutrition plan: {str(e)}"}
            
    def validate_nutrition_plan(self, plan_data, user_preferences):
        """
        Validate the nutrition plan against user preferences and nutritional guidelines.
        
        Args:
            plan_data (dict): Generated nutrition plan
            user_preferences (dict): User preferences and constraints
            
        Returns:
            tuple: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check if required sections exist
        if "nutrition_plan" not in plan_data:
            issues.append("Nutrition plan section missing from response")
            return False, issues
            
        nutrition_plan = plan_data["nutrition_plan"]
        
        # Check if meals exist
        if "meals" not in nutrition_plan:
            issues.append("Meals missing from nutrition plan")
            return False, issues
            
        meals = nutrition_plan["meals"]
        
        # Check if all expected meals are present
        expected_meals = ["Breakfast", "Morning_Snack", "Lunch", "Evening_Snack", "Dinner"]
        for meal in expected_meals:
            if meal not in meals:
                issues.append(f"Missing meal: {meal}")
        
        # Validate dietary preferences
        diet_preference = user_preferences["dietary_type"]
        if "diet_preference" in nutrition_plan and nutrition_plan["diet_preference"] != diet_preference:
            issues.append(f"Diet preference mismatch: expected {diet_preference}, got {nutrition_plan['diet_preference']}")
        
        # Check if total calories are within 10% of target
        if "daily_calories" in nutrition_plan:
            target_calories = user_preferences["target_daily_intake"]
            actual_calories = nutrition_plan["daily_calories"]
            
            deviation_pct = abs(target_calories - actual_calories) / target_calories * 100
            if deviation_pct > 10:
                issues.append(f"Total calories deviate too much from target: {actual_calories} vs {target_calories} ({deviation_pct:.1f}% difference)")
        
        # Validate macronutrient distribution if present
        if "macros" in nutrition_plan:
            macros = nutrition_plan["macros"]
            
            # Check if protein is within 5g of target
            if "protein" in macros:
                protein_target = user_preferences["protein_target"]
                protein_actual = macros["protein"]
                
                if abs(protein_target - protein_actual) > 5:
                    issues.append(f"Protein deviates too much from target: {protein_actual}g vs {protein_target}g")
        
        return len(issues) == 0, issues
        
    def combine_plans(self, workout_plan, nutrition_plan):
        """
        Combine workout and nutrition plans into a unified plan.
        
        Args:
            workout_plan (dict): Generated workout plan
            nutrition_plan (dict): Generated nutrition plan
            
        Returns:
            dict: Combined plan
        """
        # Extract key components from each plan
        combined_plan = {}
        
        # Copy user profile and calculations from workout plan
        if "user_profile" in workout_plan:
            combined_plan["user_profile"] = workout_plan["user_profile"]
            
        if "weight_loss_calculation" in workout_plan:
            combined_plan["weight_loss_calculation"] = workout_plan["weight_loss_calculation"]
            
        if "daily_calorie_intake" in workout_plan:
            combined_plan["daily_calorie_intake"] = workout_plan["daily_calorie_intake"]
            
        # Copy workout plan
        if "workout_plan" in workout_plan:
            combined_plan["workout_plan"] = workout_plan["workout_plan"]
            
        # Copy nutrition plan
        if "nutrition_plan" in nutrition_plan:
            combined_plan["nutrition_plan"] = nutrition_plan["nutrition_plan"]
            
        combined_plan["success"] = True
        
        return combined_plan