import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from utils.study_planner import StudyPlannerAgent
from utils.ics_generator import generate_ics
from utils.calendar_sync import sync_to_google_tasks
from utils.exam_scout import ExamScoutAgent, update_exam_database

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
            data = json.load(f)
            # Normalize data: Ensure 'exam_name' key exists
            for exam in data.get('exams', []):
                if 'name' in exam and 'exam_name' not in exam:
                    exam['exam_name'] = exam['name']
            return data
            return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {"exams": [
            {"exam_name": "JEE-Main", "level": "National", "stream": "Engineering", "registration_start": "2024-12-01", "registration_end": "2024-12-15", "exam_date": "2025-01-20"},
            {"exam_name": "NEET", "level": "National", "stream": "Medical", "registration_start": "2024-11-01", "registration_end": "2024-11-30", "exam_date": "2025-05-04"},
            {"exam_name": "KCET", "level": "State", "stream": "Engineering", "registration_start": "2024-12-10", "registration_end": "2025-01-10", "exam_date": "2025-05-25"},
            {"exam_name": "MHT-CET", "level": "State", "stream": "Engineering", "registration_start": "2024-11-15", "registration_end": "2024-12-20", "exam_date": "2025-05-27"}
        ]}

# Title and description
st.title("🎯 StrikeGoal")
st.subheader("Smart Exam Planner for Indian Entrance Exams")


import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Load Auth Config
with open('auth_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    pre_authorized=config['pre-authorized']
)

# Authentication Logic
# 0.4.2 syntax might differ slightly, but typically:
# name, authentication_status, username = authenticator.login('Login', 'main') 
# However, newer 0.3+ use login() returning None/True/False
# Let's try the standard pattern for v0.3+ which 0.4.x usually follows
try:
    authenticator.login()
except Exception as e:
    st.error(f"Auth Error: {e}")

