"""
Example script demonstrating how to use Groqqle's API functionality.

This is a minimal example that shows the API structure
without requiring actual execution of the code.
"""

# Import required libraries
import requests
import json

def groqqle_search(query, search_type="web", num_results=10, max_tokens=4096):
    """
    Function to perform a search using Groqqle's API.
    
    Args:
        query (str): The search query
        search_type (str): Either "web" or "news"
        num_results (int): Number of results to return
        max_tokens (int): Maximum number of tokens for responses
        
    Returns:
        dict: JSON response from the API
    """
    # API endpoint (when running Groqqle in API mode)
    api_url = "http://127.0.0.1:5000/search"
    
    # Prepare the request payload
    payload = {
        "query": query,
        "num_results": num_results,
        "max_tokens": max_tokens,
        "search_type": search_type  # "web" or "news"
    }
    
    # Send the POST request
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def example_usage():
    """Show example usage without actually executing the API calls."""
    
    print("=== Groqqle API Usage Example ===")
    print("\nExample 1: Web Search")
    print("```python")
    print('results = groqqle_search("quantum computing breakthroughs", search_type="web")')
    print("for result in results:")
    print('    print(f"Title: {result[\'title\']}")')
    print('    print(f"URL: {result[\'url\']}")')
    print('    print(f"Description: {result[\'description\'][:100]}...")')
    print('    print("")')
    print("```")
    
    print("\nExample 2: News Search")
    print("```python")
    print('news_results = groqqle_search("latest AI developments", search_type="news", num_results=5)')
    print("for result in news_results:")
    print('    print(f"Title: {result[\'title\']}")')
    print('    print(f"Source: {result.get(\'source\', \'Unknown\')}")')
    print('    print(f"Date: {result.get(\'timestamp\', \'Unknown\')}")')
    print('    print(f"URL: {result[\'url\']}")')
    print('    print("")')
    print("```")
    
    print("\n=== How to Start the API Server ===")
    print("To use this functionality, you need to start Groqqle in API mode:")
    print("```bash")
    print("python Groqqle.py api --num_results 20 --max_tokens 4096")
    print("```")
    
    print("\nThe API server will start running on http://127.0.0.1:5000")
    print("You can then use the groqqle_search function to interact with it.")
    
    print("\n=== Environment Setup ===")
    print("Make sure you have set the GROQ_API_KEY in your environment variables or .env file:")
    print("```env")
    print("GROQ_API_KEY=your_api_key_here")
    print("```")
    
    print("\n=== Extended API Options ===")
    print("You can customize these parameters:")
    print("- num_results: Number of search results (default: 10)")
    print("- max_tokens: Maximum tokens for AI responses (default: 4096)")
    print("- search_type: 'web' or 'news' (default: 'web')")
    
if __name__ == "__main__":
    # Just show the example usage
    example_usage()
    
    print("\n=== Notes ===")
    print("1. This is just an example - you need to actually start the Groqqle API server")
    print("2. Required dependencies: requests, json")
    print("3. Make sure to set up your API keys properly")
    print("4. You can modify this script for your specific use case")