
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Core_Brain.nlp_engine.nlp_engine import NLPEngine

class TestNLPEngineRobustness(unittest.TestCase):
    def setUp(self):
        # Prevent actual API calls during tests by default
        self.patcher = patch('requests.post')
        self.mock_post = self.patcher.start()
        self.engine = NLPEngine()
        
    def tearDown(self):
        self.patcher.stop()

    def test_init_default_model(self):
        """Test if default model is the supported one"""
        self.assertEqual(self.engine.model_name, "llama-3.1-8b-instant")
        
    def test_empty_messages(self):
        """Test handling of empty message list"""
        response = self.engine.call_groq_model([])
        self.assertIn("Error", response)
        self.assertIn("Invalid input", response)

    def test_api_success(self):
        """Test successful API response flow"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello user"}}]
        }
        self.mock_post.return_value = mock_response
        
        result = self.engine.call_groq_model([{"role": "user", "content": "hi"}])
        self.assertEqual(result, "Hello user")

    def test_api_401_auth_error(self):
        """Test handling of invalid API key (401)"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        self.mock_post.return_value = mock_response
        
        result = self.engine.call_groq_model([{"role": "user", "content": "hi"}])
        self.assertIn("Authentication Error", result)
        # Should not retry on 401
        self.assertEqual(self.mock_post.call_count, 1)

    def test_api_429_retry(self):
        """Test handling of rate limits (429) with retry"""
        # First 2 calls fail with 429, 3rd succeeds
        response_429 = MagicMock()
        response_429.status_code = 429
        
        response_200 = MagicMock()
        response_200.status_code = 200
        response_200.json.return_value = {"choices": [{"message": {"content": "Finally works"}}]}
        
        self.mock_post.side_effect = [response_429, response_429, response_200]
        
        # We mock time.sleep to avoid waiting in tests
        with patch('time.sleep'):
            result = self.engine.call_groq_model([{"role": "user", "content": "hi"}])
            
        self.assertEqual(result, "Finally works")
        self.assertEqual(self.mock_post.call_count, 3)

    def test_fallback_on_total_failure(self):
        """Test fallback mechanism when all retries fail"""
        # All calls raise Timeout
        self.mock_post.side_effect = Exception("Network Down")
        
        with patch('time.sleep'):
            result = self.engine.call_groq_model([{"role": "user", "content": "hi"}])
            
        # Should return one of the fallback strings
        self.assertTrue(any(x in result for x in ["trouble", "drifting", "scrambled"]))

if __name__ == '__main__':
    unittest.main()
