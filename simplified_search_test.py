#!/usr/bin/env python3
"""
Simplified search test that tests the Web_Agent directly instead of through the API.
This gives us proper search results even without the API server running.
"""

import os
import sys
import json
import traceback
from urllib.parse import quote_plus
import urllib.request
from urllib.error import HTTPError, URLError
import time
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Set DEBUG mode
os.environ['DEBUG'] = 'True'

# Important: Do NOT set STREAMLIT_CLOUD to '1' here, as that forces the fallback mode

def log_debug(message):
    """Print debug messages when DEBUG is True."""
    if os.environ.get('DEBUG') == 'True':
        print(message)

def direct_web_search(query, num_results=5):
    """
    Perform a direct web search without Selenium using urllib.
    
    Args:
        query: The search query string
        num_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing search results with title, url, and description
    """
    log_debug(f"Performing direct web search for query: {query}")
    
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
        log_debug(f"Requesting: {search_url}")
        req = urllib.request.Request(search_url, headers=headers)
        
        # Send the request and get the response
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
        log_debug(f"Response received, length: {len(html_content)} bytes")
        
        # Parse the response using simple string operations (no BS4 needed)
        results = []
        lines = html_content.split('\n')
        
        # Debug: Save HTML content to file for analysis
        with open("ddg_response.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        log_debug(f"Saved DDG response HTML to ddg_response.html")
        
        # Check for common patterns in DuckDuckGo Lite's response
        log_debug(f"Checking for common patterns in response HTML")
        
        # Generic result extraction approach for DuckDuckGo Lite
        # Check for any links in the HTML that look like search results
        i = 0
        found_result_links = False
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if the line contains a hyperlink and doesn't point to DuckDuckGo itself
            if 'href="http' in line and 'duckduckgo.com' not in line:
                found_result_links = True
                log_debug(f"Found potential result link in line {i+1}: {line[:100]}...")
                
                # Extract the URL - find where it starts
                url_start = line.find('href="') + 6
                if url_start > 6:  # make sure 'href="' was found
                    url_end = line.find('"', url_start)
                    if url_end > url_start:
                        url = line[url_start:url_end]
                        
                        # Skip if not a valid external URL
                        if not url.startswith('http') or "duckduckgo.com" in url:
                            i += 1
                            continue
                        
                        # Try to extract a title - could be in the same line or next line
                        title = "No title"
                        title_start = line.find('>', url_end) + 1
                        if title_start > url_end:
                            title_end = line.find('</a>', title_start)
                            if title_end > title_start:
                                title = line[title_start:title_end].strip()
                        
                        # Try to find a description nearby
                        description = ""
                        for j in range(max(0, i-3), min(i+5, len(lines))):
                            if '<td' in lines[j] and '</td>' in lines[j] and not 'href' in lines[j].lower():
                                desc_start = lines[j].find('>') + 1
                                desc_end = lines[j].find('</td>', desc_start)
                                if desc_end > desc_start:
                                    description = lines[j][desc_start:desc_end].strip()
                                    break
                        
                        # Add this result
                        log_debug(f"Extracted URL: {url}")
                        log_debug(f"Extracted title: {title}")
                        log_debug(f"Extracted description: {description[:50]}...")
                        
                        result = {
                            "title": title,
                            "url": url,
                            "description": description
                        }
                        results.append(result)
                        
                        # Stop if we have enough results
                        if len(results) >= num_results:
                            break
            
            i += 1
            
        # Log stats about what we found
        log_debug(f"Found any result links: {found_result_links}")
        log_debug(f"Extracted {len(results)} valid results")
        
        # If we found valid results, return them
        if results:
            log_debug(f"Successfully found {len(results)} results")
            return results
            
        # If parsing failed or no results found, use a backup method
        log_debug("Primary parsing failed, attempting backup method")
        backup_results = backup_search(query, num_results)
        if backup_results:
            return backup_results
            
        # If all else fails, return generic search engine links
        log_debug("All search methods failed, returning fallback links")
        return fallback_results(query)
        
    except Exception as e:
        log_debug(f"Error in direct web search: {str(e)}")
        log_debug(traceback.format_exc())
        return fallback_results(query)

def backup_search(query, num_results=5):
    """Alternative search method using a different approach."""
    try:
        # Try searching using DuckDuckGo HTML version (alternative to Lite)
        encoded_query = quote_plus(query)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
            "Accept": "text/html",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache"
        }
        
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
        # Simple parsing for HTML version (different structure than Lite)
        results = []
        current_position = 0
        
        # Find each result block
        while current_position < len(html_content) and len(results) < num_results:
            # Find the start of a result
            result_start = html_content.find('<div class="result__body">', current_position)
            if result_start == -1:
                break
                
            # Find title and URL
            link_start = html_content.find('<a class="result__a" href="', result_start)
            if link_start == -1:
                current_position = result_start + 1
                continue
                
            url_start = link_start + len('<a class="result__a" href="')
            url_end = html_content.find('"', url_start)
            url = html_content[url_start:url_end]
            
            title_start = url_end + 2  # Skip '">
            title_end = html_content.find('</a>', title_start)
            title = html_content[title_start:title_end].strip()
            
            # Find description
            desc_start = html_content.find('<a class="result__snippet"', title_end)
            if desc_start != -1:
                desc_text_start = html_content.find('>', desc_start) + 1
                desc_end = html_content.find('</a>', desc_text_start)
                description = html_content[desc_text_start:desc_end].strip()
            else:
                description = ""
            
            # Only add if we have a valid URL and title
            if url and title and url.startswith('http'):
                result = {
                    "title": title,
                    "url": url,
                    "description": description
                }
                results.append(result)
                
            # Move to next result
            current_position = title_end
        
        return results if results else None
        
    except Exception as e:
        log_debug(f"Backup search error: {str(e)}")
        return None

def fallback_results(query):
    """Generate search engine links when all search methods fail."""
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

def main():
    """Test the Web_Agent search functionality directly."""
    print("Testing Web_Agent search functionality")
    
    # Check for API key
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
        print("ERROR: GROQ_API_KEY not found. Please set this environment variable or add it to a .env file.")
        return
    
    print(f"API key found: {api_key[:5]}...")
    
    try:
        # Import necessary modules
        from agents.Web_Agent import Web_Agent
        print("Successfully imported Web_Agent")
        
        # Query to test
        query = "test"  # Simple query to test functionality
        print(f"\nPerforming search for query: '{query}'")
        
        # Create Web_Agent instance
        agent = Web_Agent(
            api_key,
            num_results=5,
            max_tokens=4096,
            model="llama3-8b-8192",
            temperature=0.0,
            comprehension_grade=8,
            summary_length=300,
            humanize=False
        )
        print("Web_Agent initialized successfully")
        
        # Process the search request
        print("Calling agent.process_request()...")
        results = agent.process_request(query)
        
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
        traceback.print_exc()

if __name__ == "__main__":
    main()