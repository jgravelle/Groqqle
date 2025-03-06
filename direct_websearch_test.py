#!/usr/bin/env python3
"""
Simple test script to directly test the WebSearch_Tool functionality.
This script uses the cloud mode to skip Selenium requirements.
"""

import os
import sys

# Set DEBUG mode
os.environ['DEBUG'] = 'True'
# Force cloud mode to avoid Selenium dependencies
os.environ['STREAMLIT_CLOUD'] = '1'

def main():
    """Direct test of WebSearch_Tool without Web_Agent"""
    print("Testing direct WebSearch_Tool functionality in cloud mode")
    
    try:
        # Import after setting environment variables
        from tools.web_tools.WebSearch_Tool import WebSearch_Tool
        
        # Test query
        query = "test"
        num_results = 5
        print(f"\nPerforming web search for query: '{query}'")
        
        # Execute search
        results = WebSearch_Tool(query, num_results)
        
        # Display results
        if results:
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Title: {result['title']}")
                print(f"URL: {result['url']}")
                description = result.get('description', 'No description')
                print(f"Description: {description[:150]}..." if len(description) > 150 else f"Description: {description}")
        else:
            print("\nNo results found.")
    
    except Exception as e:
        print(f"\nError during search: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()