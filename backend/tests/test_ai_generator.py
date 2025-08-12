import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock, patch, MagicMock
from ai_generator import AIGenerator


class TestAIGenerator(unittest.TestCase):
    """Test cases for AIGenerator tool calling functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.model = "claude-3-sonnet-20240229"
        self.ai_generator = AIGenerator(self.api_key, self.model)

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_response_without_tools(self, mock_anthropic):
        """Test basic response generation without tools"""
        # Setup mock client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Create AI generator
        ai_gen = AIGenerator(self.api_key, self.model)
        
        # Generate response
        result = ai_gen.generate_response("What is machine learning?")

        # Verify API call
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        
        self.assertEqual(call_args["model"], self.model)
        self.assertEqual(call_args["temperature"], 0)
        self.assertEqual(call_args["max_tokens"], 800)
        self.assertEqual(len(call_args["messages"]), 1)
        self.assertEqual(call_args["messages"][0]["content"], "What is machine learning?")

        # Verify response
        self.assertEqual(result, "Test response")

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_response_with_conversation_history(self, mock_anthropic):
        """Test response generation with conversation history"""
        # Setup mock client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Follow-up response")]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Create AI generator
        ai_gen = AIGenerator(self.api_key, self.model)
        
        # Generate response with history
        history = "Previous conversation context"
        result = ai_gen.generate_response("Follow up question", conversation_history=history)

        # Verify system prompt includes history
        call_args = mock_client.messages.create.call_args[1]
        self.assertIn(history, call_args["system"])

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_response_with_tools_no_tool_use(self, mock_anthropic):
        """Test response generation with tools available but not used"""
        # Setup mock client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Direct response")]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Create AI generator
        ai_gen = AIGenerator(self.api_key, self.model)
        
        # Setup mock tools
        tools = [{"name": "test_tool", "description": "Test tool"}]
        tool_manager = Mock()

        # Generate response
        result = ai_gen.generate_response(
            "General question", 
            tools=tools, 
            tool_manager=tool_manager
        )

        # Verify tools were included in API call
        call_args = mock_client.messages.create.call_args[1]
        self.assertEqual(call_args["tools"], tools)
        self.assertEqual(call_args["tool_choice"], {"type": "auto"})

        # Verify tool manager wasn't called
        tool_manager.execute_tool.assert_not_called()

        # Verify response
        self.assertEqual(result, "Direct response")

    @patch('ai_generator.anthropic.Anthropic')
    def test_generate_response_with_tool_use(self, mock_anthropic):
        """Test response generation with tool use"""
        # Setup mock client
        mock_client = Mock()
        
        # Mock initial response with tool use
        mock_tool_content = Mock()
        mock_tool_content.type = "tool_use"
        mock_tool_content.name = "search_course_content"
        mock_tool_content.input = {"query": "test query", "course_name": "Test Course"}
        mock_tool_content.id = "tool_123"
        
        mock_initial_response = Mock()
        mock_initial_response.content = [mock_tool_content]
        mock_initial_response.stop_reason = "tool_use"

        # Mock final response after tool execution
        mock_final_response = Mock()
        mock_final_response.content = [Mock(text="Response based on tool results")]
        
        # Setup client to return initial then final response
        mock_client.messages.create.side_effect = [mock_initial_response, mock_final_response]
        mock_anthropic.return_value = mock_client

        # Create AI generator
        ai_gen = AIGenerator(self.api_key, self.model)
        
        # Setup mock tools and tool manager
        tools = [{"name": "search_course_content", "description": "Search course content"}]
        tool_manager = Mock()
        tool_manager.execute_tool.return_value = "Tool execution result"

        # Generate response
        result = ai_gen.generate_response(
            "Search for machine learning content",
            tools=tools,
            tool_manager=tool_manager
        )

        # Verify tool was executed
        tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="test query",
            course_name="Test Course"
        )

        # Verify two API calls were made
        self.assertEqual(mock_client.messages.create.call_count, 2)
        
        # Verify second call includes tool results
        second_call_args = mock_client.messages.create.call_args_list[1][1]
        self.assertEqual(len(second_call_args["messages"]), 3)  # user, assistant, user with tool results
        
        # Verify final response
        self.assertEqual(result, "Response based on tool results")

    @patch('ai_generator.anthropic.Anthropic')
    def test_handle_tool_execution_error(self, mock_anthropic):
        """Test handling of tool execution errors"""
        # Setup mock client
        mock_client = Mock()
        
        # Mock initial response with tool use
        mock_tool_content = Mock()
        mock_tool_content.type = "tool_use"
        mock_tool_content.name = "search_course_content"
        mock_tool_content.input = {"query": "test query"}
        mock_tool_content.id = "tool_123"
        
        mock_initial_response = Mock()
        mock_initial_response.content = [mock_tool_content]
        mock_initial_response.stop_reason = "tool_use"

        # Mock final response
        mock_final_response = Mock()
        mock_final_response.content = [Mock(text="Error handled response")]
        
        mock_client.messages.create.side_effect = [mock_initial_response, mock_final_response]
        mock_anthropic.return_value = mock_client

        # Create AI generator
        ai_gen = AIGenerator(self.api_key, self.model)
        
        # Setup mock tool manager that returns error
        tools = [{"name": "search_course_content", "description": "Search course content"}]
        tool_manager = Mock()
        tool_manager.execute_tool.return_value = "Tool execution failed: Database error"

        # Generate response
        result = ai_gen.generate_response(
            "Search query",
            tools=tools,
            tool_manager=tool_manager
        )

        # Verify tool error was passed to AI
        second_call_args = mock_client.messages.create.call_args_list[1][1]
        tool_result_message = second_call_args["messages"][2]  # Tool result message
        self.assertIn("Tool execution failed: Database error", str(tool_result_message))

        # Verify AI handled the error
        self.assertEqual(result, "Error handled response")

    def test_system_prompt_content(self):
        """Test that system prompt contains expected instructions"""
        system_prompt = AIGenerator.SYSTEM_PROMPT
        
        # Check for key elements
        self.assertIn("course materials", system_prompt.lower())
        self.assertIn("search_course_content", system_prompt)
        self.assertIn("get_course_outline", system_prompt)
        self.assertIn("one tool use per query maximum", system_prompt.lower())

    @patch('ai_generator.anthropic.Anthropic')
    def test_multiple_tool_calls_in_response(self, mock_anthropic):
        """Test handling of multiple tool calls in a single response"""
        # Setup mock client
        mock_client = Mock()
        
        # Mock initial response with multiple tool uses
        mock_tool1 = Mock()
        mock_tool1.type = "tool_use"
        mock_tool1.name = "search_course_content"
        mock_tool1.input = {"query": "test1"}
        mock_tool1.id = "tool_1"

        mock_tool2 = Mock()
        mock_tool2.type = "tool_use"
        mock_tool2.name = "get_course_outline"
        mock_tool2.input = {"course_name": "Test Course"}
        mock_tool2.id = "tool_2"
        
        mock_initial_response = Mock()
        mock_initial_response.content = [mock_tool1, mock_tool2]
        mock_initial_response.stop_reason = "tool_use"

        mock_final_response = Mock()
        mock_final_response.content = [Mock(text="Combined response")]
        
        mock_client.messages.create.side_effect = [mock_initial_response, mock_final_response]
        mock_anthropic.return_value = mock_client

        # Create AI generator
        ai_gen = AIGenerator(self.api_key, self.model)
        
        # Setup mock tool manager
        tools = [{"name": "search_course_content"}, {"name": "get_course_outline"}]
        tool_manager = Mock()
        tool_manager.execute_tool.side_effect = ["Result 1", "Result 2"]

        # Generate response
        result = ai_gen.generate_response(
            "Complex query",
            tools=tools,
            tool_manager=tool_manager
        )

        # Verify both tools were executed
        self.assertEqual(tool_manager.execute_tool.call_count, 2)
        
        # Verify tool results were passed correctly
        second_call_args = mock_client.messages.create.call_args_list[1][1]
        tool_results_message = second_call_args["messages"][2]
        self.assertEqual(len(tool_results_message["content"]), 2)  # Two tool results


if __name__ == '__main__':
    unittest.main()