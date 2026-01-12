from datetime import datetime
import pandas as pd

def generate_ics(plan_df, exam_name):
    """
    Generate an iCalendar (.ics) string from the study plan DataFrame.
    """
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//StrikeGoal//StudyPlanner//EN",
        f"X-WR-CALNAME:StrikeGoal - {exam_name}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    
    for _, row in plan_df.iterrows():
        try:
            # Parse Date
            if isinstance(row['Date'], str):
                date_str = row['Date']
            else:
                date_str = row['Date'].strftime('%Y-%m-%d')
                
            start_date = datetime.strptime(date_str, '%Y-%m-%d')
            # All day event: Value=DATE
            dt_start = start_date.strftime("%Y%m%d")
            
            # End date is exclusive in ICS for all-day events, so add 1 day
            # But simpler: just use DTSTART;VALUE=DATE
            
            subject = row.get('Subject', 'Study')
            chapter = row.get('Chapter', 'Topic')
            focus = row.get('Focus', 'Study')
            
            title = f"{subject}: {chapter} ({focus})"
            desc = f"Study Plan for {exam_name}\\nSubject: {subject}\\nTopic: {chapter}\\nFocus: {focus}"
            
            event = [
                "BEGIN:VEVENT",
                f"DTSTAMP:{timestamp}",
                f"DTSTART;VALUE=DATE:{dt_start}",
                f"SUMMARY:{title}",
                f"DESCRIPTION:{desc}",
                f"UID:{dt_start}-{subject.replace(' ', '')}-{chapter.replace(' ', '')}@strikegoal.app",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ]
            ics_content.extend(event)
        except Exception as e:
            print(f"Error creating event for row {row}: {e}")
            continue

    ics_content.append("END:VCALENDAR")
    return "\r\n".join(ics_content)
