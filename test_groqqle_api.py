#!/usr/bin/env python3
"""
Test script for Groqqle API functionality (developer usage without GUI)
This version directly uses the Web_Agent rather than starting an API server.
"""

import os
import sys
import time
import traceback

# Load environment variables from .env file manually
def load_env_file():
    try:
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if line.strip() and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value.strip('"\'')
    except Exception as e:
        print(f"Error loading .env file: {e}")

# Load the .env file
load_env_file()

# Enable debug mode
os.environ['DEBUG'] = 'True'

# Make sure we're NOT using cloud mode - we want real search results
if 'STREAMLIT_CLOUD' in os.environ:
    del os.environ['STREAMLIT_CLOUD']

def test_web_agent_search(query, num_results=5):
    """Test the Web_Agent search functionality directly"""
    from agents.Web_Agent import Web_Agent
    
    # Get API key
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        # Try to read from .env file if it exists
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("GROQ_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip('"\'')
                        break
        except Exception as e:
            print(f"Error reading .env file: {str(e)}")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set this environment variable or add it to a .env file.")
    
    # Initialize Web_Agent
    agent = Web_Agent(
        api_key,
        num_results=num_results,
        max_tokens=4096,
        model="llama3-8b-8192",
        temperature=0.0,
        comprehension_grade=8,
        summary_length=300,
        humanize=False
    )
    
    # Process the search request
    return agent.process_request(query)

def main():
    """Test the Web_Agent search functionality directly"""
    print("Testing Web_Agent search functionality")
    
    # Verify we have the GROQ_API_KEY set
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("WARNING: GROQ_API_KEY environment variable not set. Checking .env file...")
        try:
            with open(".env", "r") as f:
                if "GROQ_API_KEY=" in f.read():
                    print("Found GROQ_API_KEY in .env file.")
                else:
                    print("GROQ_API_KEY not found in .env file. Tests will likely fail.")
        except:
            print("No .env file found. Tests will likely fail.")
    else:
        print(f"Found GROQ_API_KEY in environment variables: {api_key[:5]}...")
    
    # Test a web search
    query = "test"  # Simple query to test functionality
    print(f"\nPerforming web search for query: '{query}'")
    
    try:
        # Call the Web_Agent directly
        results = test_web_agent_search(query)
        
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
        print(f"\nError: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()