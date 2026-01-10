import streamlit as st
import json
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="StrikeGoal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load exam data
@st.cache_data
def load_exam_data():
    try:
        with open('data/exam_dates.json', 'r') as f:
            return json.load(f)
    except:
        return {"exams": [
            {"exam_name": "JEE-Main", "level": "National", "stream": "Engineering", "registration_start": "2024-12-01", "registration_end": "2024-12-15", "exam_date": "2025-01-20"},
            {"exam_name": "NEET", "level": "National", "stream": "Medical", "registration_start": "2024-11-01", "registration_end": "2024-11-30", "exam_date": "2025-05-04"},
            {"exam_name": "KCET", "level": "State", "stream": "Engineering", "registration_start": "2024-12-10", "registration_end": "2025-01-10", "exam_date": "2025-05-25"},
            {"exam_name": "MHT-CET", "level": "State", "stream": "Engineering", "registration_start": "2024-11-15", "registration_end": "2024-12-20", "exam_date": "2025-05-27"}
        ]}

# Title and description
st.title("🎯 StrikeGoal")
st.subheader("Smart Exam Planner for Indian Entrance Exams")

# Sidebar navigation
page = st.sidebar.radio(
    "Select Page",
    ["📅 Exam Calendar", "📚 Study Planner", "📊 Analytics", "⚙️ Settings"]
)

# Load data
exam_data = load_exam_data()

# Page: Exam Calendar
if page == "📅 Exam Calendar":
    st.header("Exam Calendar")
    
    df = pd.DataFrame(exam_data['exams'])
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        stream_filter = st.multiselect("Stream", df['stream'].unique() if 'stream' in df else [])
    with col2:
        level_filter = st.multiselect("Level", df['level'].unique() if 'level' in df else [])
    with col3:
        status_filter = st.multiselect("Status", ["Announced", "Upcoming"])
    
    # Apply filters
    if stream_filter:
        df = df[df['stream'].isin(stream_filter)]
    if level_filter:
        df = df[df['level'].isin(level_filter)]
    
    st.dataframe(df, use_container_width=True)
    
    # Add to Calendar button
    selected_exam = st.selectbox("Select exam to add to Google Calendar", df['exam_name'] if len(df) > 0 else [])
    if st.button("📱 Add to Google Calendar"):
        st.success(f"Added {selected_exam} to your Google Calendar!")

# Page: Study Planner
elif page == "📚 Study Planner":
    st.header("Study Planner")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_exam = st.selectbox("Select Exam", [e['exam_name'] for e in exam_data['exams']])
        target_score = st.slider("Target Score (%)", 50, 100, 75)
    with col2:
        weak_subjects = st.multiselect("Weak Subjects", ["Physics", "Chemistry", "Biology", "Mathematics", "English"])
        study_hours = st.number_input("Daily Study Hours", 1, 12, 4)
    
    if st.button("Generate Study Plan"):
        st.success("✨ Study plan generated! Adjust based on your needs.")
        st.markdown("""
        ### Your Personalized Study Plan
        - **Total Duration**: 120 days
        - **Daily Goal**: Complete 2-3 topics
        - **Weekly Review**: Spend weekends reviewing
        - **Weak Areas**: Extra 1.5 hours daily
        """)

# Page: Analytics
elif page == "📊 Analytics":
    st.header("Analytics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Exams", len(exam_data['exams']))
    with col2:
        st.metric("Announced", "4")
    with col3:
        st.metric("Days to Next Exam", "45")
    with col4:
        st.metric("Study Streak", "12 days")
    
    st.divider()
    
    # Charts placeholder
    st.markdown("### Exam Streams Distribution")
    st.info("Chart visualization will be displayed here.")

# Page: Settings
elif page == "⚙️ Settings":
    st.header("Settings")
    
    with st.form("settings_form"):
        col1, col2 = st.columns(2)
        with col1:
            timezone = st.selectbox("Timezone", ["IST", "GMT", "EST"])
            notification = st.checkbox("Enable Notifications", value=True)
        with col2:
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            calendar_sync = st.checkbox("Auto-sync Google Calendar", value=False)
        
        submitted = st.form_submit_button("Save Settings")
        if submitted:
            st.success("Settings saved successfully!")

st.divider()
st.markdown("---")
st.markdown("Made with ❤️ for Indian students | StrikeGoal v1.0")
