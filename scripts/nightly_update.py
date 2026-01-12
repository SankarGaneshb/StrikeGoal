import pandas as pd
import json
import re
import os
from datetime import datetime

EXCEL_FILE = 'data/National and State Level Entrance Examinations for UG Admissions.xlsx'
JSON_FILE = 'data/exam_dates.json'

def parse_date(date_str):
    """
    Extracts the first valid date from a string like "21–30 January 2026" or "04 May 2026".
    Returns YYYY-MM-DD string or None.
    """
    if not isinstance(date_str, str):
        return None
    
    # Try to find date pattern like "21 January 2026" or "21-30 January 2026"
    # We will pick the start date
    
    # Match strings like "21 January 2026" or "02 April 2026"
    # Regex explanation:
    # (\d{1,2})  -> Day (1 or 2 digits)
    # [–-]?      -> Optional range separator (en-dash or hyphen)
    # \d{0,2}    -> Optional end day (ignored)
    # \s*        -> whitespace
    # ([A-Za-z]+)-> Month
    # \s*        -> whitespace
    # (\d{4})    -> Year
    
    pattern = r"(\d{1,2})(?:[–-]\d{1,2})?\s+([A-Za-z]+)\s+(\d{4})"
    match = re.search(pattern, date_str)
    
    if match:
        day, month, year = match.groups()
        date_string = f"{day} {month} {year}"
        try:
            dt = datetime.strptime(date_string, "%d %B %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
            
    return None

def infer_stream(text):
    text = str(text).lower()
    if 'engineering' in text or 'tech' in text or 'b.e' in text:
        return 'Engineering'
    if 'medical' in text or 'mbbs' in text or 'dental' in text:
        return 'Medical'
    if 'law' in text or 'llb' in text:
        return 'Law'
    if 'design' in text:
        return 'Design'
    if 'architecture' in text or 'b.arch' in text:
        return 'Architecture'
    if 'pharmacy' in text:
        return 'Pharmacy'
    if 'agriculture' in text:
        return 'Agriculture'
    return 'General'

def update_exams():
    print(f"Reading from {EXCEL_FILE}...")
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    new_exams = []
    
    for _, row in df.iterrows():
        exam_name = row.get('Examination Name')
        if not exam_name:
            continue
            
        date_str = row.get('Exam Date (2025-26)')
        exam_date = parse_date(date_str)
        
        # If no 2026 date found, skip or verify logic (user prompt implies pulling this data)
        # We will include it even if date is missing, labeled TBA? 
        # For calendar, we need a date. Let's start with only those having valid dates.
        if not exam_date:
            continue

        stream = infer_stream(row.get('Admitting Institutions / Courses', ''))
        
        exam_entry = {
            "exam_name": exam_name,
            "level": "National", # Defaulting as per plan
            "stream": stream,
            "exam_date": exam_date,
            "registration_start": None,
            "registration_end": None,
            "source": row.get('Source')
        }
        new_exams.append(exam_entry)

    print(f"Found {len(new_exams)} valid exams.")

    # Load existing
    existing_data = {"exams": []}
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            try:
                existing_data = json.load(f)
            except:
                pass
    
    # Merge strategy: Overwrite or Append?
    # User said "pull all the data", implying this is the source of truth.
    # But let's keep existing manual entries if they are distinct?
    # For now, let's append new ones if they don't exactly match name.
    
    existing_names = {e.get('exam_name') for e in existing_data['exams']}
    
    added_count = 0
    for exam in new_exams:
        if exam['exam_name'] not in existing_names:
            existing_data['exams'].append(exam)
            added_count += 1
        else:
            # Update existing?
            for i, e in enumerate(existing_data['exams']):
                if e.get('exam_name') == exam['exam_name']:
                    # Update fields
                    existing_data['exams'][i].update(exam)
                    break
    
    with open(JSON_FILE, 'w') as f:
        json.dump(existing_data, f, indent=4)
        
    print(f"Updated {JSON_FILE}. Added {added_count} new exams, updated others.")

if __name__ == "__main__":
    update_exams()
