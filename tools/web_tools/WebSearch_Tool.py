import requests
from bs4 import BeautifulSoup
import sys
import json

def WebSearch_Tool(query, num_results=10):
    url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('div', class_='g')
        
        results = []
        for result in search_results:
            item = {}
            
            # Extract the title
            title_element = result.find('h3', class_='LC20lb')
            if title_element:
                item['title'] = title_element.get_text(strip=True)
            else:
                continue  # Skip this result if there's no title
            
            # Extract the URL
            link_element = result.find('a')
            if link_element:
                item['url'] = link_element['href']
            else:
                continue  # Skip this result if there's no URL
            
            # Extract the description
            desc_element = result.find('div', class_='VwiC3b')
            if desc_element:
                item['description'] = desc_element.get_text(strip=True)
            else:
                item['description'] = "No description available"
            
            results.append(item)
        
        return results[:num_results]  # Ensure we don't return more than requested
    
    except requests.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: WebSearch_Tool.py <search_query> [num_results]")
        sys.exit(1)
    
    query = sys.argv[1]
    num_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    results = WebSearch_Tool(query, num_results)
    
    # Convert the results to JSON and print
    print(json.dumps(results, indent=2))