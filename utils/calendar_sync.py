import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

# Scopes
# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/tasks'
]

def get_credentials():
    """
    Get valid user credentials from storage or run authentication flow.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # We need credentials.json from the user
            if not os.path.exists('credentials.json'):
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

def sync_to_google_calendar(plan_df, calendar_id='primary'):
    """
    Sync items from plan_df to Google Calendar as All-Day Events.
    """
    creds = get_credentials()
    if not creds:
        return {"status": "error", "message": "credentials.json not found or auth failed."}

    try:
        service = build('calendar', 'v3', credentials=creds)
        
        count = 0
        for _, row in plan_df.iterrows():
            date_str = row['Date'] # YYYY-MM-DD
            subject = row.get('Subject', 'Study')
            chapter = row.get('Chapter', 'Topic')
            weightage = row.get('Weightage', 'Low')
            
            # Color ID: 11 (Red) for High, 5 (Yellow) for Medium, 9 (Blue) for Low
            # See https://lukeboyle.com/blog-posts/2016/04/google-calendar-api-color-id
            color_id = '9' 
            if weightage == 'High': color_id = '11'
            if weightage == 'Medium': color_id = '5'
            
            event = {
                'summary': f"📚 {subject}: {chapter}",
                'description': f"Focus: {row.get('Focus', 'Study')}\nWeightage: {weightage}",
                'start': {
                    'date': date_str,
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'date': date_str,
                    'timeZone': 'Asia/Kolkata', 
                },
                'colorId': color_id,
                'transparency': 'transparent', # Show as 'Available' so it doesn't block meetings
            }

            try:
                service.events().insert(calendarId=calendar_id, body=event).execute()
                count += 1
            except Exception as loop_e:
                print(f"Failed to add event for {date_str}: {loop_e}")
                
        return {"status": "success", "message": f"Successfully added {count} events to Calendar."}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def sync_to_google_tasks(plan_df, task_list_name="StrikeGoal Plan"):
    """
    Sync items from plan_df to a Google Task list.
    """
    creds = get_credentials()
    if not creds:
        # Check if credentials.json exists to give a more specific error
        if not os.path.exists('credentials.json'):
            return {
                "status": "error", 
                "message": "Configuration Missing: 'credentials.json' not found. Please download it from Google Cloud Console and place it in the project root."
            }
        return {"status": "error", "message": "Authentication failed. Please check your Google API credentials."}

    try:
        service = build('tasks', 'v1', credentials=creds)

        # 1. Create or Find Task List
        tasklists = service.tasklists().list().execute()
        target_list_id = None
        
        for tl in tasklists.get('items', []):
            if tl['title'] == task_list_name:
                target_list_id = tl['id']
                break
        
        if not target_list_id:
            new_list = service.tasklists().insert(body={'title': task_list_name}).execute()
            target_list_id = new_list['id']

        # 2. Add Tasks
        count = 0
        total = len(plan_df)
        
        for _, row in plan_df.iterrows():
            date_str = row['Date'] # String 'YYYY-MM-DD'
            subject = row.get('Subject', '')
            chapter = row.get('Chapter', '')
            
            # ISO 8601 timestamp for due date (RFC 3339)
            # Google Tasks due date is T00:00:00.000Z
            due_date = f"{date_str}T00:00:00.000Z"
            
            task_body = {
                'title': f"{subject}: {chapter}",
                'notes': f"Focus: {row.get('Focus', 'Study')}",
                'due': due_date
            }
            
            service.tasks().insert(tasklist=target_list_id, body=task_body).execute()
            count += 1
            
        return {"status": "success", "message": f"Successfully added {count} tasks to '{task_list_name}'"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_google_tasks_streak(prefix="SG:"):
    """
    Calculate the current study streak (consecutive days with completed tasks).
    Look for task lists starting with 'prefix' (default 'SG:' for StrikeGoal).
    """
    creds = get_credentials()
    if not creds:
        return 0 # No credentials, no streak
        
    try:
        service = build('tasks', 'v1', credentials=creds)
        
        # 1. Find relevant task lists
        tasklists = service.tasklists().list().execute()
        relevant_list_ids = []
        for tl in tasklists.get('items', []):
            if tl['title'].startswith(prefix):
                relevant_list_ids.append(tl['id'])
                
        if not relevant_list_ids:
            return 0
            
        # 2. Fetch completed tasks from all lists
        completed_dates = set()
        for list_id in relevant_list_ids:
            # We want completed tasks. showCompleted=True, showHidden=True
            results = service.tasks().list(
                tasklist=list_id, 
                showCompleted=True, 
                showHidden=True,
                maxResults=100
            ).execute()
            
            tasks = results.get('items', [])
            for task in tasks:
                if task['status'] == 'completed' and 'completed' in task:
                    # Parse timestamp (YYYY-MM-DD...)
                    comp_date_str = task['completed'][:10]
                    completed_dates.add(comp_date_str)
                    
        # 3. Calculate Streak
        if not completed_dates:
            return 0
            
        sorted_dates = sorted([datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in completed_dates], reverse=True)
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        if sorted_dates[0] < yesterday:
            return 0
            
        streak = 0
        current_check = today
        if sorted_dates[0] != today:
             current_check = yesterday
             
        date_set = set(sorted_dates)
        while current_check in date_set:
            streak += 1
            current_check -= datetime.timedelta(days=1)
            
        return streak
        
    except Exception as e:
        print(f"Error calculating streak: {e}")
        return 0
