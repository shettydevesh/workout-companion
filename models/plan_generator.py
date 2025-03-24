import logging
from concurrent.futures import ThreadPoolExecutor
from models import WorkoutModel, NutritionModel
from utils import FitnessCalculator

logger = logging.getLogger(__name__)

class PlanGenerator:
    def __init__(self, exercise_data=None):
        self.exercise_data = exercise_data
        self.nutrition_model = NutritionModel()
        self.calculator = FitnessCalculator()
    
    def generate_plan(self, user_info, ai_service):
        """
        Generate a complete fitness plan with parallel API calls.
        
        Args:
            user_info (dict): User information and preferences
            ai_service (AnthropicService): Service for AI interactions
            
        Returns:
            dict: Complete fitness plan
        """
        try:
            # Initialize workout model with user's weight
            workout_model = WorkoutModel(
                weight=user_info["weight"],
                exercise_data=self.exercise_data
            )
            
            # Prepare user preferences
            user_preferences = workout_model.prepare_user_preferences(
                height=user_info["height_cm"],
                weight=user_info["weight"],
                goal_weight=user_info["goal_weight"],
                duration_weeks=user_info["time_frame"],
                location=user_info["location"],
                diet_preference=user_info["diet_preference"],
                time_constraint=user_info["time_constraint"],
                age=user_info["age"],
                gender=user_info["gender"],
                activity_level=user_info["activity_level"],
                food_type=user_info["food_type"]
            )
            # Use ThreadPoolExecutor for parallel API calls
            with ThreadPoolExecutor(max_workers=2) as executor:
                # Submit both API calls in parallel
                workout_future = executor.submit(
                    workout_model.generate_workout_plan,
                    user_preferences,
                    ai_service
                )
                
                nutrition_future = executor.submit(
                    self.nutrition_model.generate_nutrition_plan,
                    user_preferences,
                    ai_service
                )
                
                # Wait for both to complete
                workout_plan = workout_future.result()
                nutrition_plan = nutrition_future.result()
            
            # Check for errors
            if "error" in workout_plan:
                logger.error(f"Failed to generate workout plan: {workout_plan['error']}")
                return workout_plan
                
            if "error" in nutrition_plan:
                logger.error(f"Failed to generate nutrition plan: {nutrition_plan['error']}")
                return nutrition_plan
                
            # Combine plans
            combined_plan = self.nutrition_model.combine_plans(workout_plan, nutrition_plan)
            logger.info("Successfully generated complete fitness plan using parallel processing")
            combined_plan['weight_loss_calculation'] = {
                    'total_calories_to_burn': user_preferences.get('total_calories_to_burn'),
                    'daily_calorie_deficit': user_preferences.get('daily_calorie_deficit'),
                    'exercise_portion_calories': user_preferences.get('exercise_portion_calories'),
                    'diet_portion_calories': user_preferences.get('diet_portion_calories'),
                }
            combined_plan['daily_calorie_intake'] = {
                'baseline_calories': user_preferences.get('daily_maintenance_calories'),
                'diet_calorie_deficit': user_preferences.get('diet_portion_calories'),
                'target_daily_intake': user_preferences.get('target_daily_intake'),
            }
            return combined_plan
            
        except Exception as e:
            logger.error(f"Error generating plan: {e}", exc_info=True)
            return {"error": f"Failed to generate fitness plan: {str(e)}"}
    
    def regenerate_workout_plan(self, user_info, current_plan, ai_service):
        """
        Regenerate only the workout portion of an existing plan.
        
        Args:
            user_info (dict): User information and preferences
            current_plan (dict): Current complete plan
            ai_service (AnthropicService): Service for AI interactions
            
        Returns:
            dict: Updated complete plan
        """
        try:
            # Initialize workout model with user's weight
            workout_model = WorkoutModel(
                weight=user_info["weight"],
                exercise_data=self.exercise_data
            )
            
            # Prepare user preferences
            user_preferences = workout_model.prepare_user_preferences(
                height=user_info["height_cm"],
                weight=user_info["weight"],
                goal_weight=user_info["goal_weight"],
                duration_weeks=user_info["time_frame"],
                location=user_info["location"],
                diet_preference=user_info["diet_preference"],
                time_constraint=user_info["time_constraint"],
                age=user_info["age"],
                gender=user_info["gender"],
                activity_level=user_info["activity_level"],
                food_type=user_info["food_type"]
            )
            
            # Generate workout plan
            logger.info("Regenerating workout plan...")
            workout_plan = workout_model.generate_workout_plan(user_preferences, ai_service)
            
            # Check for errors in workout plan
            if "error" in workout_plan:
                logger.error(f"Failed to regenerate workout plan: {workout_plan['error']}")
                return workout_plan
                
            # Create updated plan (keep existing nutrition plan)
            updated_plan = self.nutrition_model.combine_plans(
                workout_plan,
                {"nutrition_plan": current_plan.get("nutrition_plan", {})}
            )
            
            logger.info("Successfully regenerated workout plan")
            return updated_plan
            
        except Exception as e:
            logger.error(f"Error regenerating workout plan: {e}", exc_info=True)
            return {"error": f"Failed to regenerate workout plan: {str(e)}"}
    
    def regenerate_nutrition_plan(self, user_info, current_plan, ai_service):
        """
        Regenerate only the nutrition portion of an existing plan.
        
        Args:
            user_info (dict): User information and preferences
            current_plan (dict): Current complete plan
            ai_service (AnthropicService): Service for AI interactions
            
        Returns:
            dict: Updated complete plan
        """
        try:
            # Initialize workout model to prepare user preferences
            workout_model = WorkoutModel(
                weight=user_info["weight"],
                exercise_data=self.exercise_data
            )
            
            # Prepare user preferences
            user_preferences = workout_model.prepare_user_preferences(
                height=user_info["height_cm"],
                weight=user_info["weight"],
                goal_weight=user_info["goal_weight"],
                duration_weeks=user_info["time_frame"],
                location=user_info["location"],
                diet_preference=user_info["diet_preference"],
                time_constraint=user_info["time_constraint"],
                age=user_info["age"],
                gender=user_info["gender"],
                activity_level=user_info["activity_level"],
                food_type=user_info["food_type"]
            )
            
            # Generate nutrition plan
            logger.info("Regenerating nutrition plan...")
            nutrition_plan = self.nutrition_model.generate_nutrition_plan(user_preferences, ai_service)
            
            # Check for errors in nutrition plan
            if "error" in nutrition_plan:
                logger.error(f"Failed to regenerate nutrition plan: {nutrition_plan['error']}")
                return nutrition_plan
                
            # Create a mock workout plan with just the structure components
            workout_structure = {
                "user_profile": current_plan.get("user_profile", {}),
                "weight_loss_calculation": current_plan.get("weight_loss_calculation", {}),
                "daily_calorie_intake": current_plan.get("daily_calorie_intake", {}),
                "workout_plan": current_plan.get("workout_plan", {})
            }
            
            # Create updated plan (keep existing workout plan)
            updated_plan = self.nutrition_model.combine_plans(
                workout_structure,
                nutrition_plan
            )
            
            logger.info("Successfully regenerated nutrition plan")
            return updated_plan
            
        except Exception as e:
            logger.error(f"Error regenerating nutrition plan: {e}", exc_info=True)
            return {"error": f"Failed to regenerate nutrition plan: {str(e)}"}