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
        self.today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
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
                # Default to 1st of the month
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
            base_path = os.path.dirname(os.path.dirname(__file__))
            data_path = os.path.join(base_path, 'data', 'syllabus.json')
            
            if not os.path.exists(data_path):
                # Fallback: empty syllabus or maybe load a default one
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

        # Flatten all chapters into a single list
        all_chapters = []
        
        # Determine Strategy
        if days_remaining > 180:
            self.strategy_mode = "Long Term (Detailed)"
            allowed_weightages = ['High', 'Medium', 'Low']
        else:
            self.strategy_mode = "Short Term (Crunch)"
            # valid_weightages logic: In crunch mode, we prioritize High, but we MUST cover everything 
            # if the user asked for it. 
            # For now, let's include EVERYTHING but sort by weightage so low priority stuff 
            # gets pushed to the end or doubled up.
            allowed_weightages = ['High', 'Medium', 'Low'] 
            
        for subject, chapters in self.syllabus.items():
            if self.subjects and subject not in self.subjects:
                continue
                
            for chapter in chapters:
                weightage = chapter.get('weightage', 'Low')
                
                # Add metadata
                chapter_data = chapter.copy()
                chapter_data['subject'] = subject
                
                # Weightage score for sorting
                weight_map = {'High': 3, 'Medium': 2, 'Low': 1}
                w_score = weight_map.get(weightage, 1)
                
                chapter_data['priority_score'] = w_score
                all_chapters.append(chapter_data)
        
        # Sort by priority (descending) so high weightage comes first
        all_chapters.sort(key=lambda x: x['priority_score'], reverse=True)
        
        if not all_chapters:
             return {"error": "No chapters found for the selected subjects."}

        schedule = []
        current_date = self.today
        
        # Scheduling Logic: "Crunch Mode"
        # We must fit `len(all_chapters)` into `days_remaining`.
        # Ensure at least 1 chapter per day.
        
        # Calculate chapters needed per day (ceil)
        import math
        chapters_per_day = math.ceil(len(all_chapters) / days_remaining)
        
        chapter_idx = 0
        while chapter_idx < len(all_chapters):
            # If we passed exam date, we must double up on the last day or just keep adding to the list 
            # (which implies >1 chapter/day effectively, but let's try to keep dates valid)
            
            if current_date >= self.exam_date:
                # Fallback: Schedule everything remaining on the last possible study day (yesterday)
                # or just cap it. Let's stack them on the last day - 1
                current_date = self.exam_date - timedelta(days=1)
                if current_date < self.today:
                    current_date = self.today # Should not happen if days_remaining > 0

            # Schedule N chapters for this day
            for _ in range(chapters_per_day):
                if chapter_idx >= len(all_chapters):
                    break
                    
                daily_task = all_chapters[chapter_idx]
                schedule.append({
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Day": current_date.strftime("%A"),
                    "Subject": daily_task['subject'],
                    "Chapter": daily_task['name'],
                    "Weightage": daily_task.get('weightage', 'Low'),
                    "Focus": "Deep Study" if daily_task.get('weightage') == 'High' else "Review"
                })
                chapter_idx += 1
            
            # Move to next day
            current_date += timedelta(days=1)

        return pd.DataFrame(schedule)

    def generate_ai_strategy(self, api_key, plan_df):
        """
        Generate a personalized strategy using Google Gemini.
        """
        try:
            genai.configure(api_key=api_key)
            # Use a more available model or make it configurable
            # gemini-1.5-flash is often the new standard for fast tasks
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            model = genai.GenerativeModel(model_name)
            
            # Construct Prompt
            days = plan_df['Date'].nunique() if not plan_df.empty else 0
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
            2. Explain why the "{self.strategy_mode}" approach was chosen.
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
