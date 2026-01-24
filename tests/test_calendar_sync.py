import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from utils.calendar_sync import sync_to_google_calendar

class TestCalendarSync(unittest.TestCase):
    
    @patch('utils.calendar_sync.get_credentials')
    @patch('utils.calendar_sync.build')
    def test_sync_success(self, mock_build, mock_get_creds):
        # Setup Mocks
        mock_creds = MagicMock()
        mock_get_creds.return_value = mock_creds
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        
        # Test Data
        plan_df = pd.DataFrame([
            {
                'Date': '2026-01-01', 
                'Subject': 'Physics', 
                'Chapter': 'Optics', 
                'Weightage': 'High',
                'Focus': 'Deep Study'
            },
            {
                'Date': '2026-01-02', 
                'Subject': 'Chem', 
                'Chapter': 'Atoms', 
                'Weightage': 'Low',
                'Focus': 'Review'
            }
        ])
        
        # Execute
        result = sync_to_google_calendar(plan_df)
        
        # Verify
        self.assertEqual(result['status'], 'success')
        self.assertEqual(mock_events.insert.call_count, 2)
        
        # Check Payload of first call
        args, kwargs = mock_events.insert.call_args_list[0]
        body = kwargs['body']
        
        self.assertEqual(body['summary'], '📚 Physics: Optics')
        self.assertEqual(body['colorId'], '11') # High weightage = Red
        self.assertEqual(body['start']['date'], '2026-01-01') # All day event
        self.assertTrue('transparency' in body)

    @patch('utils.calendar_sync.get_credentials')
    def test_sync_no_creds(self, mock_get_creds):
        mock_get_creds.return_value = None
        result = sync_to_google_calendar(pd.DataFrame([]))
        self.assertEqual(result['status'], 'error')
        self.assertIn("credentials.json not found", result['message'])

if __name__ == '__main__':
    unittest.main()
