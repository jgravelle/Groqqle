#!/usr/bin/env python3
"""
Demo script for Groqqle API functionality with realistic static results.
This simulates how the API would work in a real-world scenario.
"""

import os
import sys
import json
from static_search import static_search_results

class GroqqleAPI:
    """Simulated Groqqle API for demonstration purposes"""
    
    def __init__(self, api_key=None):
        """Initialize the API with an optional API key"""
        self.api_key = api_key
        print("Initializing Groqqle API (simulation)")
        if not api_key:
            print("Warning: No API key provided, functionality may be limited")
        
    def search(self, query, search_type="web", num_results=10, max_tokens=4096):
        """
        Perform a search using the Groqqle API.
        
        Args:
            query (str): The search query
            search_type (str): Type of search - "web" or "news"
            num_results (int): Number of results to return
            max_tokens (int): Maximum tokens for generation
            
        Returns:
            list: List of search result dictionaries
        """
        print(f"Searching for: '{query}' (type: {search_type})")
        
        # Use static results for demo purposes
        results = static_search_results(query)
        
        # Limit to requested number of results
        return results[:num_results] if results else []
    
    def summarize_url(self, url, max_tokens=4096, comprehension_grade=8):
        """
        Generate a summary of a web page's content.
        
        Args:
            url (str): The URL to summarize
            max_tokens (int): Maximum tokens for generation
            comprehension_grade (int): Target reading level
            
        Returns:
            dict: Summary with title and description
        """
        print(f"Summarizing URL: {url}")
        print(f"Parameters: max_tokens={max_tokens}, comprehension_grade={comprehension_grade}")
        
        # Generate a demo summary
        # In a real implementation, this would fetch and summarize actual content
        return {
            "title": "Simulated Summary: " + url.split('/')[-1],
            "url": url,
            "description": f"This is a simulated summary of the content at {url}, generated at a reading comprehension level appropriate for grade {comprehension_grade}. In a real implementation, this would fetch the content from the URL, process it, and generate a comprehensive summary with the specified parameters."
        }

def demo_api_usage():
    """Demonstrate usage of the Groqqle API"""
    print("=== Groqqle API Usage Demo ===\n")
    
    # Initialize the API
    api_key = os.environ.get("GROQ_API_KEY", "demo_key_123456")
    api = GroqqleAPI(api_key)
    
    # Demo 1: Basic web search
    print("\n--- Demo 1: Basic Web Search ---")
    results = api.search("quantum computing", num_results=3)
    
    print("\nResults:")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        description = result.get('description', 'No description')
        if len(description) > 100:
            description = description[:100] + "..."
        print(f"Description: {description}")
    
    # Demo 2: URL summarization
    print("\n--- Demo 2: URL Summarization ---")
    if results:
        first_url = results[0]['url']
        summary = api.summarize_url(first_url, comprehension_grade=10)
        
        print("\nSummary:")
        print(f"Title: {summary['title']}")
        print(f"URL: {summary['url']}")
        print(f"Description: {summary['description'][:200]}...")
    
    # Demo 3: News search (simulated)
    print("\n--- Demo 3: News Search (Simulated) ---")
    news_results = api.search("artificial intelligence", search_type="news", num_results=2)
    
    print("\nNews Results:")
    for i, result in enumerate(news_results, 1):
        print(f"\nResult {i}:")
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        description = result.get('description', 'No description')
        if len(description) > 100:
            description = description[:100] + "..."
        print(f"Description: {description}")
    
    # Integration example
    print("\n--- Integration Example ---")
    print("""
To integrate this functionality in your code:

```python
from groqqle_api import GroqqleAPI

# Initialize with your API key
api = GroqqleAPI("your_api_key_here")

# Search for information
results = api.search(
    query="your search query",
    search_type="web",  # or "news"
    num_results=10
)

# Process results
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Description: {result['description']}")
    
# Summarize a specific URL
summary = api.summarize_url(
    url="https://example.com/article",
    comprehension_grade=8  # Target reading level
)

print(f"Summary: {summary['description']}")
```
    """)
    
    print("\n--- Implementation Notes ---")
    print("1. In a real implementation, you would need to start the Groqqle API server")
    print("2. API requests would be made via HTTP to the server endpoint")
    print("3. The response format shown here matches the actual API response format")
    print("4. API keys should be stored securely and not hardcoded")

if __name__ == "__main__":
    demo_api_usage()