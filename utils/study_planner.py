import json
import pandas as pd
from datetime import datetime, timedelta
import os
import re
from dateutil import parser as date_parser
import google.generativeai as genai

class StudyPlannerAgent:
    def __init__(self, exam_name, exam_date, subjects=None, target_year=None):
        self.exam_name = exam_name
        self.raw_date_str = exam_date
        self.subjects = subjects or []
        self.today = datetime.now()
        
        # Parse and Project Date
        parsed_date = self._parse_exam_date(exam_date)
        if parsed_date and target_year:
            # If target year is in the future relative to the parsed date, project it
            # e.g. Parsed 2026, Target 2027 -> Add 365 days usually, or just replace year
            # Simple projection: Replace year if valid
            if parsed_date.year < target_year:
                try:
                    parsed_date = parsed_date.replace(year=target_year)
                except ValueError:
                    # Leap year case (Feb 29 -> Mar 1)
                    parsed_date = parsed_date + timedelta(days=365)
        
        self.exam_date = parsed_date
        self.strategy_mode = "Standard"
        self.syllabus = self._load_syllabus()

    def _parse_exam_date(self, date_str):
        """
        Robustly extract the first valid date from a complex string.
        """
        if not date_str or "Not in source" in date_str:
            return None

        # 1. Try simple strict parse first
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pass
            
        # 2. Pattern 1: Day ... Month Year (e.g., "21-30 January 2026", "21 Jan 2026")
        # We look for a Day, optional range end, then Month and Year.
        # Regex explanation:
        # (\d{1,2})       : Capture Start Day
        # (?:[-–\s]+\d{1,2})? : Optional Range end (non-capturing), e.g. "-30"
        # \s+             : Space before month
        # ([A-Za-z]+)     : Capture Month
        # \s+             : Space
        # (\d{4})         : Capture Year
        
        match = re.search(r'(\d{1,2})(?:[-–\s]+\d{1,2})?\s+([A-Za-z]+)\s+(\d{4})', date_str)
        if match:
            d, m, y = match.groups()
            try:
                # Try full month name
                return datetime.strptime(f"{d} {m} {y}", "%d %B %Y")
            except ValueError:
                try:
                    # Try abbreviated month name
                    return datetime.strptime(f"{d} {m} {y}", "%d %b %Y")
                except ValueError:
                    pass

        # 3. Pattern 2: Month ... Year (e.g., "May 2026")
        match = re.search(r'([A-Za-z]+).*?(\d{4})', date_str)
        if match:
            m, y = match.groups()
            try:
                return datetime.strptime(f"1 {m} {y}", "%d %B %Y")
            except ValueError:
                try:
                    return datetime.strptime(f"1 {m} {y}", "%d %b %Y")
                except ValueError:
                    pass
        
        return None

    def _load_syllabus(self):
        try:
            # Assuming syllabus.json is in the data folder relative to project root
            # or same directory structure
            base_path = os.path.dirname(os.path.dirname(__file__))
            data_path = os.path.join(base_path, 'data', 'syllabus.json')
            
            if not os.path.exists(data_path):
                return {}
                
            with open(data_path, 'r') as f:
                data = json.load(f)
            
            return data.get(self.exam_name, {})
        except Exception as e:
            print(f"Error loading syllabus: {e}")
            return {}

    def generate_plan(self):
        if not self.syllabus:
            return {"error": "Syllabus not found for this exam."}
        
        if not self.exam_date:
            return {"error": f"Could not determine a valid exam date from: '{self.raw_date_str}'"}

        days_remaining = (self.exam_date - self.today).days
        if days_remaining <= 0:
            return {"error": "Exam date has already passed!"}

        # Flatten all chapters into a single list to prioritize and schedule
        all_chapters = []
        
        # Determine Strategy based on timeline
        # > 6 months (180 days) -> Detailed
        # <= 180 days -> Crunch (High Weightage only)
        if days_remaining > 180:
            self.strategy_mode = "Long Term (Detailed)"
            allowed_weightages = ['High', 'Medium', 'Low']
        else:
            self.strategy_mode = "Short Term (Crunch)"
            allowed_weightages = ['High'] # User requested ONLY high weightage for short term
            
        for subject, chapters in self.syllabus.items():
            # FILTER: If specific subjects selected, skip others
            if self.subjects and subject not in self.subjects:
                continue
                
            for chapter in chapters:
                # STRATEGY FILTER: Check weightage
                weightage = chapter.get('weightage', 'Low')
                if weightage not in allowed_weightages:
                    continue
                    
                # Add metadata
                chapter_data = chapter.copy()
                chapter_data['subject'] = subject
                
                # Weightage score for sorting
                weight_map = {'High': 3, 'Medium': 2, 'Low': 1}
                w_score = weight_map.get(weightage, 1)
                
                chapter_data['priority_score'] = w_score
                all_chapters.append(chapter_data)
        
        # Sort by priority (descending)
        all_chapters.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Scheduling Logic
        # We will allocate chapters to dates.
        # Simple algorithm: 1 chapter per day for now, or multiple if time permits. 
        # Ideally, we should sum 'time_required' and fit into 'days_remaining'.
        
        schedule = []
        current_date = self.today
        
        # If we have more chapters than days, we need to double up.
        # Ratio of chapters/days
        chapters_per_day = len(all_chapters) / max(1, days_remaining)
        
        # Simple Round-Robin iterator or linear assignment
        chapter_idx = 0
        while chapter_idx < len(all_chapters) and current_date < self.exam_date:
            # Determine how many chapters to schedule for this day
            # If ratio > 1, we might need 2 chapters some days
            
            # For simplicity in V1: Just take the next available chapter
            # In a real agent, this would be more complex balancing load
            
            daily_task = all_chapters[chapter_idx]
            
            schedule.append({
                "Date": current_date.strftime("%Y-%m-%d"),
                "Day": current_date.strftime("%A"),
                "Subject": daily_task['subject'],
                "Chapter": daily_task['name'],
                "Weightage": daily_task['weightage'],
                "Focus": "Deep Study" if daily_task['weightage'] == 'High' else "Review"
            })
            
            # Move to next chapter
            chapter_idx += 1
            
            # If we are falling behind schedule (too many chapters, too few days), 
            # maybe schedule another one same day?
            if chapters_per_day > 1.0 and chapter_idx < len(all_chapters):
                # Check if we should add another one today
                # Rudimentary check: "Start a second shift"
                 daily_task_2 = all_chapters[chapter_idx]
                 schedule.append({
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Day": current_date.strftime("%A"),
                    "Subject": daily_task_2['subject'],
                    "Chapter": daily_task_2['name'],
                    "Weightage": daily_task_2['weightage'],
                    "Focus": "Practice" # Second slot usually practice
                })
                 chapter_idx += 1

            current_date += timedelta(days=1)

        return pd.DataFrame(schedule)

    def generate_ai_strategy(self, api_key, plan_df):
        """
        Generate a personalized strategy using Google Gemini.
        """
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')  # Or gemini-pro if flash invalid
            
            # Construct Prompt
            days = plan_df['Date'].nunique()
            topics = len(plan_df)
            focus_subjects = ", ".join(self.subjects) if self.subjects else "All Subjects"
            
            prompt = f"""
            You are an expert Exam Strategy Coach for Indian Entrance Exams (JEE/NEET).
            
            Student Profile:
            - Exam: {self.exam_name}
            - Strategy Mode: {self.strategy_mode}
            - Days Remaining: {days}
            - Total Topics to Cover: {topics}
            - Focus Subjects: {focus_subjects}
            
            Task:
            1. Provide a concise 3-bullet point strategy to maximize their score.
            2. Explain why the "{self.strategy_mode}" approach was chosen (e.g. "Since you have >6 months..." or "Due to limited time...").
            3. Give one high-impact technical tip for the Focus Subjects.
            
            Output Format:
            **Strategic Brief**
            * [Point 1]
            * [Point 2]
            * [Point 3]
            
            **Expert Tip:** [Tip]
            """
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ **AI Coach Unavailable**: {str(e)}"
