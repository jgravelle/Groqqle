import os
import requests
import sys
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEBUG = os.environ.get('DEBUG') == 'True'

def log_debug(message):
    if DEBUG:
        print(message)

def WebSearch_Tool(query: str, num_results: int = 10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.0',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    search_url = f"https://www.google.com/search?q={query}&num={num_results}"
    log_debug(f"Search URL: {search_url}")

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        search_results = []
        for g in soup.find_all('div', class_='g'):
            anchor = g.find('a')
            title = g.find('h3').text if g.find('h3') else 'No title'
            url = anchor.get('href', 'No URL') if anchor else 'No URL'
            
            # Extracting the description
            description = ''
            description_div = g.find('div', class_=['VwiC3b', 'yXK7lf']) # Add more classes if needed
            if description_div:
                description = description_div.get_text(strip=True)
            else:
                # Fallback: try to get any text content if the specific class is not found
                description = g.get_text(strip=True)

            search_results.append({
                'title': title,
                'description': description,
                'url': url
            })

        if DEBUG:
            print(f"Successfully retrieved {len(search_results)} search results for query: {query}")
            print(f"Search results preview: {search_results[:5]}")

        return search_results

    except requests.RequestException as e:
        error_message = f"Error performing search for query '{query}': {str(e)}"
        if DEBUG:
            print(error_message)
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: WebSearch_Tool.py <query> [num_results]")
        sys.exit(1)

    query = sys.argv[1]
    num_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    results = WebSearch_Tool(query, num_results)
    if results:
        for result in results:
            print(result)
    else:
        print("Failed to retrieve search results")