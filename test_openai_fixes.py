#!/usr/bin/env python3
"""
Test script to validate OpenAI API fixes for empty response issues.
This script tests the improved error handling, debug logging, and recovery mechanisms.
"""
import asyncio
import os
from dotenv import load_dotenv
from app.services import get_sql_from_gpt

# Load environment variables
load_dotenv(override=True)

async def test_openai_fixes():
    """Test the OpenAI API improvements with various question types."""
    
    print("🧪 Testing OpenAI API Fixes for Empty Response Issues")
    print("=" * 60)
    
    # Test cases with different complexity levels
    test_questions = [
        "How many employees are there?",
        "Show me the top 5 products by sales",
        "What is the average age of employees?",
        "List all departments",
        "Find customers in Seattle",
        "Show employee details with their departments",
        # Edge case - very simple question
        "Show me some data",
        # Edge case - complex question
        "Give me a comprehensive analysis of sales performance by product category including revenue, quantity, and growth trends over the last year"
    ]
    
    successful_tests = 0
    total_tests = len(test_questions)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}/{total_tests}: {question}")
        print("-" * 40)
        
        try:
            sql_result = await get_sql_from_gpt(question)
            
            if sql_result and len(sql_result.strip()) > 0:
                print(f"✅ SUCCESS: Generated SQL ({len(sql_result)} chars)")
                print(f"📝 SQL: {sql_result}")
                successful_tests += 1
            else:
                print("❌ FAILED: Empty SQL returned")
                
        except Exception as e:
            print(f"❌ FAILED: Exception occurred: {e}")
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"📊 TEST RESULTS: {successful_tests}/{total_tests} tests passed")
    success_rate = (successful_tests / total_tests) * 100
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Empty response issues should be resolved.")
    elif successful_tests >= total_tests * 0.8:
        print("⚠️  Most tests passed. Minor issues may remain.")
    else:
        print("🚨 Several tests failed. Further investigation needed.")
    
    return successful_tests, total_tests

async def test_error_scenarios():
    """Test error handling scenarios."""
    print("\n🔧 Testing Error Handling Scenarios")
    print("=" * 60)
    
    # Test with potentially problematic input
    edge_cases = [
        "",  # Empty question
        "   ",  # Whitespace only
        "DROP TABLE Users;",  # Malicious input (should be handled)
        "SELECT * FROM NonExistentTable",  # Valid SQL but wrong table
    ]
    
    for i, question in enumerate(edge_cases, 1):
        print(f"\n🧪 Edge Case {i}: '{question}'")
        print("-" * 30)
        
        try:
            sql_result = await get_sql_from_gpt(question)
            print(f"✅ Handled gracefully: {sql_result[:50]}{'...' if len(sql_result) > 50 else ''}")
        except Exception as e:
            print(f"⚠️  Exception (expected): {e}")

if __name__ == "__main__":
    print("🚀 Starting OpenAI API Fix Validation Tests...")
    
    # Check if API key is configured
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Make sure your .env file is properly configured")
        exit(1)
    
    # Run the tests
    asyncio.run(test_openai_fixes())
    asyncio.run(test_error_scenarios())
    
    print("\n✨ Test run completed!")
