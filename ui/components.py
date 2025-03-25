import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)


def render_header():
    """
    Render the application header with logo and title.
    """
    st.markdown("""
    <div class="main-header">
        💪 Personalized Fitness & Nutrition Planner
    </div>
    """, unsafe_allow_html=True)

def user_info_form():
    """
    Render the user information form in the sidebar.
    
    Returns:
        dict: User input values
    """
    with st.sidebar:
        st.markdown("## User Information")
        
        height_ft = st.number_input("Height (feet)", min_value=4, max_value=7, value=5)
        height_inch = st.number_input("Height (inches)", min_value=0, max_value=11, value=10)
        height_cm = (height_ft * 30.48) + (height_inch * 2.54)
        
        weight = st.number_input("Current Weight (kg)", min_value=40, max_value=200, value=73)
        goal_weight = st.number_input("Goal Weight (kg)", min_value=40, max_value=200, value=71)
        time_frame = st.slider("Time Frame (weeks)", min_value=4, max_value=30, value=4)
        
        st.markdown("## Additional Information")
        age = st.number_input("Age", min_value=18, max_value=80, value=22)
        gender = st.selectbox("Gender", ["Male", "Female"])
        
        activity_level = st.selectbox(
            "Activity Level", 
            ["Sedentary", "Lightly active", "Moderately active", "Very active", "Extra active"],
            index=0
        )
        
        time_constraint = st.slider("Daily Workout Time (minutes)", min_value=15, max_value=60, value=30)
        location = st.selectbox("Location", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"], index=0)
        diet_preference = st.selectbox("Diet Preference", ["Non-Vegetarian", "Vegetarian", "Vegan"], index=0)
        food_type = st.selectbox("Food Type", ["Maharashtrian", "Punjabi", "South Indian", "Gujarati", "Bengali"], index=0)
        
        submit_button = st.button("Generate Plan", type="primary")
        
        return {
            "submit": submit_button,
            "height_ft": height_ft,
            "height_inch": height_inch,
            "height_cm": height_cm,
            "weight": weight,
            "goal_weight": goal_weight,
            "time_frame": time_frame,
            "age": age,
            "gender": gender,
            "activity_level": activity_level,
            "time_constraint": time_constraint,
            "location": location,
            "diet_preference": diet_preference,
            "food_type": food_type,
        }

def user_profile_card(user_profile, height_ft, height_inch, height_cm):
    
    """
    Render the user profile overview card.
    
    Args:
        user_profile (dict): User profile data
        height_ft (int): Height in feet
        height_inch (int): Height in inches
        height_cm (float): Height in centimeters
    """
    st.markdown('<div class="section-header">User Profile Overview</div>', unsafe_allow_html=True)
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

def weight_loss_chart(weight_loss_calc):
    """
    Display weight loss calculation with visualization.
    
    Args:
        weight_loss_calc (dict): Weight loss calculation data
    """
    st.markdown('<div class="section-header">Weight Loss Calculation</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="info-box">
            <p><strong>Total Calorie Deficit Needed:</strong> {weight_loss_calc.get('total_calories_to_burn'):,.0f} calories</p>
            <p><strong>Daily Calorie Deficit:</strong> {weight_loss_calc.get('daily_calorie_deficit'):,.0f} calories</p>
            <ul>
                <li><strong>Exercise Portion (30%):</strong> {weight_loss_calc.get('exercise_portion_calories'):,.0f} calories per day</li>
                <li><strong>Diet Portion (70%):</strong> {(weight_loss_calc.get('diet_portion_calories')):,.0f} calories per day</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Create a pie chart for deficit distribution
        fig = go.Figure(data=[go.Pie(
            labels=['Exercise Deficit', 'Diet Deficit'],
            values=[weight_loss_calc.get('exercise_portion_calories'), 
                    (weight_loss_calc.get('diet_portion_calories'))],
            hole=.3,
            marker_colors=['#1E88E5', '#43A047']
        )])
        fig.update_layout(
            title="Daily Calorie Deficit Distribution",
            margin=dict(t=30, b=0, l=0, r=0),
            height=250
        )
        st.plotly_chart(fig, use_container_width=True)

def display_workout_day(day, info, workout_index):
    """
    Display a single workout day's details.
    
    Args:
        day (str): Day of the week
        info (dict): Workout information for the day
        workout_index (int): Index for the HTML ID
    """
    st.markdown(f'<div class="day-header" id="workout-day-{workout_index}">{day}: {info.get("focus")}</div>', unsafe_allow_html=True)
    
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
    
def render_meal_table(meal_name, meal_data):
    """
    Render a single meal table with details.
    
    Args:
        meal_name (str): Name of the meal
        meal_data (dict): Nutritional data for the meal
    """
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

def render_macros_chart(macros, daily_calories):
    """
    Render a pie chart showing macronutrient distribution.
    
    Args:
        macros (dict): Macronutrient data
        daily_calories (float): Total daily calorie target
    """
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
        
        # Calculate percentages
        protein_calories = protein_grams * 4  # 4 calories per gram of protein
        carbs_calories = carbs_grams * 4      # 4 calories per gram of carbs
        fat_calories = fat_grams * 9          # 9 calories per gram of fat
        total_cals = protein_calories + carbs_calories + fat_calories
        
        if total_cals > 0:
            protein_pct = round((protein_calories / total_cals) * 100)
            carbs_pct = round((carbs_calories / total_cals) * 100)
            fat_pct = round((fat_calories / total_cals) * 100)
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
    
    # Display detailed macros
    st.markdown(f"""
    <div class="summary-box">
        <p><strong>Protein:</strong> {protein_grams}g ({protein_pct}% of total calories)</p>
        <p><strong>Carbohydrates:</strong> {carbs_grams}g ({carbs_pct}% of total calories)</p>
        <p><strong>Fats:</strong> {fat_grams}g ({fat_pct}% of total calories)</p>
        <p><strong>Total Daily Calories:</strong> {daily_calories:,.0f} kcal</p>
    </div>
    """, unsafe_allow_html=True)

def render_progress_tracker(current_weight, goal_weight, duration_weeks):
    """
    Render a progress tracker showing expected weight loss trajectory.
    
    Args:
        current_weight (float): Starting weight in kg
        goal_weight (float): Target weight in kg
        duration_weeks (int): Time frame in weeks
    """
    # Generate expected progress data
    weight_to_lose = current_weight - goal_weight
    weekly_loss = weight_to_lose / duration_weeks
    
    weeks = list(range(duration_weeks + 1))
    expected_weights = [current_weight - (weekly_loss * week) for week in weeks]
    
    # Create the chart
    fig = px.line(
        x=weeks,
        y=expected_weights,
        markers=True,
        labels={"x": "Week", "y": "Weight (kg)"},
        title="Expected Weight Loss Trajectory"
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        yaxis=dict(range=[min(goal_weight * 0.95, min(expected_weights)), current_weight * 1.02])
    )
    
    # Add goal line
    fig.add_hline(
        y=goal_weight,
        line_dash="dash",
        line_color="green",
        annotation_text="Goal Weight",
        annotation_position="bottom right"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add weekly breakdown
    st.markdown(f"""
    <div class="info-box">
        <p><strong>Weekly Weight Loss Goal:</strong> {weekly_loss:.2f} kg per week</p>
        <p><strong>Daily Calorie Deficit Needed:</strong> {(weekly_loss * 7700 / 7):.0f} calories per day</p>
    </div>
    """, unsafe_allow_html=True)

def export_plan_button(plan_data):
    """
    Create buttons to export the plan in different formats.
    
    Args:
        plan_data (dict): Plan data to export
    """
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as JSON
        if st.download_button(
            label="📊 Export Plan as JSON",
            data=json.dumps(plan_data, indent=2),
            file_name=f"workout_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        ):
            st.success("Plan exported as JSON!")
    
    with col2:
        # Future implementation: Export as PDF
        if st.button("📄 Export Plan as PDF (Coming Soon)"):
            st.info("PDF export functionality will be available in the next update!")