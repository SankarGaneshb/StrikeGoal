from duckduckgo_search import DDGS
import google.generativeai as genai
import json
import datetime

class ExamScoutAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    def scan_exam(self, exam_name, current_date=None):
        """
        Search for updates for a specific exam.
        Returns a dict with found info or None.
        """
        if not self.api_key:
            return {"error": "API Key missing"}

        print(f"Scouting for: {exam_name}")
        current_year = datetime.datetime.now().year
        # Search for current year exams too, especially early in the year
        query = f"{exam_name} exam date {current_year} {current_year + 1} official notification"
        
        try:
            # 1. Search Web
            results = DDGS().text(query, max_results=5)
            if not results:
                return {"status": "no_results", "message": "No recent news found."}
                
            snippets = "\n\n".join([f"Source: {r['title']}\nSnippet: {r['body']}\nLink: {r['href']}" for r in results])
            
            # 2. Extract with Gemini
            prompt = f"""
            You are an Exam Data Scout. Analyze these search results for the exam "{exam_name}".
            Current Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
            Current Data on file: {current_date if current_date else "Unknown"}
            
            Search Results:
            {snippets}
            
            Task:
            Identify the OFFICIAL Exam Date for the upcoming session (likely {current_year} or {current_year + 1}).
            If there are multiple specific dates (e.g., "21, 22, 23..."), list ALL of them explicitly. Do NOT summarize as a range (e.g., "21-30") if gaps exist.
            
            Output JSON only:
            {{
                "found": true/false,
                "exam_date": "Exact string from source (e.g., 'January 21, 22, 23, 24, 28, 2026')",
                "source_link": "URL of most reliable source",
                "status": "Official" or "Tentative" or "predicted",
                "summary": "One sentence summary"
            }}
            """
            
            response = self.model.generate_content(prompt)
            # clean json
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            
            return data
            
        except Exception as e:
            return {"error": str(e)}

def update_exam_database(updates_list):
    """
    Update the JSON database with new info.
    updates_list: List of dicts with 'Exam' and 'New Date' keys.
    """
    try:
        import os
        base_path = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(base_path, 'data', 'exam_dates.json')
        
        with open(data_path, 'r') as f:
            data = json.load(f)
            
        updated_count = 0
        for update in updates_list:
            name = update.get('Exam')
            new_date = update.get('New Date')
            source = update.get('Source')
            
            # Find and update
            for exam in data['exams']:
                if exam.get('exam_name') == name or exam.get('name') == name:
                    exam['exam_date'] = new_date
                    exam['source_link'] = source
                    exam['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d')
                    updated_count += 1
                    break
        
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True, f"Updated {updated_count} exams successfully."
    except Exception as e:
        return False, str(e)
