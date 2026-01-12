from utils.study_planner import StudyPlannerAgent
from datetime import datetime, timedelta

# Mock Exam Date
exam_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')

print(f"Testing for Exam Date: {exam_date}")

# Test JEE-Main
agent = StudyPlannerAgent("JEE-Main", exam_date, weak_subjects=["Physics"])
plan = agent.generate_plan()

if "error" in plan:
    print(f"Error: {plan['error']}")
else:
    print("Success! Plan Generated.")
    print(plan.head())
    print("\nColumns:", plan.columns)
    
    # Check prioritization
    high_priority = plan[plan['Weightage'] == 'High']
    print(f"\nHigh Weightage Topics: {len(high_priority)}")
    print("First 3 topics:")
    print(plan[['Date', 'Subject', 'Chapter', 'Weightage']].head(3))

# Test Invalid Exam
agent_inv = StudyPlannerAgent("Unknown-Exam", exam_date)
res = agent_inv.generate_plan()
if "error" in res:
    print(f"\nCorrectly handled invalid exam: {res['error']}")
