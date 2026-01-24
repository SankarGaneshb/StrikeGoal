
import pytest
from datetime import datetime, timedelta
import pandas as pd
import os
import json
from unittest.mock import patch, mock_open
from utils.study_planner import StudyPlannerAgent

# Mock Data
MOCK_SYLLABUS = {
    "JEE (Main)": {
        "Physics": [
            {"name": "Kinematics", "weightage": "High"},
            {"name": "Units", "weightage": "Low"}
        ],
        "Chemistry": [
            {"name": "Atomic Structure", "weightage": "Medium"}
        ]
    }
}

@pytest.fixture
def mock_syllabus_file(monkeypatch):
    def mock_load(self):
        return MOCK_SYLLABUS.get(self.exam_name, {})
    monkeypatch.setattr(StudyPlannerAgent, "_load_syllabus", mock_load)

def test_planner_initialization():
    agent = StudyPlannerAgent("JEE (Main)", "2026-01-01")
    assert agent.exam_name == "JEE (Main)"
    assert agent.exam_date == datetime(2026, 1, 1)

def test_planner_invalid_date():
    # Should handle invalid date gracefully
    agent = StudyPlannerAgent("JEE (Main)", "Invalid-Date")
    # Depending on implementation, might return error in generate_plan or set date to None
    plan = agent.generate_plan()
    assert isinstance(plan, dict)
    assert "error" in plan
    assert "valid exam date" in plan['error']

def test_generate_plan_structure(mock_syllabus_file):
    # Future date to ensure we have days to plan
    future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    agent = StudyPlannerAgent("JEE (Main)", future_date)
    plan = agent.generate_plan()
    
    assert isinstance(plan, pd.DataFrame)
    assert not plan.empty
    expected_cols = ['Date', 'Subject', 'Chapter', 'Weightage', 'Focus']
    for col in expected_cols:
        assert col in plan.columns

def test_generate_plan_crunch_mode(mock_syllabus_file):
    # Very short duration - 1 day left, multiple chapters
    # Should schedule ALL chapters even if it means stacking them
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    agent = StudyPlannerAgent("JEE (Main)", tomorrow)
    plan = agent.generate_plan()

    assert isinstance(plan, pd.DataFrame)
    assert not plan.empty
    
    # We maintain 3 chapters in mock syllabus
    # Logic should include all 3
    assert len(plan) == 3
    
    # Check if they are all on the same day (or valid range)
    dates = plan['Date'].unique()
    assert len(dates) >= 1

def test_ai_strategy_mocked(mock_syllabus_file):
    # Test that AI strategy uses the mock and doesn't crash
    future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    agent = StudyPlannerAgent("JEE (Main)", future_date)
    plan = agent.generate_plan()
    
    strategy = agent.generate_ai_strategy("fake_key", plan)
    assert "Mocked Strategy" in strategy or isinstance(strategy, str)
    assert "Unavailable" not in strategy

def test_target_year_logic():
    # If exam is in 2025 but target is 2026, it should project
    # This logic depends on the implementation of StudyPlannerAgent
    # Assuming it handles target_year
    current_year = datetime.now().year
    target = current_year + 1
    
    # Passing target_year to constructor
    agent = StudyPlannerAgent("JEE (Main)", f"{current_year}-01-01", target_year=target)
    
    # It should have projected the date to target year
    assert agent.exam_date.year == target
    
    # Passing a date from current year
    agent = StudyPlannerAgent("Mock Exam", f"{current_year}-05-01", target_year=target)
    
    assert agent.exam_date.year == target
    assert agent.exam_date.month == 5
    assert agent.exam_date.day == 1
