import pandas as pd
import logging
import streamlit as st
import os

logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_exercise_data(file_path='data/dataset.csv'):
    """
    Load and preprocess exercise data from CSV file.
    
    Args:
        file_path (str): Path to the exercise dataset CSV
        
    Returns:
        DataFrame: Processed exercise data
        
    Raises:
        FileNotFoundError: If dataset file is not found
        ValueError: If dataset doesn't have required columns
    """
    try:
        logger.info(f"Loading exercise data from: {file_path}")
        
        if not os.path.exists(file_path):
            alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                raise FileNotFoundError(f"Dataset file not found at {file_path}")
        
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} exercises from dataset")
        
        # Validate required columns
        required_columns = ['id', 'name', 'exercise_duration', 'calories_burned_per_kg']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Dataset missing required columns: {', '.join(missing_columns)}")
            
        # Clean and preprocess data
        # 1. Remove any duplicates by id
        df = df.drop_duplicates(subset=['id'])
        
        # 2. Sort by calorie efficiency (calories per minute)
        df['calories_per_minute'] = df['calories_burned_per_kg'] / (df['exercise_duration'] / 60)
        
        # 3. Make sure all numeric fields are the right type
        numeric_columns = ['exercise_duration', 'calories_burned_per_kg', 'calories_per_minute']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # 4. Drop rows with missing values in critical columns
        df = df.dropna(subset=numeric_columns)
        
        # 5. Log data quality metrics
        logger.info(f"Processed dataset: {len(df)} valid exercises")
        logger.info(f"Exercise duration range: {df['exercise_duration'].min()}-{df['exercise_duration'].max()} minutes")
        
        return df
        
    except FileNotFoundError as e:
        logger.error(f"Dataset file not found: {e}")
        raise
    except ValueError as e:
        logger.error(f"Dataset validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading exercise data: {e}", exc_info=True)
        raise ValueError(f"Failed to load exercise data: {str(e)}")