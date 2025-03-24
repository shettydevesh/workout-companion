# Import modules
from dotenv import load_dotenv
import os
import streamlit as st
from config import AppConfig
from utils import setup_logging
from data import load_exercise_data
from models import PlanGenerator, AnthropicService
from ui import (render_header, user_info_form, user_profile_card, 
                          weight_loss_chart, display_workout_day, render_meal_table,
                          export_plan_button, load_custom_css)

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Load application configuration
config = AppConfig()

# Set page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide"
)

# Load custom CSS
load_custom_css()

# Application main function
def main():
    # Render header
    render_header()
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_KEY')
    if not api_key:
        st.warning("⚠️ Anthropic API key not found. Please add it to your .env file or enter it below.")
        api_key = st.text_input("Anthropic API Key", type="password")
        if not api_key:
            st.stop()
    
    # Initialize AI service
    ai_service = AnthropicService(
        api_key=api_key,
        model=config.AI_MODEL,
        max_retries=config.API_MAX_RETRIES,
        timeout=config.API_TIMEOUT
    )
    
    # Load exercise data
    try:
        exercise_df = load_exercise_data(config.DATASET_PATH)
        st.session_state['exercise_df'] = exercise_df
    except Exception as e:
        st.error(f"Error loading exercise data: {e}")
        st.stop()
    
    # Get user information from sidebar form
    user_info = user_info_form()
    # Generate plan when button is clicked
    if user_info["submit"]:
        with st.spinner('Generating your personalized fitness and nutrition plan...'):
            try:
                planner = PlanGenerator(exercise_df)
                plan, calculations = planner.generate_plan(user_info, ai_service)
                plan['weight_loss_calculation'] = {
                    'total_calories_to_burn': calculations.get('total_calories_to_burn'),
                    'daily_calorie_deficit': calculations.get('daily_calorie_deficit'),
                    'exercise_portion_calories': calculations.get('exercise_portion_calories'),
                    'diet_portion_calories': calculations.get('diet_portion_calories'),
                }
                plan['daily_calorie_intake'] = {
                    'baseline_calories': calculations.get('daily_maintenance_calories'),
                    'diet_calorie_deficit': calculations.get('diet_portion_calories'),
                    'target_daily_intake': calculations.get('target_daily_intake'),
                }
                # Display plan if successful
                if "error" in plan:
                    st.error(plan["error"])
                    if "raw_response" in plan:
                        with st.expander("View raw AI response"):
                            st.text(plan["raw_response"])
                else:
                    # Save plan to session state
                    st.session_state['current_plan'] = plan
                    
                    # Display user profile
                    user_profile_card(
                        plan.get("user_profile", {}),
                        user_info["height_ft"],
                        user_info["height_inch"],
                        user_info["height_cm"]
                    )
                    
                    # Display weight loss calculation
                    weight_loss_calc = plan.get("weight_loss_calculation", {})
                    weight_loss_chart(weight_loss_calc)
                    
                    # Display daily calorie intake recommendation
                    st.markdown('<div class="section-header">Recommended Daily Calorie Intake</div>', unsafe_allow_html=True)
                    calorie_intake = plan.get("daily_calorie_intake", {})
                    logger.info(f"Daily calorie intake: {calorie_intake}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div class="summary-box">
                            <p><strong>Baseline Calories:</strong> {calorie_intake.get('baseline_calories'):,.0f} kcal</p>
                            <p><strong>Diet Calorie Deficit:</strong> {calorie_intake.get('diet_calorie_deficit'):,.0f} kcal</p>
                            <p><strong>Target Daily Intake:</strong> {calorie_intake.get('target_daily_intake'):,.0f} kcal</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display workout plan
                    st.markdown('<div class="section-header">5-Day Workout Plan</div>', unsafe_allow_html=True)
                    
                    workout_plan = plan.get("workout_plan", {})
                    
                    st.markdown('<div class="subsection-header">Workout Strategy</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="info-box">
                        {workout_plan.get('strategy')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display detailed workout plan
                    st.markdown('<div class="subsection-header">Detailed Weekly Plan</div>', unsafe_allow_html=True)
                    
                    weekly_plan = workout_plan.get("weekly_plan", {})
                    for i, (day, info) in enumerate(weekly_plan.items()):
                        display_workout_day(day, info, i)
                    
                    # Display rest days
                    rest_days = workout_plan.get("rest_days", ["Saturday", "Sunday"])
                    st.markdown(f'<div class="day-header">{" & ".join(rest_days)}: Rest Days</div>', unsafe_allow_html=True)
                    
                    # Display nutrition plan
                    nutrition_plan = plan.get("nutrition_plan", {})
                    st.markdown(f'<div class="section-header">Nutrition Plan for {nutrition_plan.get("diet_preference")} in {nutrition_plan.get("location")}</div>', unsafe_allow_html=True)
                    
                    # Display meal plan
                    meals = nutrition_plan.get("meals", {})
                    for meal_name, meal_data in meals.items():
                        render_meal_table(meal_name, meal_data)
                    
                    # Add export functionality
                    export_plan_button(plan)
                    
            except Exception as e:
                st.error(f"Error generating plan: {e}")
                logger.error(f"Plan generation error: {e}", exc_info=True)
    else:
        # Show welcome screen
        st.markdown("""
        ## Welcome to your AI-powered Fitness & Nutrition Planner!
        
        This tool creates a personalized plan to help you achieve your weight and fitness goals.
        
        To get started:
        1. Fill in your details in the sidebar
        2. Click "Generate Plan" to see your personalized program
        3. Follow the workout and nutrition recommendations
        
        Your plan will be tailored to your specific body metrics, goals, and food preferences.
        """)
        
        # Add quick tips or information
        with st.expander("Why use Workout Companion?"):
            st.markdown("""
            - **Personalized Workout Plans**: Custom exercises based on your BMI and time constraints
            - **Culturally-Relevant Nutrition**: Meal plans with your preferred cuisine type
            - **Time-Efficient**: Workouts designed to fit your schedule
            - **Comprehensive Approach**: Combines exercise and nutrition for optimal results
            - **AI-Powered**: Uses advanced AI to create truly personalized recommendations
            """)

if __name__ == "__main__":
    main()