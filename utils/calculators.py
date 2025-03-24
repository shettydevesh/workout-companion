import logging

logger = logging.getLogger(__name__)

class FitnessCalculator:
    """Handles all fitness-related calculations."""
    
    def __init__(self):
        """Initialize the fitness calculator with standard reference values."""
        # Activity level multipliers
        self.activity_multipliers = {
            'sedentary': 1.2,
            'lightly active': 1.375,
            'moderately active': 1.55,
            'very active': 1.725,
            'extra active': 1.9
        }
        
        # BMI category thresholds
        self.bmi_categories = {
            (0, 18.5): "Underweight",
            (18.5, 25): "Normal weight",
            (25, 30): "Overweight",
            (30, float('inf')): "Obese"
        }
        
        # Calories per kg of fat loss
        self.calories_per_kg_fat = 7700
        
    def calculate_bmi(self, weight_kg, height_cm):
        """
        Calculate Body Mass Index (BMI).
        
        Args:
            weight_kg (float): Weight in kilograms
            height_cm (float): Height in centimeters
            
        Returns:
            float: BMI value rounded to 2 decimal places
        """
        if height_cm <= 0:
            logger.error(f"Invalid height: {height_cm}cm")
            raise ValueError("Height must be greater than 0")
            
        if weight_kg <= 0:
            logger.error(f"Invalid weight: {weight_kg}kg")
            raise ValueError("Weight must be greater than 0")
            
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 2)
    
    def get_bmi_category(self, bmi):
        """
        Determine BMI category.
        
        Args:
            bmi (float): BMI value
            
        Returns:
            str: BMI category name
        """
        for (lower, upper), category in self.bmi_categories.items():
            if lower <= bmi < upper:
                return category
                
        return "Obese"  # Default for values above highest threshold
    
    def calculate_bmr(self, weight_kg, height_cm, age, gender):
        """
        Calculate Basal Metabolic Rate using Harris-Benedict formula.
        
        Args:
            weight_kg (float): Weight in kilograms
            height_cm (float): Height in centimeters
            age (int): Age in years
            gender (str): 'male' or 'female'
            
        Returns:
            float: BMR value
        """
        gender = gender.lower()
        if gender not in ['male', 'female']:
            logger.error(f"Invalid gender: {gender}")
            raise ValueError("Gender must be 'male' or 'female'")
            
        if gender == 'male':
            bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
            
        return round(bmr, 2)
    
    def get_activity_multiplier(self, activity_level):
        """
        Get the activity multiplier for a given activity level.
        
        Args:
            activity_level (str): Activity level descriptor
            
        Returns:
            float: Activity multiplier
        """
        activity_level = activity_level.lower()
        
        # Try exact match first
        if activity_level in self.activity_multipliers:
            return self.activity_multipliers[activity_level]
            
        # Try partial match
        for key in self.activity_multipliers:
            if key in activity_level:
                return self.activity_multipliers[key]
                
        # Default to sedentary if no match found
        logger.warning(f"Unknown activity level: {activity_level}, defaulting to sedentary")
        return self.activity_multipliers['sedentary']
    
    def calculate_tdee(self, bmr, activity_level):
        """
        Calculate Total Daily Energy Expenditure.
        
        Args:
            bmr (float): Basal Metabolic Rate
            activity_level (str): Activity level descriptor
            
        Returns:
            float: TDEE value
        """
        multiplier = self.get_activity_multiplier(activity_level)
        tdee = bmr * multiplier
        return round(tdee, 2)
    
    def calculate_weight_loss_calories(self, current_weight, goal_weight, timeframe_weeks):
        """
        Calculate the calories needed to reach a weight loss goal.
        
        Args:
            current_weight (float): Current weight in kg
            goal_weight (float): Target weight in kg
            timeframe_weeks (int): Number of weeks to achieve goal
            
        Returns:
            dict: Calorie deficit information
        """
        if current_weight <= goal_weight:
            logger.warning(f"Goal weight ({goal_weight}kg) is not less than current weight ({current_weight}kg)")
            weight_to_lose = 0
        else:
            weight_to_lose = current_weight - goal_weight
            
        # Calculate total calorie deficit needed
        total_calorie_deficit = weight_to_lose * self.calories_per_kg_fat
        
        # Daily deficit needed
        days = timeframe_weeks * 7
        daily_deficit = total_calorie_deficit / days if days > 0 else 0
        
        # Split between exercise and diet
        exercise_portion = daily_deficit * 0.3
        diet_portion = daily_deficit * 0.7
        
        return {
            "total_calories_to_burn": round(total_calorie_deficit, 2),
            "daily_calorie_deficit": round(daily_deficit, 2),
            "exercise_portion_calories": round(exercise_portion, 2),
            "diet_portion_calories": round(diet_portion, 2)
        }
        
    def calculate_exercise_calories(self, exercise_duration, calories_per_kg, weight_kg):
        """
        Calculate calories burned during an exercise.
        
        Args:
            exercise_duration (float): Duration in minutes
            calories_per_kg (float): Calories burned per kg of body weight
            weight_kg (float): User's weight in kg
            
        Returns:
            float: Total calories burned
        """
        total_calories = calories_per_kg * weight_kg
        return round(total_calories, 2)