import requests
from bs4 import BeautifulSoup
import sys
import json
import traceback

def log_debug(message):
    with open('debug_info.txt', 'a') as f:
        f.write(f"WebSearch_Tool: {message}\n")

def WebSearch_Tool(query, num_results=10):
    log_debug(f"Starting search for query: {query}, num_results: {num_results}")
    url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        log_debug("Sending request to Google")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        log_debug(f"Request successful. Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('div', class_='g')
        log_debug(f"Found {len(search_results)} raw search results")
        
        results = []
        for result in search_results:
            item = {}
            
            # Extract the title
            title_element = result.find('h3', class_='LC20lb')
            if title_element:
                item['title'] = title_element.get_text(strip=True)
            else:
                log_debug("Skipping result due to missing title")
                continue  # Skip this result if there's no title
            
            # Extract the URL
            link_element = result.find('a')
            if link_element:
                item['url'] = link_element['href']
            else:
                log_debug("Skipping result due to missing URL")
                continue  # Skip this result if there's no URL
            
            # Extract the description
            desc_element = result.find('div', class_='VwiC3b')
            if desc_element:
                item['description'] = desc_element.get_text(strip=True)
            else:
                item['description'] = "No description available"
                log_debug("No description found for a result")
            
            results.append(item)
        
        log_debug(f"Returning {len(results)} processed results")
        return results[:num_results]  # Ensure we don't return more than requested
    
    except requests.RequestException as e:
        log_debug(f"Request exception occurred: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        log_debug(f"Unexpected error occurred: {str(e)}")
        log_debug(f"Traceback: {traceback.format_exc()}")
        return {"error": f"An unexpected error occurred: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: WebSearch_Tool.py <search_query> [num_results]")
        sys.exit(1)
    
    query = sys.argv[1]
    num_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    results = WebSearch_Tool(query, num_results)
    
    # Convert the results to JSON and print
    print(json.dumps(results, indent=2))