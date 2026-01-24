import pytest
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def mock_genai(monkeypatch):
    """
    Mock Google Generative AI to prevent actual API calls during tests.
    """
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "Mocked Strategy Strategy"
    
    mock_genai_mod = MagicMock()
    mock_genai_mod.GenerativeModel.return_value = mock_model
    
    monkeypatch.setattr("utils.study_planner.genai", mock_genai_mod)

@pytest.fixture(autouse=True)
def cleanup_artifacts():
    """
    Ensure no debug files are left over.
    """
    yield
    if os.path.exists("test_output.txt"):
        try:
            os.remove("test_output.txt")
        except:
            pass
