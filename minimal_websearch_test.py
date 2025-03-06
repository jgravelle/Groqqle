#!/usr/bin/env python3
"""
Minimal test script that directly uses the WebSearch_Tool's fallback search.
This avoids the selenium import issue by implementing our own version of the fallback.
"""

import os
import sys
import urllib.request
from urllib.parse import quote_plus
import json

# Set DEBUG mode
os.environ['DEBUG'] = 'True'

def fallback_search(query, num_results=5):
    """Generate search engine links when direct search fails."""
    encoded_query = quote_plus(query)
    return [
        {
            "title": f"Google Search: {query}",
            "url": f"https://www.google.com/search?q={encoded_query}",
            "description": f"Search Google for information about '{query}'. Click this link to see search results directly."
        },
        {
            "title": f"Bing Search: {query}",
            "url": f"https://www.bing.com/search?q={encoded_query}",
            "description": f"Search Bing for information about '{query}'. Click this link to see search results directly."
        },
        {
            "title": f"DuckDuckGo Search: {query}",
            "url": f"https://duckduckgo.com/?q={encoded_query}",
            "description": f"Search DuckDuckGo for information about '{query}'. Click this link to see search results directly."
        }
    ]

def direct_web_search(query, num_results=5):
    """Attempt to perform a direct web search using DuckDuckGo Lite."""
    try:
        # Format the query for DuckDuckGo Lite search (most reliable without JS)
        encoded_query = quote_plus(query)
        search_url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
        
        # Set up headers to look like a normal browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "identity",  # No compression
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
        # Prepare the request
        print(f"Requesting: {search_url}")
        req = urllib.request.Request(search_url, headers=headers)
        
        # Send the request and get the response
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
        
        # Save the HTML for debugging
        with open("ddg_response.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Simple parsing for DuckDuckGo Lite
        results = []
        current_position = 0
        
        # Find links in the HTML
        while current_position < len(html_content) and len(results) < num_results:
            link_start = html_content.find('href="http', current_position)
            if link_start == -1:
                break
                
            url_start = link_start + 6  # Length of 'href="'
            url_end = html_content.find('"', url_start)
            url = html_content[url_start:url_end]
            
            # Skip DuckDuckGo links
            if "duckduckgo.com" in url:
                current_position = url_end + 1
                continue
                
            # Try to extract title
            title_start = html_content.find('>', url_end) + 1
            title_end = html_content.find('</a>', title_start)
            title = html_content[title_start:title_end].strip()
            
            # Use URL as title if no title found
            if not title:
                title = url.split('//')[1].split('/')[0]
            
            results.append({
                "title": title,
                "url": url,
                "description": f"Result found for '{query}'. Click to view the page."
            })
            
            current_position = title_end + 1
        
        # If we found results, return them
        if results:
            return results
        
        # Otherwise fall back to the generic links
        return fallback_search(query, num_results)
        
    except Exception as e:
        print(f"Error in direct web search: {str(e)}")
        import traceback
        traceback.print_exc()
        return fallback_search(query, num_results)

def main():
    """Test direct web search functionality."""
    print("Testing direct web search functionality")
    
    # Test query
    query = "test"
    num_results = 5
    print(f"\nPerforming web search for query: '{query}'")
    
    # Execute search
    try:
        results = direct_web_search(query, num_results)
        
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