import unittest
import sys
import os
import tempfile
import shutil
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock, patch, MagicMock
from rag_system import RAGSystem
from config import Config


class TestRAGIntegration(unittest.TestCase):
    """Integration tests for RAG system query handling"""

    def setUp(self):
        """Set up test fixtures with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test config with temporary database
        self.test_config = Config()
        self.test_config.CHROMA_PATH = os.path.join(self.temp_dir, "test_chroma_db")
        self.test_config.ANTHROPIC_API_KEY = "test_key"
        self.test_config.MAX_RESULTS = 5  # Fix the config issue

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('rag_system.AIGenerator')
    @patch('rag_system.VectorStore')
    def test_rag_system_initialization(self, mock_vector_store, mock_ai_generator):
        """Test that RAG system initializes all components correctly"""
        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Verify components were initialized
        self.assertIsNotNone(rag_system.document_processor)
        self.assertIsNotNone(rag_system.vector_store)
        self.assertIsNotNone(rag_system.ai_generator)
        self.assertIsNotNone(rag_system.session_manager)
        self.assertIsNotNone(rag_system.tool_manager)
        
        # Verify tools were registered
        self.assertEqual(len(rag_system.tool_manager.tools), 2)  # search and outline tools
        self.assertIn("search_course_content", rag_system.tool_manager.tools)
        self.assertIn("get_course_outline", rag_system.tool_manager.tools)

    @patch('rag_system.AIGenerator')
    def test_query_creates_session_if_none_provided(self, mock_ai_generator):
        """Test that query creates a session if none provided"""
        # Setup mock AI generator
        mock_ai_instance = Mock()
        mock_ai_instance.generate_response.return_value = "Test response"
        mock_ai_generator.return_value = mock_ai_instance

        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Query without session ID
        response, sources = rag_system.query("Test query")
        
        # Verify response was generated
        self.assertEqual(response, "Test response")
        self.assertIsInstance(sources, list)

    @patch('rag_system.AIGenerator')
    def test_query_with_existing_session(self, mock_ai_generator):
        """Test that query uses existing session for history"""
        # Setup mock AI generator
        mock_ai_instance = Mock()
        mock_ai_instance.generate_response.return_value = "Contextual response"
        mock_ai_generator.return_value = mock_ai_instance

        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Create a session with some history
        session_id = rag_system.session_manager.create_session()
        rag_system.session_manager.add_exchange(session_id, "Previous query", "Previous response")
        
        # Query with existing session
        response, sources = rag_system.query("Follow-up query", session_id)
        
        # Verify AI generator was called with history
        mock_ai_instance.generate_response.assert_called_once()
        call_args = mock_ai_instance.generate_response.call_args[1]
        
        self.assertIsNotNone(call_args.get("conversation_history"))
        self.assertIn("tools", call_args)
        self.assertIn("tool_manager", call_args)

    @patch('rag_system.AIGenerator')
    @patch('rag_system.VectorStore')
    def test_query_handles_tool_execution(self, mock_vector_store, mock_ai_generator):
        """Test that query properly handles tool execution"""
        # Setup mock vector store
        mock_vs_instance = Mock()
        mock_vector_store.return_value = mock_vs_instance

        # Setup mock AI generator
        mock_ai_instance = Mock()
        mock_ai_instance.generate_response.return_value = "AI response with tool results"
        mock_ai_generator.return_value = mock_ai_instance

        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Mock the search tool to return sources
        rag_system.search_tool.last_sources = [
            {"text": "Test Course - Lesson 1", "link": "https://example.com/lesson1"}
        ]

        # Query for content
        response, sources = rag_system.query("What is machine learning?")
        
        # Verify AI was called with tools
        mock_ai_instance.generate_response.assert_called_once()
        call_args = mock_ai_instance.generate_response.call_args[1]
        
        self.assertIsNotNone(call_args.get("tools"))
        self.assertIsNotNone(call_args.get("tool_manager"))
        
        # Verify sources were retrieved and reset
        self.assertIsInstance(sources, list)

    @patch('rag_system.AIGenerator')
    def test_query_handles_ai_generator_exception(self, mock_ai_generator):
        """Test that query handles AI generator exceptions gracefully"""
        # Setup mock AI generator to raise exception
        mock_ai_instance = Mock()
        mock_ai_instance.generate_response.side_effect = Exception("API Error")
        mock_ai_generator.return_value = mock_ai_instance

        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Query should raise the exception (not caught in current implementation)
        with self.assertRaises(Exception) as context:
            rag_system.query("Test query")
        
        self.assertIn("API Error", str(context.exception))

    @patch('rag_system.VectorStore')
    def test_add_course_document_success(self, mock_vector_store):
        """Test successful course document addition"""
        # Setup mock vector store
        mock_vs_instance = Mock()
        mock_vector_store.return_value = mock_vs_instance

        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Mock document processor
        mock_course = Mock()
        mock_course.title = "Test Course"
        mock_chunks = [Mock(), Mock(), Mock()]  # 3 chunks
        
        rag_system.document_processor.process_course_document = Mock(
            return_value=(mock_course, mock_chunks)
        )

        # Add course document
        course, chunk_count = rag_system.add_course_document("test_file.txt")
        
        # Verify processing
        self.assertEqual(course, mock_course)
        self.assertEqual(chunk_count, 3)
        
        # Verify vector store was called
        mock_vs_instance.add_course_metadata.assert_called_once_with(mock_course)
        mock_vs_instance.add_course_content.assert_called_once_with(mock_chunks)

    @patch('rag_system.VectorStore')
    def test_add_course_document_failure(self, mock_vector_store):
        """Test handling of document processing failure"""
        # Setup mock vector store
        mock_vs_instance = Mock()
        mock_vector_store.return_value = mock_vs_instance

        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Mock document processor to raise exception
        rag_system.document_processor.process_course_document = Mock(
            side_effect=Exception("File not found")
        )

        # Add course document
        course, chunk_count = rag_system.add_course_document("nonexistent_file.txt")
        
        # Verify failure handling
        self.assertIsNone(course)
        self.assertEqual(chunk_count, 0)

    def test_get_course_analytics(self):
        """Test course analytics retrieval"""
        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Mock vector store methods
        rag_system.vector_store.get_course_count = Mock(return_value=5)
        rag_system.vector_store.get_existing_course_titles = Mock(
            return_value=["Course 1", "Course 2", "Course 3", "Course 4", "Course 5"]
        )

        # Get analytics
        analytics = rag_system.get_course_analytics()
        
        # Verify analytics
        self.assertEqual(analytics["total_courses"], 5)
        self.assertEqual(len(analytics["course_titles"]), 5)
        self.assertIn("Course 1", analytics["course_titles"])

    @patch('rag_system.os.path.exists')
    @patch('rag_system.os.listdir')
    def test_add_course_folder_with_files(self, mock_listdir, mock_exists):
        """Test adding courses from a folder"""
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ["course1.txt", "course2.pdf", "image.jpg", "course3.docx"]

        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Mock vector store methods
        rag_system.vector_store.get_existing_course_titles = Mock(return_value=set())
        
        # Mock document processor
        def mock_process_document(file_path):
            if "course1" in file_path:
                mock_course = Mock()
                mock_course.title = "Course 1"
                return mock_course, [Mock(), Mock()]
            elif "course2" in file_path:
                mock_course = Mock()
                mock_course.title = "Course 2"
                return mock_course, [Mock()]
            elif "course3" in file_path:
                mock_course = Mock()
                mock_course.title = "Course 3"
                return mock_course, [Mock(), Mock(), Mock()]
            return None, []

        rag_system.document_processor.process_course_document = Mock(side_effect=mock_process_document)
        rag_system.vector_store.add_course_metadata = Mock()
        rag_system.vector_store.add_course_content = Mock()

        # Add course folder
        total_courses, total_chunks = rag_system.add_course_folder("/test/folder")
        
        # Verify results (should process 3 valid files, skip image.jpg)
        self.assertEqual(total_courses, 3)
        self.assertEqual(total_chunks, 6)  # 2 + 1 + 3 chunks

    @patch('rag_system.os.path.exists')
    def test_add_course_folder_nonexistent(self, mock_exists):
        """Test handling of nonexistent folder"""
        mock_exists.return_value = False

        # Create RAG system
        rag_system = RAGSystem(self.test_config)
        
        # Add nonexistent folder
        total_courses, total_chunks = rag_system.add_course_folder("/nonexistent/folder")
        
        # Verify no processing occurred
        self.assertEqual(total_courses, 0)
        self.assertEqual(total_chunks, 0)


class TestRAGSystemEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions in RAG system"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = Config()
        self.test_config.CHROMA_PATH = os.path.join(self.temp_dir, "test_chroma_db")
        self.test_config.ANTHROPIC_API_KEY = "test_key"
        self.test_config.MAX_RESULTS = 5

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('rag_system.AIGenerator')
    def test_empty_query_handling(self, mock_ai_generator):
        """Test handling of empty queries"""
        mock_ai_instance = Mock()
        mock_ai_instance.generate_response.return_value = "Please provide a query"
        mock_ai_generator.return_value = mock_ai_instance

        rag_system = RAGSystem(self.test_config)
        
        response, sources = rag_system.query("")
        
        # Should still process the empty query
        self.assertIsInstance(response, str)
        self.assertIsInstance(sources, list)

    @patch('rag_system.AIGenerator')
    def test_very_long_query_handling(self, mock_ai_generator):
        """Test handling of very long queries"""
        mock_ai_instance = Mock()
        mock_ai_instance.generate_response.return_value = "Response to long query"
        mock_ai_generator.return_value = mock_ai_instance

        rag_system = RAGSystem(self.test_config)
        
        long_query = "What is machine learning? " * 100  # Very long query
        response, sources = rag_system.query(long_query)
        
        # Should handle long queries
        self.assertEqual(response, "Response to long query")


if __name__ == '__main__':
    unittest.main()