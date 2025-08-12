#!/usr/bin/env python3
"""
Live system test to reproduce the "query failed" issue.
This test uses the actual system components without mocks.
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import config
from rag_system import RAGSystem
from vector_store import VectorStore


class TestLiveSystem(unittest.TestCase):
    """Test the actual live system to reproduce issues"""

    def setUp(self):
        """Set up with actual system"""
        try:
            self.rag_system = RAGSystem(config)
        except Exception as e:
            self.fail(f"Failed to initialize RAG system: {e}")

    def test_vector_store_search_functionality(self):
        """Test if vector store search works at all"""
        try:
            # Test basic search on existing data
            results = self.rag_system.vector_store.search("machine learning")
            print(f"Search results: {results}")
            
            # Even if no results, should not error
            self.assertIsNotNone(results, "Search returned None")
            
            if results.error:
                print(f"Search error: {results.error}")
            
            print(f"Number of results: {len(results.documents)}")
            
        except Exception as e:
            self.fail(f"Vector store search failed with exception: {e}")

    def test_course_search_tool_execution(self):
        """Test CourseSearchTool execution"""
        try:
            result = self.rag_system.search_tool.execute(
                query="machine learning",
                course_name=None,
                lesson_number=None
            )
            print(f"CourseSearchTool result: {result}")
            
            # Should return a string, not raise an exception
            self.assertIsInstance(result, str, "CourseSearchTool should return string")
            
            # Check if it's an error message
            if "error" in result.lower() or "failed" in result.lower():
                print(f"CourseSearchTool returned error: {result}")
            
        except Exception as e:
            self.fail(f"CourseSearchTool execution failed: {e}")

    def test_ai_generator_with_tools(self):
        """Test AI generator with tool calling (will fail without valid API key)"""
        try:
            # This will likely fail with invalid API key, but we can see what happens
            response = self.rag_system.ai_generator.generate_response(
                query="What is machine learning?",
                tools=self.rag_system.tool_manager.get_tool_definitions(),
                tool_manager=self.rag_system.tool_manager
            )
            print(f"AI Generator response: {response}")
            
        except Exception as e:
            print(f"Expected failure with AI Generator (likely API key issue): {e}")
            # This is expected to fail without proper API key

    def test_system_configuration_issues(self):
        """Test configuration that might cause system failures"""
        print(f"MAX_RESULTS setting: {config.MAX_RESULTS}")
        print(f"ANTHROPIC_API_KEY set: {'Yes' if config.ANTHROPIC_API_KEY else 'No'}")
        print(f"ANTHROPIC_API_KEY length: {len(config.ANTHROPIC_API_KEY) if config.ANTHROPIC_API_KEY else 0}")
        print(f"CHROMA_PATH: {config.CHROMA_PATH}")
        print(f"EMBEDDING_MODEL: {config.EMBEDDING_MODEL}")
        
        # Check if ChromaDB has any data
        try:
            course_count = self.rag_system.vector_store.get_course_count()
            course_titles = self.rag_system.vector_store.get_existing_course_titles()
            print(f"Courses in database: {course_count}")
            print(f"Course titles: {course_titles}")
        except Exception as e:
            print(f"Error checking database contents: {e}")

    def test_rag_system_query_end_to_end(self):
        """Test end-to-end query processing"""
        try:
            print("Testing end-to-end query...")
            response, sources = self.rag_system.query("What is machine learning?")
            print(f"Response: {response}")
            print(f"Sources: {sources}")
            
            # Should return strings/lists, not raise exceptions
            self.assertIsInstance(response, str, "Response should be string")
            self.assertIsInstance(sources, list, "Sources should be list")
            
        except Exception as e:
            print(f"End-to-end query failed: {e}")
            # Don't fail the test, just report the error


if __name__ == '__main__':
    # Run with high verbosity to see all output
    unittest.main(verbosity=2)