
import json
import os

exam_file = 'data/exam_dates.json'
syllabus_file = 'data/syllabus.json'

# Review Templates
templates = {
    # Engineering: Physics, Chemistry, Maths
    "Engineering": {
        "Physics": [
            {"name": "Mechanics", "weightage": "High", "time_required": 4},
            {"name": "Electromagnetism", "weightage": "High", "time_required": 3},
            {"name": "Optics & Thermodynamics", "weightage": "Medium", "time_required": 3}
        ],
        "Chemistry": [
            {"name": "Physical Chemistry", "weightage": "High", "time_required": 3},
            {"name": "Organic Chemistry", "weightage": "High", "time_required": 4},
            {"name": "Inorganic Chemistry", "weightage": "Medium", "time_required": 2}
        ],
        "Mathematics": [
            {"name": "Calculus", "weightage": "High", "time_required": 5},
            {"name": "Algebra", "weightage": "High", "time_required": 4},
            {"name": "Coordinate Geometry", "weightage": "Medium", "time_required": 3}
        ]
    },
    # Medical: Physics, Chemistry, Biology
    "Medical": {
        "Physics": [
            {"name": "Mechanics", "weightage": "High", "time_required": 4},
            {"name": "Electrodynamics", "weightage": "High", "time_required": 3}
        ],
        "Chemistry": [
            {"name": "Organic Chemistry", "weightage": "High", "time_required": 4},
            {"name": "Inorganic Chemistry", "weightage": "Medium", "time_required": 3}
        ],
        "Biology": [
            {"name": "Human Physiology", "weightage": "High", "time_required": 5},
            {"name": "Genetics", "weightage": "High", "time_required": 4},
            {"name": "Plant Physiology", "weightage": "Medium", "time_required": 3}
        ]
    },
    # Law/Management/General: Aptitude based
    "Aptitude": {
        "Quantitative Aptitude": [
            {"name": "Arithmetic", "weightage": "High", "time_required": 3},
            {"name": "Algebra & Geometry", "weightage": "Medium", "time_required": 2},
            {"name": "Data Interpretation", "weightage": "High", "time_required": 3}
        ],
        "Logical Reasoning": [
            {"name": "Analytical Reasoning", "weightage": "High", "time_required": 2},
            {"name": "Critical Reasoning", "weightage": "Medium", "time_required": 2}
        ],
        "English": [
            {"name": "Reading Comprehension", "weightage": "High", "time_required": 3},
            {"name": "Grammar & Vocabulary", "weightage": "Medium", "time_required": 2}
        ],
        "General Knowledge": [
            {"name": "Current Affairs", "weightage": "High", "time_required": 2},
            {"name": "Static GK", "weightage": "Low", "time_required": 2}
        ]
    },
    # Design: Creative based
    "Design": {
        "Creative Ability": [
            {"name": "Visualization & Spatial Ability", "weightage": "High", "time_required": 4},
            {"name": "Observation & Design Sensitivity", "weightage": "High", "time_required": 3}
        ],
        "General Ability": [
            {"name": "Quantitative Ability", "weightage": "Medium", "time_required": 2},
            {"name": "Communication Ability", "weightage": "Medium", "time_required": 2},
            {"name": "English Comprehension", "weightage": "Medium", "time_required": 2}
        ]
    }
}

# Stream Mapping
stream_map = {
    "Engineering": "Engineering",
    "Medical": "Medical",
    "Law": "Aptitude",
    "Management": "Aptitude",
    "General": "Aptitude",
    "Design": "Design",
    "Hotel Management": "Aptitude",
    "Civil Services": "Aptitude" # Simplified for UPSC Prelims (General Studies + CSAT)
}

try:
    # Load Exams
    with open(exam_file, 'r') as f:
        exams_data = json.load(f)
    
    # Load Existing Syllabus
    if os.path.exists(syllabus_file):
        with open(syllabus_file, 'r') as f:
            syllabus_data = json.load(f)
    else:
        syllabus_data = {}

    count = 0
    for exam in exams_data['exams']:
        name = exam['exam_name']
        stream = exam.get('stream', 'General')
        
        # Skip if already exists (preserve custom data like JEE/NEET)
        if name in syllabus_data:
            continue
            
        template_key = stream_map.get(stream, "Aptitude")
        if template_key in templates:
            syllabus_data[name] = templates[template_key]
            count += 1
            print(f"Added syllabus for {name} ({template_key})")
    
    # Write back
    with open(syllabus_file, 'w') as f:
        json.dump(syllabus_data, f, indent=4)
        
    print(f"\nSuccessfully populated syllabus for {count} exams.")

except Exception as e:
    print(f"Error: {e}")
