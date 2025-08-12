import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import config


class TestConfigurationIssues(unittest.TestCase):
    """Test for configuration issues that might cause system failures"""

    def test_anthropic_api_key_present(self):
        """Test that Anthropic API key is configured"""
        self.assertIsNotNone(config.ANTHROPIC_API_KEY, "ANTHROPIC_API_KEY is not set")
        self.assertNotEqual(config.ANTHROPIC_API_KEY, "", "ANTHROPIC_API_KEY is empty")

    def test_max_results_configuration(self):
        """Test that MAX_RESULTS is properly configured"""
        # This is a critical bug - MAX_RESULTS is set to 0 in config.py
        self.assertGreater(config.MAX_RESULTS, 0, 
                          f"MAX_RESULTS is {config.MAX_RESULTS}, should be > 0 for search to work")

    def test_chunk_size_reasonable(self):
        """Test that chunk size is reasonable"""
        self.assertGreater(config.CHUNK_SIZE, 0, "CHUNK_SIZE must be positive")
        self.assertLess(config.CHUNK_SIZE, 10000, "CHUNK_SIZE seems too large")

    def test_chunk_overlap_reasonable(self):
        """Test that chunk overlap is reasonable"""
        self.assertGreaterEqual(config.CHUNK_OVERLAP, 0, "CHUNK_OVERLAP cannot be negative")
        self.assertLess(config.CHUNK_OVERLAP, config.CHUNK_SIZE, 
                       "CHUNK_OVERLAP should be less than CHUNK_SIZE")

    def test_model_name_format(self):
        """Test that model name follows expected format"""
        self.assertIsInstance(config.ANTHROPIC_MODEL, str, "Model name should be string")
        self.assertNotEqual(config.ANTHROPIC_MODEL, "", "Model name cannot be empty")
        # Should contain 'claude' in the name
        self.assertIn("claude", config.ANTHROPIC_MODEL.lower(), 
                     "Model name should contain 'claude'")

    def test_embedding_model_name(self):
        """Test embedding model configuration"""
        self.assertIsInstance(config.EMBEDDING_MODEL, str, "Embedding model should be string")
        self.assertNotEqual(config.EMBEDDING_MODEL, "", "Embedding model cannot be empty")

    def test_chroma_path_reasonable(self):
        """Test that ChromaDB path is reasonable"""
        self.assertIsInstance(config.CHROMA_PATH, str, "ChromaDB path should be string")
        self.assertNotEqual(config.CHROMA_PATH, "", "ChromaDB path cannot be empty")

    def test_max_history_reasonable(self):
        """Test that max history is reasonable"""
        self.assertGreaterEqual(config.MAX_HISTORY, 0, "MAX_HISTORY cannot be negative")
        self.assertLessEqual(config.MAX_HISTORY, 10, "MAX_HISTORY seems too large")


if __name__ == '__main__':
    unittest.main()