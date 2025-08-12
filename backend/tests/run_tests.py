#!/usr/bin/env python3
"""
Test runner for the RAG chatbot system.
Runs all tests and provides detailed output for debugging.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    """Run all tests with detailed output"""
    print("=" * 70)
    print("RAG CHATBOT SYSTEM TEST SUITE")
    print("=" * 70)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    
    # Load tests from the tests directory
    test_dir = os.path.dirname(__file__)
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True,
        failfast=False
    )
    
    print(f"\nRunning tests from: {test_dir}")
    print("-" * 70)
    
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFAILURES:")
        print("-" * 40)
        for test, traceback in result.failures:
            print(f"• {test}")
            print(f"  {traceback.split('AssertionError: ')[-1].split(chr(10))[0]}")
    
    if result.errors:
        print("\nERRORS:")
        print("-" * 40)
        for test, traceback in result.errors:
            print(f"• {test}")
            # Extract the main error message
            error_lines = traceback.split('\n')
            for line in error_lines:
                if 'Error:' in line or 'Exception:' in line:
                    print(f"  {line.strip()}")
                    break
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / 
                   result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())