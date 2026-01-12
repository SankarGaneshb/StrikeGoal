
import pytest
from datetime import datetime, timedelta
import pandas as pd
from utils.study_planner import StudyPlannerAgent


def test_planner_initialization():
    agent = StudyPlannerAgent("JEE (Main)", "2026-01-01")
    assert agent.exam_name == "JEE (Main)"
    assert agent.exam_date == datetime(2026, 1, 1)

def test_planner_invalid_date():
    # Should handle invalid date gracefully or default to something safe, 
    # but based on current implementation it might print error and set None
    agent = StudyPlannerAgent("JEE (Main)", "Invalid-Date")
    assert agent.exam_date is None

def test_generate_plan_structure():
    # Future date to ensure we have days to plan
    future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    agent = StudyPlannerAgent("JEE (Main)", future_date)
    plan = agent.generate_plan()
    
    assert isinstance(plan, pd.DataFrame)
    assert not plan.empty
    expected_cols = ['Date', 'Subject', 'Chapter', 'Weightage', 'Focus']
    for col in expected_cols:
        assert col in plan.columns

def test_generate_plan_short_duration():
    # Very short duration might fail or return empty if logic is strict, 
    # or just return few items.
    future_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    agent = StudyPlannerAgent("JEE (Main)", future_date)
    plan = agent.generate_plan()

    
    # Depending on logic, it might be a dict with error or a small dataframe
    if isinstance(plan, dict):
        assert "error" in plan
    else:
        assert isinstance(plan, pd.DataFrame)
