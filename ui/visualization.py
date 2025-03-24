import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st

def create_calendar_heatmap(weekly_plan):
    """
    Create a calendar heatmap showing the workout intensity by day.
    
    Args:
        weekly_plan (dict): Weekly workout plan data
        
    Returns:
        plotly.graph_objects.Figure: Calendar heatmap
    """
    # Days of the week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Initialize values array
    values = np.zeros(7)
    hover_texts = [""] * 7
    
    # Fill in values for workout days
    for day, info in weekly_plan.items():
        if day in days:
            day_index = days.index(day)
            values[day_index] = info.get("total_calories", 0)
            workout_names = [w.get("name") for w in info.get("workouts", [])]
            hover_texts[day_index] = f"{day}: {', '.join(workout_names)}"
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[values],
        x=days,
        y=["Week 1"],
        colorscale="Blues",
        text=[hover_texts],
        hoverinfo="text"
    ))
    
    fig.update_layout(
        title="Weekly Workout Schedule",
        height=200,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    return fig

def create_workout_comparison_chart(weekly_plan):
    """
    Create a bar chart comparing workouts across days.
    
    Args:
        weekly_plan (dict): Weekly workout plan data
        
    Returns:
        plotly.graph_objects.Figure: Workout comparison chart
    """
    days = []
    calories = []
    durations = []
    
    for day, info in weekly_plan.items():
        days.append(day)
        calories.append(info.get("total_calories", 0))
        durations.append(info.get("total_time", 0))
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=days,
        y=calories,
        name="Calories Burned",
        marker_color="#1E88E5"
    ))
    
    fig.add_trace(go.Scatter(
        x=days,
        y=durations,
        name="Duration (mins)",
        marker_color="#FFA726",
        line=dict(width=4),
        yaxis="y2"
    ))
    
    fig.update_layout(
        title="Workout Comparison by Day",
        xaxis=dict(title="Day"),
        yaxis=dict(
            title="Calories Burned",
            side="left"
        ),
        yaxis2=dict(
            title="Duration (mins)",
            side="right",
            overlaying="y",
            showgrid=False
        ),
        legend=dict(x=0.01, y=0.99),
        height=400
    )
    
    return fig

def create_nutrition_breakdown(meals):
    """
    Create a stacked bar chart showing nutrition breakdown by meal.
    
    Args:
        meals (dict): Nutrition plan meals data
        
    Returns:
        plotly.graph_objects.Figure: Nutrition breakdown chart
    """
    meal_names = []
    proteins = []
    carbs = []
    fats = []
    calories = []
    
    for meal_name, meal_data in meals.items():
        meal_names.append(meal_name.replace("_", " "))
        proteins.append(meal_data.get("total_protein", 0))
        carbs.append(meal_data.get("total_carbs", 0))
        fats.append(meal_data.get("total_fat", 0))
        calories.append(meal_data.get("calories", 0))
    
    # Create the stacked bar chart for macros
    fig = go.Figure(data=[
        go.Bar(name="Protein", x=meal_names, y=proteins, marker_color="#1E88E5"),
        go.Bar(name="Carbs", x=meal_names, y=carbs, marker_color="#43A047"),
        go.Bar(name="Fat", x=meal_names, y=fats, marker_color="#FFA726")
    ])
    
    # Add calories as a line on secondary axis
    fig.add_trace(go.Scatter(
        x=meal_names,
        y=calories,
        name="Calories",
        line=dict(color="red", width=3),
        yaxis="y2"
    ))
    
    fig.update_layout(
        barmode="stack",
        title="Nutrition Breakdown by Meal",
        xaxis=dict(title="Meal"),
        yaxis=dict(
            title="Macronutrients (g)",
            side="left"
        ),
        yaxis2=dict(
            title="Calories",
            side="right",
            overlaying="y",
            showgrid=False
        ),
        legend=dict(x=0.01, y=0.99),
        height=400
    )
    
    return fig