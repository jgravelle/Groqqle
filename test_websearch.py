import os
import sys
from tools.web_tools.WebSearch_Tool import WebSearch_Tool, log_debug

# Enable debug mode
os.environ['DEBUG'] = 'True'

def main():
    """Test the WebSearch_Tool with a simple query"""
    print("Testing WebSearch_Tool with Selenium implementation")
    
    # Check if selenium is installed
    try:
        import selenium
        print(f"Selenium is installed (version: {selenium.__version__})")
    except ImportError:
        print("Selenium is not installed. Please install it with: pip install selenium")
        print("Exiting test...")
        return
    
    # Check if webdriver is available
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("Selenium webdriver module is available")
    except ImportError:
        print("Selenium webdriver module is not available")
        return
    
    query = "test query"
    print(f"\nTesting search with query: '{query}'")
    
    results = WebSearch_Tool(query)
    
    if results:
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Description: {result.get('description', 'No description')[:100]}...")
    else:
        print("\nNo results found or an error occurred.")
        print("This could be due to:")
        print("1. WebDriver not installed (Chrome or Firefox driver)")
        print("2. Browser not installed (Chrome or Firefox)")
        print("3. Google blocking automated access")
        print("\nPlease make sure you have Chrome or Firefox installed along with the appropriate WebDriver.")

if __name__ == "__main__":
    main()