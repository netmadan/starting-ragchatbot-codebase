import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock, patch
from search_tools import CourseSearchTool
from vector_store import VectorStore, SearchResults


class TestCourseSearchTool(unittest.TestCase):
    """Test cases for CourseSearchTool.execute method"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock vector store
        self.mock_vector_store = Mock(spec=VectorStore)
        self.search_tool = CourseSearchTool(self.mock_vector_store)

    def test_execute_successful_search(self):
        """Test successful search with results"""
        # Setup mock return value
        mock_results = SearchResults(
            documents=["Test content from lesson 1"],
            metadata=[{"course_title": "Test Course", "lesson_number": 1}],
            distances=[0.5],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        self.mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson1"

        # Execute search
        result = self.search_tool.execute(
            query="test query",
            course_name="Test Course",
            lesson_number=1
        )

        # Verify vector store was called correctly
        self.mock_vector_store.search.assert_called_once_with(
            query="test query",
            course_name="Test Course",
            lesson_number=1
        )

        # Verify result format
        self.assertIn("[Test Course - Lesson 1]", result)
        self.assertIn("Test content from lesson 1", result)
        
        # Verify sources were stored
        self.assertEqual(len(self.search_tool.last_sources), 1)
        self.assertEqual(self.search_tool.last_sources[0]["text"], "Test Course - Lesson 1")

    def test_execute_search_error(self):
        """Test handling of search errors"""
        # Setup mock to return error
        mock_results = SearchResults.empty("Database connection failed")
        self.mock_vector_store.search.return_value = mock_results

        # Execute search
        result = self.search_tool.execute(query="test query")

        # Verify error is returned
        self.assertEqual(result, "Database connection failed")

    def test_execute_no_results(self):
        """Test handling of empty search results"""
        # Setup mock to return empty results
        mock_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results

        # Execute search with filters
        result = self.search_tool.execute(
            query="nonexistent query",
            course_name="Test Course",
            lesson_number=1
        )

        # Verify appropriate "no results" message
        expected_msg = "No relevant content found in course 'Test Course' in lesson 1."
        self.assertEqual(result, expected_msg)

    def test_execute_no_results_no_filters(self):
        """Test handling of empty results without filters"""
        # Setup mock to return empty results
        mock_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results

        # Execute search without filters
        result = self.search_tool.execute(query="nonexistent query")

        # Verify appropriate "no results" message
        self.assertEqual(result, "No relevant content found.")

    def test_execute_multiple_results(self):
        """Test handling of multiple search results"""
        # Setup mock return value with multiple results
        mock_results = SearchResults(
            documents=[
                "Content from course 1 lesson 1",
                "Content from course 1 lesson 2"
            ],
            metadata=[
                {"course_title": "Course 1", "lesson_number": 1},
                {"course_title": "Course 1", "lesson_number": 2}
            ],
            distances=[0.3, 0.4],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        self.mock_vector_store.get_lesson_link.side_effect = [
            "https://example.com/lesson1",
            "https://example.com/lesson2"
        ]

        # Execute search
        result = self.search_tool.execute(query="test query", course_name="Course 1")

        # Verify both results are included
        self.assertIn("[Course 1 - Lesson 1]", result)
        self.assertIn("[Course 1 - Lesson 2]", result)
        self.assertIn("Content from course 1 lesson 1", result)
        self.assertIn("Content from course 1 lesson 2", result)
        
        # Verify two sources were stored
        self.assertEqual(len(self.search_tool.last_sources), 2)

    def test_execute_missing_metadata(self):
        """Test handling of missing metadata in results"""
        # Setup mock return value with incomplete metadata
        mock_results = SearchResults(
            documents=["Test content"],
            metadata=[{}],  # Empty metadata
            distances=[0.5],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results

        # Execute search
        result = self.search_tool.execute(query="test query")

        # Verify graceful handling of missing metadata
        self.assertIn("[unknown]", result)
        self.assertIn("Test content", result)

    def test_get_tool_definition(self):
        """Test that tool definition is properly formatted"""
        definition = self.search_tool.get_tool_definition()
        
        # Verify required fields
        self.assertEqual(definition["name"], "search_course_content")
        self.assertIn("description", definition)
        self.assertIn("input_schema", definition)
        
        # Verify schema structure
        schema = definition["input_schema"]
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("query", schema["properties"])
        self.assertEqual(schema["required"], ["query"])


if __name__ == '__main__':
    unittest.main()