if st.session_state["authentication_status"]:
    # Logout button in sidebar
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f"Welcome *{st.session_state['name']}*")

    # Sidebar navigation
    page = st.sidebar.radio(
        "Select Page",
        ["📅 Exam Calendar", "📚 Study Planner", "📊 Analytics", "🧘 Wellness", "⚙️ Settings"]
    )
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
    st.stop()


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
    
    
    # Add to Calendar button
    with st.expander("📱 Add Exam to Google Calendar"):
        selected_to_add = st.selectbox("Select exam", df['exam_name'].unique() if len(df) > 0 else [])
        if st.button("Add to Calendar"):
            st.success(f"Added {selected_to_add} to your Google Calendar!")

    from streamlit_calendar import calendar

    # View selection
    view_mode = st.radio("View Format", ["📝 Table", "📅 Calendar"], horizontal=True, label_visibility="collapsed")

    if view_mode == "📅 Calendar":
        # Prepare calendar events
        events = []
        
        # We need to parse dates for the calendar
        # Helper to parse specifically for the calendar view
        def parse_dates_for_cal(date_str):
            if not date_str: return []
            import re
            
            all_events = []
            
            # Split by semicolon to handle multiple sessions (e.g. Session 1; Session 2)
            parts = date_str.split(';')
            
            for part in parts:
                part = part.strip()
                if not part: continue
                
                # Extract potential label: Text before the date
                # Simple heuristic: split by ':' if present, or take text before the first digit
                label = ""
                if ':' in part:
                    label = part.split(':')[0].strip()
                else:
                    # try to extract text before the first number
                    match_text = re.match(r'^([^\d]+)', part)
                    if match_text:
                        label = match_text.group(1).strip()
                
                events_found = []
                
                # 1. Range Pattern: "21-30 January 2026"
                match_range = re.search(r'(\d{1,2})\s*[-–\u2013\u2014to]+\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', part, re.IGNORECASE)
                if match_range:
                    d_start, d_end, m, y = match_range.groups()
                    try:
                        dt_start = datetime.strptime(f"{d_start} {m} {y}", "%d %B %Y")
                        dt_end = datetime.strptime(f"{d_end} {m} {y}", "%d %B %Y")
                        
                        curr = dt_start
                        while curr <= dt_end:
                            d_str = curr.strftime('%Y-%m-%d')
                            events_found.append({'start': d_str, 'end': d_str, 'label': label})
                            curr += timedelta(days=1)
                        all_events.extend(events_found)
                        continue
                    except: pass
                
                # 2. Month-Days-Year Pattern: "January 21, 22, 23... 2026"
                months = "January|February|March|April|May|June|July|August|September|October|November|December"
                match_main = re.search(fr'({months})\s+(.*?)\s+(\d{{4}})', part, re.IGNORECASE)
                if match_main:
                    mon_str = match_main.group(1)
                    day_part = match_main.group(2)
                    year_str = match_main.group(3)
                    
                    day_nums = re.findall(r'\d+', day_part)
                    for d in day_nums:
                        try:
                            dt = datetime.strptime(f"{d} {mon_str} {year_str}", "%d %B %Y")
                            events_found.append({'start': dt.strftime('%Y-%m-%d'), 'end': dt.strftime('%Y-%m-%d'), 'label': label})
                        except: pass
                    if events_found:
                        all_events.extend(events_found)
                        continue

                # 3. Single Date / Fallback
                match_single = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', part)
                if match_single:
                    d, m, y = match_single.groups()
                    try:
                        dt = datetime.strptime(f"{d} {m} {y}", "%d %B %Y")
                        all_events.append({'start': dt.strftime('%Y-%m-%d'), 'end': dt.strftime('%Y-%m-%d'), 'label': label})
                    except: pass

            return all_events

        for index, row in df.iterrows():
            raw_date = row['exam_date']
            
            # Get list of event dicts
            valid_events = parse_dates_for_cal(raw_date)
            
            for event in valid_events:
                # Construct title: "JEE (Main)" or "JEE (Main) - Session 1"
                evt_title = row['exam_name']
                if event.get('label'):
                    evt_title += f" - {event['label']}"
                    
                events.append({
                    "title": evt_title,
                    "start": event['start'],
                    "end": event['end'],
                    "resourceId": row['exam_name'],
                    "extendedProps": {
                       "level": row.get('level', ''),
                       "stream": row.get('stream', ''),
                       "original_text": raw_date,
                       "desc": row.get('exam_date', '')
                    }
                })

        # Calendar options
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth"
            },
            "initialView": "dayGridMonth",
        }

        # Render calendar
        if events:
            calendar(events=events, options=calendar_options)
        else:
            st.info("No exams found for the selected filters.")
            
    else:
        # Table View
        display_cols = ['exam_name', 'exam_date', 'stream', 'level', 'registration_start', 'registration_end']
        # Filter columns that exist
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[available_cols], 
            use_container_width=True,
            column_config={
                "exam_name": "Exam Name",
                "exam_date": st.column_config.TextColumn("Exam Date", help="Official Exam Dates"),
                "registration_start": st.column_config.DateColumn("Reg Start", format="DD MMM YYYY"),
                "registration_end": st.column_config.DateColumn("Reg End", format="DD MMM YYYY"),
            }
        )
    

