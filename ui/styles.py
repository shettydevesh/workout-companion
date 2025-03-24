import streamlit as st

def load_custom_css():
    """
    Load custom CSS styles for the application.
    Applies consistent styling to various UI components.
    """
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
        /* Make the sidebar wider */
        [data-testid="stSidebar"] {
            min-width: 350px !important;
        }
        /* Improve table styling */
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background-color: #E3F2FD;
            padding: 8px;
            text-align: left;
        }
        td {
            padding: 8px;
            border-top: 1px solid #E0E0E0;
        }
        tr:nth-child(even) {
            background-color: #F5F5F5;
        }
        /* Button styling */
        .stButton>button {
            width: 100%;
        }
        /* Footer styling */
        footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            color: #757575;
            font-size: 0.8rem;
        }
    </style>
    """, unsafe_allow_html=True)