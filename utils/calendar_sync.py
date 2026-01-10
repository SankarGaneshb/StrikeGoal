from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import json

def sync_to_google_calendar(exam_data, calendar_id=None):
    """
    Sync exam dates to Google Calendar.
    
    Args:
        exam_data: Dictionary containing exam information
        calendar_id: Google Calendar ID (uses primary if not specified)
    
    Returns:
        bool: True if sync successful
    """
    try:
        # Placeholder for Google Calendar API integration
        # In production, this would authenticate and add events
        print(f"Syncing {len(exam_data)} exams to Google Calendar")
        return True
    except Exception as e:
        print(f"Error syncing to calendar: {str(e)}")
        return False

def create_event(exam_name, exam_date, description=""):
    """
    Create a calendar event object.
    
    Args:
        exam_name: Name of the exam
        exam_date: Date of the exam (YYYY-MM-DD format)
        description: Event description
    
    Returns:
        dict: Event object for Google Calendar
    """
    event = {
        'summary': exam_name,
        'description': description,
        'start': {
            'date': exam_date,
        },
        'end': {
            'date': exam_date,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'notification', 'minutes': 24 * 60},  # 1 day before
                {'method': 'popup', 'minutes': 60},  # 1 hour before
            ],
        },
    }
    return event

def send_notifications(exam_data, days_before=1):
    """
    Send notifications for upcoming exams.
    
    Args:
        exam_data: List of exam dictionaries
        days_before: Send notifications this many days before
    
    Returns:
        list: Exams with upcoming notifications
    """
    today = datetime.now().date()
    upcoming = []
    
    for exam in exam_data:
        try:
            exam_date = datetime.strptime(exam.get('exam_date', ''), '%Y-%m-%d').date()
            if exam_date - today <= timedelta(days=days_before) and exam_date >= today:
                upcoming.append(exam)
        except ValueError:
            continue
    
    return upcoming
