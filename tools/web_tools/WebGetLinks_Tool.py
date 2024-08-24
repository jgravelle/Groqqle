# tools/web_tools/WebGetLinks_Tool.py

# Extracts links from a web page using BeautifulSoup
# No API key required

import os
import requests
import sys

from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEBUG = os.environ.get('DEBUG') == 'True'

def WebGetLinks_Tool(URL):
    try:
        # Set a user tool to mimic a web browser
        headers = {
            'User-Tool': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Send a GET request to the specified URL
        response = requests.get(URL, headers=headers)

        # Raise an exception for bad status codes
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <a> tags and extract text and href
        links = []
        for a in soup.find_all('a', href=True):
            text = a.text.strip()
            target = a['href']
            links.append((text, target))

        if DEBUG:
            print(f"Found {len(links)} links on the page")
            for text, target in links:
                print(f"Text: {text}")
                print(f"Target: {target}")

        return links

    except requests.RequestException as e:
        # Handle any exceptions that occur during the request
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: WebGetLinks_Tool.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    links = WebGetLinks_Tool(url)

    if isinstance(links, str):
        print(links)  # Print error message if any
    else:
        for text, target in links:
            print(f"Text: {text}")
            print(f"Target: {target}")
            print("---")