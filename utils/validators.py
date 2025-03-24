import logging
import re

logger = logging.getLogger(__name__)

class InputValidator:
    """Validates user inputs to prevent errors in calculations."""
    
    @staticmethod
    def validate_numeric(value, field_name, min_value=None, max_value=None):
        """
        Validate a numeric input.
        
        Args:
            value: Input value to validate
            field_name (str): Name of the field for error messages
            min_value (float, optional): Minimum allowed value
            max_value (float, optional): Maximum allowed value
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Convert to float
            num_value = float(value)
            
            # Check minimum value if provided
            if min_value is not None and num_value < min_value:
                return False, f"{field_name} must be at least {min_value}"
                
            # Check maximum value if provided
            if max_value is not None and num_value > max_value:
                return False, f"{field_name} must not exceed {max_value}"
                
            return True, None
            
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid number"
    
    @staticmethod
    def validate_string(value, field_name, allowed_values=None, pattern=None):
        """
        Validate a string input.
        
        Args:
            value (str): Input string to validate
            field_name (str): Name of the field for error messages
            allowed_values (list, optional): List of allowed values
            pattern (str, optional): Regex pattern to match
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if string is empty
        if not value or not isinstance(value, str):
            return False, f"{field_name} cannot be empty"
            
        # Check against allowed values if provided
        if allowed_values and value not in allowed_values:
            return False, f"{field_name} must be one of: {', '.join(allowed_values)}"
            
        # Check against pattern if provided
        if pattern and not re.match(pattern, value):
            return False, f"{field_name} format is invalid"
            
        return True, None
    
    @staticmethod
    def validate_user_inputs(inputs):
        """
        Validate all user inputs for the workout plan.
        
        Args:
            inputs (dict): Dictionary of user inputs
            
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate height
        height_valid, height_error = InputValidator.validate_numeric(
            inputs.get("height_cm"), "Height", 100, 250
        )
        if not height_valid:
            errors.append(height_error)
            
        # Validate weight
        weight_valid, weight_error = InputValidator.validate_numeric(
            inputs.get("weight"), "Current weight", 30, 300
        )
        if not weight_valid:
            errors.append(weight_error)
            
        # Validate goal weight
        goal_valid, goal_error = InputValidator.validate_numeric(
            inputs.get("goal_weight"), "Goal weight", 30, 300
        )
        if not goal_valid:
            errors.append(goal_error)
            
        # Validate time frame
        timeframe_valid, timeframe_error = InputValidator.validate_numeric(
            inputs.get("time_frame"), "Time frame", 1, 52
        )
        if not timeframe_valid:
            errors.append(timeframe_error)
            
        # Validate age
        age_valid, age_error = InputValidator.validate_numeric(
            inputs.get("age"), "Age", 18, 100
        )
        if not age_valid:
            errors.append(age_error)
            
        # Validate gender
        gender_valid, gender_error = InputValidator.validate_string(
            inputs.get("gender"), "Gender", ["Male", "Female"]
        )
        if not gender_valid:
            errors.append(gender_error)
            
        # Validate time constraint
        time_valid, time_error = InputValidator.validate_numeric(
            inputs.get("time_constraint"), "Workout time constraint", 15, 120
        )
        if not time_valid:
            errors.append(time_error)
            
        # Check weight loss goal feasibility
        if weight_valid and goal_valid and timeframe_valid:
            weight = float(inputs.get("weight"))
            goal = float(inputs.get("goal_weight"))
            weeks = float(inputs.get("time_frame"))
            
            if goal > weight:
                errors.append("Goal weight must be less than current weight for weight loss")
            else:
                # Check if weight loss rate is healthy (max 1kg per week)
                weight_diff = weight - goal
                weekly_loss = weight_diff / weeks
                
                if weekly_loss > 1:
                    errors.append(f"Weight loss goal of {weight_diff:.1f}kg in {weeks:.0f} weeks exceeds healthy rate of 1kg per week")
        
        # Return validation result
        return (len(errors) == 0, errors)