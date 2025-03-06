#!/usr/bin/env python3
"""
More comprehensive test for Groqqle_web_tool API.
Tests all main functionality while gracefully handling missing dependencies.
"""

import os
import sys
import traceback

# Enable debug mode
os.environ['DEBUG'] = 'True'
# Force cloud mode to avoid Selenium dependencies
os.environ['STREAMLIT_CLOUD'] = '1'

def main():
    """Comprehensive test for Groqqle_web_tool API"""
    print("Testing Groqqle_web_tool API functionality")
    
    # Step 1: Test importing the module
    print("\n--- Step 1: Testing import of Groqqle_web_tool ---")
    try:
        from Groqqle_web_tool import Groqqle_web_tool
        print("✓ Successfully imported Groqqle_web_tool")
    except ImportError as e:
        print(f"✗ Failed to import Groqqle_web_tool: {str(e)}")
        print("Make sure your Python environment is properly set up.")
        return
    
    # Step 2: Test importing dependencies
    print("\n--- Step 2: Testing WebSearch_Tool dependency ---")
    try:
        from tools.web_tools.WebSearch_Tool import WebSearch_Tool
        print("✓ Successfully imported WebSearch_Tool")
    except ImportError as e:
        print(f"✗ Failed to import WebSearch_Tool: {str(e)}")
        return
    
    print("\n--- Step 3: Testing WebGetContents_Tool dependency ---")
    try:
        from tools.web_tools.WebGetContents_Tool import WebGetContents_Tool
        print("✓ Successfully imported WebGetContents_Tool")
    except ImportError as e:
        print(f"✗ Failed to import WebGetContents_Tool: {str(e)}")
        return
    
    # Step 4: Test provider factory
    print("\n--- Step 4: Testing provider factory ---")
    try:
        from providers.provider_factory import ProviderFactory
        print("✓ Successfully imported ProviderFactory")
    except ImportError as e:
        print(f"✗ Failed to import ProviderFactory: {str(e)}")
        return
    
    # Step 5: Check for API keys
    print("\n--- Step 5: Checking for API keys ---")
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print(f"✓ Found GROQ_API_KEY environment variable")
        
        # Only show first few characters for security
        masked_key = api_key[:4] + "..." if len(api_key) > 4 else ""
        print(f"  Key starts with: {masked_key}")
    else:
        print("✗ GROQ_API_KEY environment variable not found")
        print("  Will try to initialize without it, but API functionality will be limited")
    
    # Step 6: Test WebSearch_Tool directly
    print("\n--- Step 6: Testing WebSearch_Tool directly ---")
    try:
        query = "What is quantum computing"
        print(f"Searching for: '{query}'")
        
        results = WebSearch_Tool(query, 3)  # Just get 3 results for testing
        
        if results:
            print(f"✓ Successfully retrieved {len(results)} search results")
            # Just show the first result title
            print(f"  First result: {results[0].get('title', 'No title')}")
        else:
            print("✗ No results returned from WebSearch_Tool")
            
    except Exception as e:
        print(f"✗ Error using WebSearch_Tool: {str(e)}")
        print(traceback.format_exc())
    
    # Step 7: Test Groqqle_web_tool initialization
    print("\n--- Step 7: Testing Groqqle_web_tool initialization ---")
    try:
        # Try with test credentials or empty string if missing
        # In a full implementation, these should be provided by user
        test_api_key = api_key if api_key else "test_key"
        
        groqqle_tool = Groqqle_web_tool(
            api_key=test_api_key,
            provider_name="groq",
            num_results=3,
            max_tokens=4096,
            model="llama3-8b-8192",
            temperature=0.0,
            comprehension_grade=8
        )
        print("✓ Successfully initialized Groqqle_web_tool")
        
        # Step 8: Test run method
        print("\n--- Step 8: Testing Groqqle_web_tool.run method ---")
        if api_key:  # Only run if we have a valid API key
            try:
                query = "What is quantum computing"
                print(f"Searching for: '{query}'")
                
                results = groqqle_tool.run(query)
                
                if results:
                    print(f"✓ Successfully retrieved {len(results)} results")
                    # Just show the first result title
                    print(f"  First result: {results[0].get('title', 'No title')}")
                    
                    # Step 9: Test URL summarization (only if we have results)
                    print("\n--- Step 9: Testing URL summarization ---")
                    try:
                        first_url = results[0]['url']
                        print(f"Summarizing URL: {first_url}")
                        
                        summary = groqqle_tool.summarize_url(first_url)
                        
                        if summary:
                            print("✓ Successfully generated summary")
                            print(f"  Title: {summary.get('title', 'No title')}")
                            # Show first 50 chars of description
                            desc = summary.get('description', '')
                            print(f"  Description starts with: {desc[:50]}..." if desc else "  No description")
                        else:
                            print("✗ Failed to generate summary")
                            
                    except Exception as e:
                        print(f"✗ Error summarizing URL: {str(e)}")
                else:
                    print("✗ No results returned from Groqqle_web_tool.run")
                    
            except Exception as e:
                print(f"✗ Error using Groqqle_web_tool.run: {str(e)}")
                print(traceback.format_exc())
        else:
            print("⚠ Skipping Groqqle_web_tool.run test - no API key available")
    
    except Exception as e:
        print(f"✗ Error initializing Groqqle_web_tool: {str(e)}")
        print(traceback.format_exc())
    
    print("\n--- Test Summary ---")
    print("Basic WebSearch_Tool functionality should work without API keys.")
    print("Full Groqqle_web_tool functionality requires valid API keys.")
    print("For optimal results, set up GROQ_API_KEY in your environment.")

if __name__ == "__main__":
    main()