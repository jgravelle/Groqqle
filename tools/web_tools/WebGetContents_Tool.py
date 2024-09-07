# tools/web_tools/WebGetContents_Tool.py

# Returns the text content of a web page given its URL
# No API key required

import os
import requests
import sys
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEBUG = os.environ.get('DEBUG') == 'True'

def WebGetContents_Tool(URL):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.0',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        if DEBUG:
            print(f"Successfully retrieved content from {URL}")
            print(f"Content preview: {text[:4000]}...")

        return text

    except requests.RequestException as e:
        error_message = f"Error retrieving content from {URL}: {str(e)}"
        if DEBUG:
            print(error_message)
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: WebGetContents_Tool.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    content = WebGetContents_Tool(url)
    if content:
        print(content)  # Print first 500 characters
    else:
        print("Failed to retrieve content")