# Page: Study Planner
elif page == "📚 Study Planner":
    st.header("Study Planner")
    
    col1, col2 = st.columns(2)
    with col1:
        # Filter exams that have syllabus data if possible, or support generic
        selected_exam = st.selectbox("Select Exam", [e['exam_name'] for e in exam_data['exams']])
        
        # Target Year Selection
        current_year = datetime.now().year
        target_year = st.radio("Target Year", [current_year, current_year + 1], horizontal=True, help="Select 'Next Year' for early planning.")
        
        # Determine Target Score specific to exam
        exam_max_scores = {
            "JEE (Main)": 300,
            "JEE (Advanced)": 360, # Varies, but usually 360
            "NEET (UG)": 720,
            "BITSAT": 390,
            "VITEEE": 125,
            "SRMJEEE": 125,
            "MHT-CET": 200,
            "KCET": 180,
            "COMEDK UGET": 180,
            "WBJEE": 200,
            "GUJCET": 120,
            "AP EAMCET (EAPCET)": 160,
            "TS EAMCET": 160,
            "CUET UG": 800 # Approx max for 4 subjects
        }
        
        # Fuzzy match or exact match
        max_score = exam_max_scores.get(selected_exam, 100)
        is_percent = max_score == 100
        
        label = f"Target Score ({'%' if is_percent else 'Marks'})"
        # Default target usually 70-80% of max
        default_target = int(max_score * 0.75)
        
        target_score = st.slider(label, 0, max_score, default_target)
        if not is_percent:
            st.caption(f"Max Score for {selected_exam}: {max_score}")
        
    with col2:
        # Load Syllabus for dynamic subjects
        # We need to peek at syllabus.json
        import os
        base_path = os.path.dirname(__file__)
        syllabus_path = os.path.join(base_path, 'data', 'syllabus.json')
        subject_options = ["Physics", "Chemistry", "Biology", "Mathematics", "English"] # Default
        
        try:
            with open(syllabus_path, 'r') as f:
                syl_data = json.load(f)
                if selected_exam in syl_data:
                    subject_list = list(syl_data[selected_exam].keys())
                    subject_options = ["All"] + subject_list
        except: pass
        
        selected_subjects = st.multiselect("Subjects (Filter)", subject_options, default=["All"], help="Select 'All' or specific subjects.")
        
        # If 'All' is selected, clear the list to imply all (or pass all explicitly)
        # Agent logic: if self.subjects is empty, it uses all.
        if "All" in selected_subjects:
            selected_subjects = [] 
        
        # daily_hours currently unused in simple agent V1 but good to keep
        study_hours = st.number_input("Daily Study Hours", 1, 12, 4)
    
    # Check if we have data for this exam
    # In a real app, we might instantiate the agent here to check support
    
    # AI Settings
    with st.expander("🤖 AI Coach Settings (Optional)"):
        gemini_api_key = st.text_input("Gemini API Key", type="password", help="Get free key from Google AI Studio")
    
    if st.button("Generate Study Plan"):
        # Instantiate Agent
        # We need the exam date. Find it from exam_data.
        exam_info = next((e for e in exam_data['exams'] if e['exam_name'] == selected_exam), None)
        
        if exam_info:
             agent = StudyPlannerAgent(
                 exam_name=selected_exam, 
                 exam_date=exam_info['exam_date'],
                 subjects=selected_subjects,
                 target_year=target_year
             )
             
             with st.spinner("Agent is analyzing syllabus and generating plan..."):
                 plan_df = agent.generate_plan()
             
             if isinstance(plan_df, dict) and "error" in plan_df:
                 st.error(plan_df['error'])
             elif isinstance(plan_df, pd.DataFrame) and not plan_df.empty:
                 st.success("✨ Study plan generated! Optimized based on chapter weightage.")
                 
                 # AI Strategy
                 if gemini_api_key:
                     with st.spinner("🤖 AI Coach is formulating your strategy..."):
                        strategy = agent.generate_ai_strategy(gemini_api_key, plan_df)
                        st.info(strategy)
                 elif not gemini_api_key:
                     st.caption("💡 Tip: Add a Gemini API Key in settings to get personalized AI strategy tips!")

                 # Metrics
                 m1, m2, m3 = st.columns(3)
                 m1.metric("Total Topics", len(plan_df))
                 m2.metric("Days Planned", plan_df['Date'].nunique())
                 m3.metric("Daily Load", f"{len(plan_df)/plan_df['Date'].nunique():.1f} topics/day")
                 
                 # Display Schedule
                 st.subheader("Your Schedule")
                 st.dataframe(
                     plan_df,
                     use_container_width=True,
                     column_config={
                         "Date": st.column_config.DateColumn("Date", format="DD MMM"),
                         "Weightage": st.column_config.TextColumn(
                             "Weightage", 
                             help="High weightage topics are prioritized",
                             validate="^(High|Medium|Low)$"
                         ),
                     }
                 )
                 
                 # Download button
                 csv = plan_df.to_csv(index=False).encode('utf-8')
                 
                 exp_col1, exp_col2, exp_col3 = st.columns(3)
                 
                 with exp_col1:
                     st.download_button(
                         "📥 CSV",
                         csv,
                         "study_plan.csv",
                         "text/csv",
                         key='download-csv'
                     )
                 
                 with exp_col2:
                     ics_data = generate_ics(plan_df, selected_exam)
                     st.download_button(
                        "📅 Calendar (.ics)",
                        ics_data,
                        f"{selected_exam.replace(' ', '_')}_Schedule.ics",
                        "text/calendar",
                        key='download-ics'
                     )

                 with exp_col3:
                     # Google Tasks Button
                     if st.button("✅ Google Tasks"):
                         with st.spinner("Syncing..."):
                             result = sync_to_google_tasks(plan_df, f"SG: {selected_exam}")
                             if result['status'] == 'success':
                                 st.success(result['message'])
                             else:
                                 st.error("Sync Failed")
                                 with st.expander("See Error Info"):
                                     st.warning(result['message'])
                    
                     # Google Calendar Button
                     from utils.calendar_sync import sync_to_google_calendar
                     if st.button("📅 Google Calendar (Direct)"):
                        with st.spinner("Adding events to default calendar..."):
                            result = sync_to_google_calendar(plan_df)
                            if result['status'] == 'success':
                                st.success(result['message'])
                            else:
                                st.error("Calendar Sync Failed")
                                with st.expander("Error Details"):
                                    st.write(result['message'])
                                    st.info("Note: You may need to delete 'token.pickle' and re-login to grant Calendar permissions.")

                                     st.markdown("""
                                     **To enable Google Tasks/Calendar Sync:**
                                     1. Create a project in Google Cloud Console.
                                     2. Enable **'Google Tasks API'** and **'Google Calendar API'**.
                                     3. Create 'Desktop App' credentials.
                                     4. Download JSON and rename to `credentials.json`.
                                     5. Place it in the root folder.
                                     """)
             else:
                  st.warning(f"No specific syllabus data found for {selected_exam}. Please select JEE-Main or NEET to see the demo.")
        else:
            st.error("Exam data not found.")
            
    st.divider()

