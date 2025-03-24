import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import anthropic
import json
import os
from dotenv import load_dotenv
import re
from models import WorkoutCompanion
# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Fitness & Nutrition Planner",
    page_icon="💪",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E88E5;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .subsection-header {
        font-size: 1.4rem;
        font-weight: bold;
        color: #1976D2;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .day-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #0D47A1;
        margin-top: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .summary-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    .big-metric {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .meal-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load or provide sample exercise data
@st.cache_data
def load_exercise_data():
    try:
        print("Loading exercise data...")
        df = pd.read_csv('dataset.csv')
        print("Exercise data loaded.")
        return df
    except FileNotFoundError:
        raise 'File Not Found.'


# Load exercise data
exercise_df = load_exercise_data()

# Sidebar for user inputs
st.sidebar.markdown("## User Information")

height_ft = st.sidebar.number_input("Height (feet)", min_value=4, max_value=7, value=5)
height_inch = st.sidebar.number_input("Height (inches)", min_value=0, max_value=11, value=10)
height_cm = (height_ft * 30.48) + (height_inch * 2.54)

weight = st.sidebar.number_input("Current Weight (kg)", min_value=40, max_value=200, value=73)
goal_weight = st.sidebar.number_input("Goal Weight (kg)", min_value=40, max_value=200, value=71)
time_frame = st.sidebar.slider("Time Frame (weeks)", min_value=4, max_value=30, value=4)

st.sidebar.markdown("## Additional Information")
age = st.sidebar.number_input("Age", min_value=18, max_value=80, value=22)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
activity_level = st.sidebar.selectbox("Activity Level", 
                                     ["Sedentary", "Lightly active", "Moderately active", "Very active", "Extra active"],
                                     index=0)
time_constraint = st.sidebar.slider("Daily Workout Time (minutes)", min_value=15, max_value=60, value=30)
location = st.sidebar.selectbox("Location", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"], index=0)
diet_preference = st.sidebar.selectbox("Diet Preference", ["Non-Vegetarian", "Vegetarian", "Vegan"], index=0)
food_type = st.sidebar.selectbox("Food Type", ["Maharashtrian", "Punjabi", "South Indian", "Gujarati", "Bengali"], index=0)

# Main content
st.markdown('<div class="main-header">Personalized Fitness & Nutrition Planner</div>', unsafe_allow_html=True)

# Button to generate plan
generate_button = st.sidebar.button("Generate Plan", type="primary")

if not generate_button:
    st.markdown("""
    Welcome to your personalized fitness and nutrition planner! This tool will help you create a comprehensive plan to achieve your weight loss goals.
    
    To get started:
    1. Fill in your details in the sidebar
    2. Enter your Anthropic API key (or set it as an environment variable)
    3. Click "Generate Plan" to see your personalized program
    4. Follow the workout and nutrition recommendations
    
    This plan will be specifically tailored to your body metrics, goals, and preferences.
    """)
    
    # Add sample images or illustrations
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align:center">
            <h3>🏋️‍♂️ Exercise Plan</h3>
            <p>Tailored workouts based on your BMI and preferences</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align:center">
            <h3>🍽️ Nutrition Plan</h3>
            <p>Meal recommendations with proper macros distribution</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align:center">
            <h3>📊 Progress Tracking</h3>
            <p>Guidelines to monitor your progress and adjust</p>
        </div>
        """, unsafe_allow_html=True)

# Generate plan when button is clicked
if generate_button:
    # Show loading indicator
    with st.spinner('Generating your personalized fitness and nutrition plan...'):
        # Initialize WorkoutCompanion
        personalized_data = exercise_df.copy()
        personalized_data['calories_burned_by_user'] = personalized_data['calories_burned_per_kg'] * weight
    
        companion = WorkoutCompanion(weight, personalized_data)
        
        # Generate plan
        plan = companion.recommend_exercises(
            height=height_cm,
            weight=weight,
            goal=goal_weight,
            duration=time_frame,
            location=location,
            preference=diet_preference,
            time_constraint=time_constraint,
            age=age,
            gender=gender,
            activity_level=activity_level, 
            food_type=food_type
        )
        # Check if there was an error
        if "error" in plan:
            st.error(plan["error"])
            if "raw_response" in plan:
                with st.expander("View raw response"):
                    st.text(plan["raw_response"])
        else:
            # Display user profile
            st.markdown('<div class="section-header">User Profile Overview</div>', unsafe_allow_html=True)
            
            user_profile = plan.get("user_profile", {})
            
            # Display user profile in 3 columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p>Current Weight</p>
                    <div class="big-metric">{user_profile.get('current_weight')} kg</div>
                </div>
                <div class="metric-card">
                    <p>Height</p>
                    <div class="big-metric">{height_ft}'{height_inch}" ({round(height_cm, 1)} cm)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <p>BMI</p>
                    <div class="big-metric">{user_profile.get('bmi')} ({user_profile.get('bmi_category')})</div>
                </div>
                <div class="metric-card">
                    <p>Goal Weight</p>
                    <div class="big-metric">{user_profile.get('goal_weight')} kg</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <p>Time Frame</p>
                    <div class="big-metric">{user_profile.get('duration_weeks')} weeks</div>
                </div>
                <div class="metric-card">
                    <p>Daily Workout Time</p>
                    <div class="big-metric">{user_profile.get('time_constraint_minutes')} mins</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display weight loss calculation
            st.markdown('<div class="section-header">Weight Loss Calculation</div>', unsafe_allow_html=True)
            
            weight_loss_calc = plan.get("weight_loss_calculation", {})
            # Display weight loss calculation in 2 columns")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="info-box">
                    <p><strong>Total Weight Loss Goal:</strong> {weight - goal_weight} kg</p>
                    <p><strong>Total Calorie Deficit Needed:</strong> {weight - goal_weight} kg × 7,700 = {weight_loss_calc.get('total_calories_to_burn'):,.0f} calories</p>
                    <p><strong>Daily Calorie Deficit:</strong> {weight_loss_calc.get('daily_calorie_deficit'):,.0f} calories</p>
                    <ul>
                        <li><strong>Exercise Portion (30%):</strong> {weight_loss_calc.get('exercise_portion_calories'):,.0f} calories per day</li>
                        <li><strong>Diet Portion (70%):</strong> {(weight_loss_calc.get('daily_calorie_deficit') - weight_loss_calc.get('exercise_portion_calories')):,.0f} calories per day</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                # Create a pie chart for deficit distribution
                fig = go.Figure(data=[go.Pie(
                    labels=['Exercise Deficit', 'Diet Deficit'],
                    values=[weight_loss_calc.get('exercise_portion_calories'), (weight_loss_calc.get('daily_calorie_deficit') - weight_loss_calc.get('exercise_portion_calories'))],
                    hole=.3,
                    marker_colors=['#1E88E5', '#43A047']
                )])
                fig.update_layout(
                    title="Daily Calorie Deficit Distribution",
                    margin=dict(t=30, b=0, l=0, r=0),
                    height=250
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Display calorie intake recommendation
            st.markdown('<div class="section-header">Recommended Daily Calorie Intake</div>', unsafe_allow_html=True)
            
            calorie_intake = plan.get("daily_calorie_intake", {})
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="summary-box">
                    <p><strong>Baseline Calories:</strong> {calorie_intake.get('baseline_calories'):,.0f} kcal</p>
                    <p><strong>Diet Calorie Deficit:</strong> {calorie_intake.get('diet_calorie_deficit'):,.0f} kcal</p>
                    <p><strong>Target Daily Intake:</strong> {calorie_intake.get('target_daily_intake'):,.0f} kcal</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                # Create a bar chart for calorie comparison
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Maintenance', 'Target Intake'],
                    y=[calorie_intake.get('baseline_calories'), calorie_intake.get('target_daily_intake')],
                    marker_color=['#FFA726', '#1E88E5']
                ))
                fig.update_layout(
                    title="Calorie Comparison",
                    yaxis_title="Calories (kcal)",
                    margin=dict(t=30, b=0, l=0, r=0),
                    height=250
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Display weekly workout plan
            st.markdown('<div class="section-header">5-Day Workout Plan</div>', unsafe_allow_html=True)
            
            workout_plan = plan.get("workout_plan", {})
            
            st.markdown('<div class="subsection-header">Workout Strategy</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-box">
                {workout_plan.get('strategy')}
            </div>
            """, unsafe_allow_html=True)
            
            # Display workout plan
            st.markdown('<div class="subsection-header">Detailed Weekly Plan</div>', unsafe_allow_html=True)
            
            weekly_plan = workout_plan.get("weekly_plan", {})
            for day, info in weekly_plan.items():
                st.markdown(f'<div class="day-header">{day}: {info.get("focus")}</div>', unsafe_allow_html=True)
                
                # Create workout table
                workout_data = []
                for i, workout in enumerate(info.get("workouts", [])):
                    workout_data.append([
                        f"{i+1}. {workout.get('name')} ({workout.get('type')})",
                        f"{workout.get('duration_mins')} mins",
                        f"{workout.get('calories_burned'):,.0f} calories"
                    ])
                
                # Add totals
                workout_data.append([
                    "<strong>Total</strong>",
                    f"<strong>{info.get('total_time')} mins</strong>",
                    f"<strong>{info.get('total_calories'):,.0f} calories</strong>"
                ])
                
                # Create DataFrame and display
                df = pd.DataFrame(workout_data, columns=["Exercise", "Duration", "Calories Burned"])
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                # Display alternatives
                alternatives = []
                for workout in info.get("workouts", []):
                    alternatives.extend(workout.get("alternatives", []))
                
                st.markdown(f"<p><strong>Alternatives:</strong> {', '.join(alternatives)}</p>", unsafe_allow_html=True)
            
            # Display rest days
            rest_days = workout_plan.get("rest_days", ["Saturday", "Sunday"])
            st.markdown(f'<div class="day-header">{" & ".join(rest_days)}: Rest Days</div>', unsafe_allow_html=True)
            st.markdown("""
            <p>Light stretching (5-10 minutes)</p>
            <p>Walking (20-30 minutes, optional)</p>
            <p>Active recovery activities</p>
            """, unsafe_allow_html=True)
            
            # Display nutrition plan
            nutrition_plan = plan.get("nutrition_plan", {})
            st.markdown(f'<div class="section-header">Nutrition Plan for {nutrition_plan.get("diet_preference")} in {nutrition_plan.get("location")}</div>', unsafe_allow_html=True)
            
            # Display macronutrient distribution
            st.markdown('<div class="subsection-header">Macronutrient Breakdown</div>', unsafe_allow_html=True)
            
            macros = nutrition_plan.get("macros", {})
            col1, col2 = st.columns(2)

            with col1:
                # Check if macros has nested structure or simple values
                protein_value = macros.get('protein', 0)
                carbs_value = macros.get('carbs', 0)
                fat_value = macros.get('fat', 0)
                
                # Handle both possible data structures
                if isinstance(protein_value, dict):
                    # Nested structure with grams/percentage
                    protein_grams = protein_value.get('grams', 0)
                    protein_pct = protein_value.get('percentage', 0)
                    carbs_grams = carbs_value.get('grams', 0) 
                    carbs_pct = carbs_value.get('percentage', 0)
                    fat_grams = fat_value.get('grams', 0)
                    fat_pct = fat_value.get('percentage', 0)
                else:
                    # Simple numeric values
                    protein_grams = protein_value
                    carbs_grams = carbs_value
                    fat_grams = fat_value
                    
                    # Calculate percentages if needed (assuming total calories known)
                    total_calories = nutrition_plan.get("daily_calories", 2000)
                    protein_calories = protein_grams * 4  # 4 calories per gram of protein
                    carbs_calories = carbs_grams * 4  # 4 calories per gram of carbs
                    fat_calories = fat_grams * 9  # 9 calories per gram of fat
                    
                    protein_pct = round((protein_calories / total_calories) * 100)
                    carbs_pct = round((carbs_calories / total_calories) * 100)
                    fat_pct = round((fat_calories / total_calories) * 100)
                
                st.markdown(f"""
                <div class="summary-box">
                    <p><strong>Protein:</strong> {protein_grams}g ({protein_pct}% of total calories)</p>
                    <p><strong>Carbohydrates:</strong> {carbs_grams}g ({carbs_pct}% of total calories)</p>
                    <p><strong>Fats:</strong> {fat_grams}g ({fat_pct}% of total calories)</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                # Get macronutrient values with defaults
                protein = macros.get('protein', 0)
                carbs = macros.get('carbs', 0)
                fat = macros.get('fat', 0)
                
                # Calculate calories for each macronutrient
                protein_calories = protein * 4  # 4 calories per gram of protein
                carbs_calories = carbs * 4      # 4 calories per gram of carbs
                fat_calories = fat * 9          # 9 calories per gram of fat
                total_calories = protein_calories + carbs_calories + fat_calories
                
                # Calculate percentages
                if total_calories > 0:
                    protein_pct = round((protein_calories / total_calories) * 100)
                    carbs_pct = round((carbs_calories / total_calories) * 100)
                    fat_pct = round((fat_calories / total_calories) * 100)
                else:
                    protein_pct, carbs_pct, fat_pct = 0, 0, 0
                
                # Create a pie chart for macronutrient distribution
                fig = go.Figure(data=[go.Pie(
                    labels=['Protein', 'Carbs', 'Fat'],
                    values=[protein_pct, carbs_pct, fat_pct],
                    hole=.3,
                    marker_colors=['#1E88E5', '#43A047', '#FFA726'],
                    text=[f"{protein_pct}%", f"{carbs_pct}%", f"{fat_pct}%"],
                    textinfo='text'
                )])
                
                fig.update_layout(
                    title="Macronutrient Distribution",
                    margin=dict(t=30, b=0, l=0, r=0),
                    height=250
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Display daily meal breakdown
            st.markdown(f'<div class="subsection-header">Daily Meal Breakdown ({nutrition_plan.get("daily_calories"):,.0f} kcal)</div>', unsafe_allow_html=True)
            
            meals = nutrition_plan.get("meals", {})
            for meal_name, meal_data in meals.items():
                display_name = meal_name.replace("_", " ")
                st.markdown(f'<div class="day-header">{display_name} ({meal_data.get("calories"):,.0f} kcal)</div>', unsafe_allow_html=True)
                
                # Create meal table
                meal_items = []
                for item in meal_data.get("items", []):
                    meal_items.append([
                        item.get("name"),
                        item.get("quantity"),
                        f"{item.get('calories'):,.0f} kcal",
                        f"{item.get('protein')}g",
                        f"{item.get('carbs')}g",
                        f"{item.get('fat')}g"
                    ])
                
                # Add totals
                meal_items.append([
                    "<strong>Total</strong>",
                    "",
                    f"<strong>{meal_data.get('calories'):,.0f} kcal</strong>",
                    f"<strong>{meal_data.get('total_protein')}g</strong>",
                    f"<strong>{meal_data.get('total_carbs')}g</strong>",
                    f"<strong>{meal_data.get('total_fat')}g</strong>"
                ])
                
                # Create DataFrame and display
                df = pd.DataFrame(meal_items, columns=["Food Item", "Quantity", "Calories", "Protein", "Carbs", "Fat"])
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            # Final notes
            st.markdown("""
            <div class="info-box">
                <p>This plan is designed for your specific needs based on the information provided. Adjust as needed based on your progress and how you feel. Remember that consistency is key to achieving your fitness goals!</p>
                <p>For any significant modifications to your plan or if you experience unusual discomfort, please consult with a healthcare professional.</p>
            </div>
            """, unsafe_allow_html=True)