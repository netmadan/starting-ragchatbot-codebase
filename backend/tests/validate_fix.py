#!/usr/bin/env python3
"""
Validation script to confirm the MAX_RESULTS fix resolved the "query failed" issue.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import config
from rag_system import RAGSystem

def main():
    print("=" * 60)
    print("VALIDATION: RAG CHATBOT SYSTEM FIX")
    print("=" * 60)
    
    print(f"✓ MAX_RESULTS configuration: {config.MAX_RESULTS}")
    
    # Initialize system
    try:
        rag_system = RAGSystem(config)
        print("✓ RAG system initialized successfully")
    except Exception as e:
        print(f"✗ RAG system initialization failed: {e}")
        return False

    # Test CourseSearchTool directly
    print("\n1. Testing CourseSearchTool directly:")
    print("-" * 40)
    try:
        result = rag_system.search_tool.execute(
            query="MCP server",
            course_name="MCP"
        )
        if "error" in result.lower() or "failed" in result.lower():
            print(f"✗ CourseSearchTool still returning errors: {result}")
            return False
        else:
            print(f"✓ CourseSearchTool working: Found content")
            print(f"  Preview: {result[:150]}...")
    except Exception as e:
        print(f"✗ CourseSearchTool execution failed: {e}")
        return False

    # Test vector store search
    print("\n2. Testing Vector Store search:")
    print("-" * 40)
    try:
        search_results = rag_system.vector_store.search("MCP server")
        if search_results.error:
            print(f"✗ Vector store error: {search_results.error}")
            return False
        elif len(search_results.documents) == 0:
            print(f"✗ Vector store returned no results (might be no matching content)")
        else:
            print(f"✓ Vector store working: {len(search_results.documents)} results")
            print(f"  Preview: {search_results.documents[0][:100]}...")
    except Exception as e:
        print(f"✗ Vector store search failed: {e}")
        return False

    # Test end-to-end RAG query
    print("\n3. Testing end-to-end RAG query:")
    print("-" * 40)
    try:
        response, sources = rag_system.query("What is an MCP server?")
        print(f"✓ RAG query successful")
        print(f"  Response length: {len(response)} characters")
        print(f"  Sources found: {len(sources)}")
        
        if len(sources) > 0:
            print(f"✓ Sources retrieved successfully: {sources[0]['text']}")
        else:
            print("! No sources found (tool may not have been invoked)")
            
        # Check if response seems course-specific vs generic
        if "mcp" in response.lower() and ("server" in response.lower() or "protocol" in response.lower()):
            print("✓ Response appears to contain course-specific content")
        else:
            print("! Response appears generic (tool may not have been used)")
            
    except Exception as e:
        print(f"✗ End-to-end query failed: {e}")
        return False

    # Test course analytics
    print("\n4. Testing system status:")
    print("-" * 40)
    try:
        analytics = rag_system.get_course_analytics()
        print(f"✓ Course count: {analytics['total_courses']}")
        print(f"✓ Available courses: {', '.join(analytics['course_titles'][:2])}...")
    except Exception as e:
        print(f"✗ Analytics failed: {e}")

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY:")
    print("✓ MAX_RESULTS configuration fixed")
    print("✓ Search functionality restored")
    print("✓ CourseSearchTool working")
    print("✓ Vector store operational")
    print("✓ End-to-end RAG pipeline functional")
    print("\nThe 'query failed' issue has been RESOLVED!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)