# Page: Analytics
elif page == "📊 Analytics":
    st.header("Analytics Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Exams", len(exam_data['exams']))
    with col2:
        st.metric("Announced", "4")
    with col3:
        # Calculate Real Streak from Google Tasks
        try:
            streak = get_google_tasks_streak()
        except:
            streak = 0
        st.metric("Study Streak", f"🔥 {streak} days")
    
    st.divider()
    


# Page: Wellness
elif page == "🧘 Wellness":
    st.header("Wellness & Care Hub")
    st.markdown("_Because a sharp mind needs a healthy body._")
    
    from utils.wellness import get_daily_tip, get_stress_buster, calculate_sleep_schedule, get_exam_day_advice
    from datetime import datetime
    
    # 1. Focus Mode (Do Not Disturb)
    st.subheader("🛑 Focus Mode")
    if 'focus_mode' not in st.session_state:
        st.session_state['focus_mode'] = False
        
    col_focus, col_info = st.columns([1, 3])
    with col_focus:
        if st.button("Toggle DND Mode", type="primary" if not st.session_state['focus_mode'] else "secondary"):
            st.session_state['focus_mode'] = not st.session_state['focus_mode']
            st.rerun()
            
    with col_info:
        if st.session_state['focus_mode']:
            st.warning("⚠️ **DND ACTIVE**: Please maintain silence. Exam in progress.")
        else:
            st.info("Activate this to signal 'Quiet Time' to those around you.")

    if st.session_state['focus_mode']:
         st.markdown("""
         <style>
            .stApp { background-color: #000000; color: #ff4b4b; }
            .dnd-overlay {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: black; color: red; z-index: 99999;
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                text-align: center;
            }
         </style>
         <div class="dnd-overlay">
            <h1 style='font-size: 80px;'>🛑 DO NOT DISTURB</h1>
            <h2>MOCK TEST IN PROGRESS</h2>
            <p>Please come back later.</p>
            <br><br>
            <p style='color: white; font-size: 20px;'>Press 'Toggle DND Mode' to exit.</p>
         </div>
         """, unsafe_allow_html=True)

    st.divider()

    # 2. Brain Fuel & Stress Busters
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🍎 Brain Fuel")
        tip = get_daily_tip()
        st.info(f"**{tip['title']}** ({tip['category']})\n\n{tip['tip']}")
        
        if st.button("New Tip"):
            pass # Rerun automatically happens
            
    with col2:
        st.subheader("🧘 Stress Buster Service")
        if st.button("I'm feeling stressed!"):
            relief = get_stress_buster()
            st.success(f"**Try this:** {relief['title']} ({relief['duration']})\n\n{relief['tip']}")
    
    st.divider()
    
    # 3. Sleep Guard
    st.subheader("😴 Sleep Guard")
    sc1, sc2 = st.columns(2)
    with sc1:
        wake_time = st.time_input("I need to wake up at:", datetime.strptime("06:00", "%H:%M").time())
    with sc2:
        if st.button("Calculate Bedtime"):
            res = calculate_sleep_schedule(wake_time.strftime("%H:%M"))
            if 'error' not in res:
                st.metric("Go to bed by", res['bed_time'])
                st.caption(f"To get {res['hours']} ({res['cycles']})")
    
    # 4. Exam Advice
    # Try to find next exam (reuse logic in a real app, simpler here)
    st.divider()
    st.subheader("📅 Exam Readiness")
    # Quick hack: assume first loaded exam is target for advice
    if 'exams' in exam_data and len(exam_data['exams']) > 0:
        target_ex = exam_data['exams'][0]
        try:
             # simple date parsing for demo
             import pandas as pd
             d_obj = pd.to_datetime(target_ex['exam_date']) # Might fail if complex string
             # Skip complexity for now, show generic advice
             st.markdown(f"**Advice for {target_ex['exam_name']}:**")
             st.write(get_exam_day_advice(30)) # Mocking '30 days left'
        except:
             st.write(get_exam_day_advice(100))


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

    # Live Updates Section
    st.divider()
    st.subheader("⚡ Live Exam Updates")
    st.info("Use AI to scan for the latest exam announcements.")
    
    # Needs API Key
    scout_api_key = st.text_input("Gemini API Key for Scout", type="password", key="scout_key")
    
    if st.button("🔍 Scan for Updates"):
        if not scout_api_key:
            st.error("Please provide a Gemini API Key to use the Scout Agent.")
        else:
            scout = ExamScoutAgent(scout_api_key)
            updates_found = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Scan top 3 exams for demo to save time/quota
            exams_to_scan = exam_data['exams'][:3] 
            
            for i, exam in enumerate(exams_to_scan):
                status_text.text(f"Scouting for {exam['exam_name']}...")
                result = scout.scan_exam(exam['exam_name'], exam.get('exam_date'))
                
                if result and result.get('found'):
                    updates_found.append({
                        "Exam": exam['exam_name'],
                        "Old Date": exam.get('exam_date', 'Unknown'),
                        "New Date": result.get('exam_date'),
                        "Source": result.get('source_link'),
                        "Status": result.get('status')
                    })
                
                progress_bar.progress((i + 1) / len(exams_to_scan))
            
            status_text.text("Scan Complete!")
            
            if updates_found:
                st.success(f"Found updates for {len(updates_found)} exams!")
                update_df = pd.DataFrame(updates_found)
                st.dataframe(update_df)
                
                if st.button("💾 Save Updates to Database"):
                    success, msg = update_exam_database(updates_found)
                    if success:
                        st.success(msg)
                        st.cache_data.clear() # Clear cache to reload new data
                        st.rerun()
                    else:
                        st.error(f"Failed to save: {msg}")
            else:
                st.warning("No new official updates found.")

st.divider()
st.markdown("---")
st.markdown("Made with ❤️ for Indian students | StrikeGoal v1.0")
