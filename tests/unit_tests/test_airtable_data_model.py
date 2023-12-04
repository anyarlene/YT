import unittest
from airtable_data_model import AirtableDataModel
from unittest.mock import patch, MagicMock

class TestAirtableDataModel(unittest.TestCase):
    
    @patch('airtable_data_model.requests.post')
    def test_post_record(self, mock_post):
        # Setup mock response
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {'id': 'record_id'})

        # Test
        airtable_data_model = AirtableDataModel()
        response = airtable_data_model.post_record({'fields': {}})
        self.assertEqual(response.status_code, 200)

    @patch('airtable_data_model.requests.patch')
    def test_update_record(self, mock_patch):
        # Setup mock response
        mock_patch.return_value = MagicMock(status_code=200)

        # Test
        airtable_data_model = AirtableDataModel()
        response = airtable_data_model.update_record('record_id', {'fields': {}})
        self.assertEqual(response.status_code, 200)

    # Add more tests as needed

if __name__ == '__main__':
    unittest.main()
