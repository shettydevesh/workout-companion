import os
from pathlib import Path

class AppConfig:
    def __init__(self):
        """Initialize configuration with default values and environment overrides."""
        # Application metadata
        self.APP_TITLE = "Fitness & Nutrition Planner"
        self.APP_ICON = "💪"
        self.APP_VERSION = "1.0.0"
        
        # File paths
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.DATASET_PATH = os.getenv("DATASET_PATH", str(self.BASE_DIR / "data" / "dataset.csv"))
        self.LOG_DIR = os.getenv("LOG_DIR", str(self.BASE_DIR / "logs"))
        
        # Ensure log directory exists
        Path(self.LOG_DIR).mkdir(exist_ok=True, parents=True)
        
        # API Configuration
        self.AI_MODEL = os.getenv("AI_MODEL", "claude-3-haiku-20240307")
        self.API_MAX_TOKENS = int(os.getenv("API_MAX_TOKENS", "4000"))
        self.API_TEMPERATURE = float(os.getenv("API_TEMPERATURE", "0"))
        self.API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))
        self.API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))
        
        # Default user parameters
        self.DEFAULT_HEIGHT_FT = 5
        self.DEFAULT_HEIGHT_IN = 10
        self.DEFAULT_WEIGHT = 73
        self.DEFAULT_GOAL_WEIGHT = 71
        self.DEFAULT_TIME_FRAME = 4
        self.DEFAULT_AGE = 22
        self.DEFAULT_TIME_CONSTRAINT = 30
        
        # Calculation constants
        self.CALORIES_PER_KG_LOSS = 7700
        self.EXERCISE_DEFICIT_PORTION = 0.3
        self.DIET_DEFICIT_PORTION = 0.7
        
        # Activity level multipliers
        self.PAL_SCORES = {
            "sedentary": 1.2,
            "lightly active": 1.375,
            "moderately active": 1.55,
            "very active": 1.725,
            "extra active": 1.9
        }
        
        # BMI categories
        self.BMI_CATEGORIES = {
            "underweight": {"max": 18.5},
            "normal weight": {"min": 18.5, "max": 25},
            "overweight": {"min": 25, "max": 30},
            "obese": {"min": 30}
        }