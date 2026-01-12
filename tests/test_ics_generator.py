
import pytest
import pandas as pd
from datetime import datetime
from utils.ics_generator import generate_ics

def test_generate_ics_content():
    # Create valid dataframe for testing
    data = {
        'Date': [datetime.now().strftime('%Y-%m-%d')],
        'Subject': ['Physics'],
        'Chapter': ['Kinematics'],
        'Focus': ['Theory'],
        'Weightage': ['High']
    }
    df = pd.DataFrame(data)
    
    ics_output = generate_ics(df, "Test-Exam")
    
    assert isinstance(ics_output, str)
    assert "BEGIN:VCALENDAR" in ics_output
    assert "END:VCALENDAR" in ics_output
    assert "SUMMARY:Physics: Kinematics (Theory)" in ics_output

def test_generate_ics_empty():
    df = pd.DataFrame()
    ics_output = generate_ics(df, "Test-Exam")
    
    assert "BEGIN:VCALENDAR" in ics_output
    assert "END:VCALENDAR" in ics_output
    # Should be no events
    assert "BEGIN:VEVENT" not in ics_output
