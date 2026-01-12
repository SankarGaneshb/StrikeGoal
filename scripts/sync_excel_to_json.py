import pandas as pd
import json
import os
import re

def infer_stream(courses_text):
    if not isinstance(courses_text, str):
        return "General"
    text = courses_text.lower()
    if any(x in text for x in ['engineering', 'tech', 'b.e', 'b.tech', 'architecture', 'planning']):
        return "Engineering"
    if any(x in text for x in ['medical', 'mbbs', 'bds', 'nursing', 'pharmacy']):
        return "Medical"
    if any(x in text for x in ['law', 'llb']):
        return "Law"
    if any(x in text for x in ['design', 'fashion', 'nift']):
        return "Design"
    if any(x in text for x in ['hotel', 'hospitality']):
        return "Hotel Management"
    return "General"

def clean_date(date_obj):
    if pd.isna(date_obj):
        return None
    return str(date_obj).strip()

def main():
    excel_path = 'data/National and State Level Entrance Examinations for UG Admissions.xlsx'
    json_path = 'data/exam_dates.json'
    
    print(f"Reading from {excel_path}...")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    exams = []
    print(f"Found {len(df)} rows in Excel.")

    for _, row in df.iterrows():
        exam = {
            "exam_name": row.get("Examination Name"),
            "level": "National", # Defaulting to National as per observed data
            "stream": infer_stream(row.get("Admitting Institutions / Courses")),
            "exam_date": clean_date(row.get("Exam Date (2025-26)")),
            "registration_start": None,
            "registration_end": None,
            "source": str(row.get("Source")) if not pd.isna(row.get("Source")) else None
        }
        exams.append(exam)
    
    output = {"exams": exams}
    
    print(f"Writing {len(exams)} exams to {json_path}...")
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=4)
    print("Sync complete.")

if __name__ == "__main__":
    main()
