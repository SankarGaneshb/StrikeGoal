from datetime import datetime, timedelta
import json

def generate_study_plan(exam_name, exam_date, target_score, weak_subjects=None, daily_hours=4):
    """
    Generate a personalized study plan based on exam parameters.
    
    Args:
        exam_name: Name of the exam
        exam_date: Date of exam in YYYY-MM-DD format
        target_score: Target score percentage (0-100)
        weak_subjects: List of weak subjects
        daily_hours: Daily study hours available
    
    Returns:
        dict: Personalized study plan
    """
    try:
        exam_dt = datetime.strptime(exam_date, '%Y-%m-%d')
        days_remaining = (exam_dt - datetime.now()).days
        
        if days_remaining <= 0:
            return {'error': 'Exam date has already passed'}
        
        total_hours = days_remaining * daily_hours
        
        plan = {
            'exam_name': exam_name,
            'exam_date': exam_date,
            'days_remaining': days_remaining,
            'target_score': target_score,
            'total_study_hours': total_hours,
            'daily_hours': daily_hours,
            'weak_subjects': weak_subjects or [],
            'timeline': generate_timeline(days_remaining, weak_subjects),
            'milestones': generate_milestones(days_remaining),
            'weekly_goals': generate_weekly_goals(days_remaining, weak_subjects, daily_hours)
        }
        return plan
    except ValueError as e:
        return {'error': f'Invalid date format: {str(e)}'}

def generate_timeline(days_remaining, weak_subjects=None):
    """
    Generate a study timeline broken into phases.
    """
    weak_subjects = weak_subjects or []
    phases = []
    
    if days_remaining > 90:
        phases.append({
            'phase': 'Fundamentals',
            'duration': '30 days',
            'focus': 'Build strong foundation in all subjects',
            'activities': ['Read textbooks', 'Understand concepts', 'Make notes']
        })
    
    if days_remaining > 45:
        phases.append({
            'phase': 'Practice',
            'duration': '30 days',
            'focus': 'Solve practice problems and previous papers',
            'activities': ['Problem solving', 'Topic tests', 'Analysis']
        })
    
    phases.append({
        'phase': 'Revision & Refinement',
        'duration': f'{min(days_remaining, 30)} days',
        'focus': 'Revise all topics with special attention to weak areas',
        'weak_areas_emphasis': weak_subjects,
        'activities': ['Review', 'Mock tests', 'Weak subject focus']
    })
    
    return phases

def generate_milestones(days_remaining):
    milestones = []
    intervals = [days_remaining // 4, days_remaining // 2, 3 * days_remaining // 4, days_remaining]
    
    for i, days in enumerate(intervals, 1):
        milestone_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        milestones.append({
            'milestone': f'Checkpoint {i}',
            'target_date': milestone_date,
            'description': f'Complete {i * 25}% of revision',
            'action_items': ['Take mock test', 'Review progress', 'Adjust strategy']
        })
    
    return milestones

def generate_weekly_goals(days_remaining, weak_subjects=None, daily_hours=4):
    weak_subjects = weak_subjects or []
    weeks = (days_remaining + 6) // 7
    weekly_goals = []
    
    for week in range(1, min(weeks + 1, 17)):
        extra_hours = 2 if weak_subjects else 0
        goal = {
            'week': week,
            'total_hours': daily_hours * 7,
            'extra_focus_hours': extra_hours * 7,
            'focus_areas': weak_subjects if week <= 2 or week >= weeks - 2 else [],
            'deliverables': ['Complete assigned topics', 'Solve practice problems', 'Weekly mock test', 'Review and consolidate']
        }
        weekly_goals.append(goal)
    
    return weekly_goals
