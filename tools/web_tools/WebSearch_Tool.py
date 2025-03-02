import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEBUG = os.environ.get('DEBUG') == 'True'

def log_debug(message):
    if DEBUG:
        print(message)

def create_driver():
    """Create and configure a headless Chrome browser using webdriver-manager"""
    log_debug("Setting up Chrome WebDriver...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Add additional options to make the browser appear more human-like
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    try:
        log_debug("Attempting to create Chrome WebDriver...")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        
        log_debug("Chrome WebDriver created successfully")
        return driver
    except Exception as e:
        log_debug(f"Error creating Chrome driver: {str(e)}")
        log_debug("Falling back to Firefox...")
        
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            firefox_options.set_preference("dom.webdriver.enabled", False)
            firefox_options.set_preference("useAutomationExtension", False)
            
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
            log_debug("Firefox WebDriver created successfully")
            return driver
        except Exception as e2:
            log_debug(f"Error creating Firefox driver: {str(e2)}")
            raise Exception("Could not initialize any webdriver. Make sure Chrome or Firefox is installed.")

def WebSearch_Tool(query: str, num_results: int = 10):
    """
    Perform a Google search using either Selenium (local) or a direct API (cloud).
    
    Args:
        query: The search query string
        num_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing search results with title, url, and description
    """
    # First try to detect if we're running in a cloud environment
    is_cloud = False
    try:
        import os
        # Check for common cloud environment variables
        if any(env in os.environ for env in ['STREAMLIT_SHARING', 'STREAMLIT_CLOUD']):
            is_cloud = True
        
        # Also check if we can create a driver as a fallback detection method
        if not is_cloud:
            try:
                test_driver = create_driver()
                test_driver.quit()
            except Exception:
                is_cloud = True
    except Exception:
        # If detection fails, assume cloud to be safe
        is_cloud = True

    if is_cloud:
        log_debug("Running in cloud environment, using API fallback")
        return _api_search(query, num_results)
    else:
        log_debug("Running in local environment, using Selenium")
        return _selenium_search(query, num_results)

def _api_search(query: str, num_results: int = 10):
    """Use a simple API-based approach for cloud environments"""
    log_debug(f"Performing API search for query: {query}")
    
    try:
        import requests
        import os
        import json
        from urllib.parse import quote_plus
        from bs4 import BeautifulSoup
        import time
        import random
        
        # Try Google Search scraping with a simplified approach (no JavaScript required)
        try:
            # Format the query for Google search
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num={min(num_results + 5, 20)}"
            
            # Set up headers to look like a normal browser request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0"
            }
            
            log_debug(f"Attempting direct Google search at: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                log_debug("Google search responded with 200 status")
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract search results
                results = []
                for result_div in soup.select("div.g"):
                    # Find title and URL
                    title_elem = result_div.select_one("h3")
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Find the URL
                    link_elem = result_div.select_one("a")
                    if not link_elem or not link_elem.has_attr("href"):
                        continue
                    
                    url = link_elem["href"]
                    if not url.startswith("http"):
                        continue
                    
                    # Find the description
                    desc_elem = result_div.select_one("div.VwiC3b") or result_div.select_one("span.aCOpRe")
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "description": description
                    })
                    
                    if len(results) >= num_results:
                        break
                
                if results:
                    log_debug(f"Successfully scraped {len(results)} results from Google")
                    return results
                else:
                    log_debug("No results found in Google search response")
            else:
                log_debug(f"Google search request failed with status code: {response.status_code}")
                
        except Exception as e:
            log_debug(f"Google search scraping failed: {str(e)}")
        
        # Try Bing API (if key is available)
        try:
            # Check for Bing API key in streamlit secrets or environment variables
            bing_api_key = None
            import streamlit as st
            if hasattr(st, 'secrets') and 'BING_API_KEY' in st.secrets:
                bing_api_key = st.secrets['BING_API_KEY']
            else:
                bing_api_key = os.environ.get("BING_API_KEY", "")
                
            if bing_api_key:
                log_debug("Attempting Bing API search")
                # Format for Bing Search API
                search_url = "https://api.bing.microsoft.com/v7.0/search"
                headers = {"Ocp-Apim-Subscription-Key": bing_api_key}
                params = {"q": query, "count": num_results, "responseFilter": "Webpages"}
                
                response = requests.get(search_url, headers=headers, params=params)
                response.raise_for_status()
                search_data = response.json()
                
                results = []
                for item in search_data.get("webPages", {}).get("value", []):
                    results.append({
                        "title": item.get("name", "No title"),
                        "url": item.get("url", ""),
                        "description": item.get("snippet", "")
                    })
                
                if results:
                    log_debug(f"Successfully retrieved {len(results)} results from Bing API")
                    return results
            else:
                log_debug("No Bing API key found")
        except Exception as e:
            log_debug(f"Bing API search failed: {str(e)}")
        
        # Try a more reliable fallback - modified web scraping with increased robustness
        try:
            log_debug("Attempting fallback to alternative search")
            # Randomly choose between several search URLs to avoid detection
            search_engines = [
                f"https://search.brave.com/search?q={quote_plus(query)}&source=web",
                f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}",
                f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            ]
            
            search_url = random.choice(search_engines)
            log_debug(f"Selected search engine URL: {search_url}")
            
            # Randomize the user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
            ]
            
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            # Different parsers for different engines
            if "duckduckgo" in search_url:
                # DuckDuckGo Lite parser
                for item in soup.select(".result"):
                    a_tag = item.select_one("a.result__a")
                    if not a_tag:
                        continue
                        
                    title = a_tag.get_text(strip=True)
                    url = a_tag["href"]
                    
                    # Extract description - approach varies by engine
                    desc_elem = item.select_one(".result__snippet")
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "description": description
                    })
                    
                    if len(results) >= num_results:
                        break
            
            elif "brave" in search_url:
                # Brave search parser
                for item in soup.select(".snippet"):
                    a_tag = item.select_one(".snippet-title a")
                    if not a_tag:
                        continue
                        
                    title = a_tag.get_text(strip=True)
                    url = a_tag["href"]
                    
                    desc_elem = item.select_one(".snippet-description")
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "description": description
                    })
                    
                    if len(results) >= num_results:
                        break
            
            if results:
                log_debug(f"Successfully retrieved {len(results)} results from fallback search")
                return results
            
        except Exception as e:
            log_debug(f"Alternative search fallback failed: {str(e)}")
        
        # Try another ultra-minimal approach with DDG JSON API
        try:
            log_debug("Attempting DDG JSON API")
            ddg_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json"
            response = requests.get(ddg_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract from RelatedTopics
            for result in data.get("RelatedTopics", [])[:num_results]:
                if "Text" in result and "FirstURL" in result:
                    # Attempt to extract a title and description
                    text = result.get("Text", "")
                    title_end = text.find(" - ")
                    
                    if title_end > 0:
                        title = text[:title_end].strip()
                        description = text[title_end+3:].strip()
                    else:
                        # If no separator, use the first 50 chars as title
                        title = text[:50] + ("..." if len(text) > 50 else "")
                        description = text
                    
                    results.append({
                        "title": title,
                        "url": result["FirstURL"],
                        "description": description
                    })
            
            if results:
                log_debug(f"Successfully retrieved {len(results)} results from DDG JSON API")
                return results
                
        except Exception as e:
            log_debug(f"DDG JSON API fallback failed: {str(e)}")
        
        # Last resort: Generate search results with direct links
        log_debug("All search methods failed, returning generated results")
        return [
            {
                "title": f"Google Search: {query}",
                "url": f"https://www.google.com/search?q={quote_plus(query)}",
                "description": f"Search Google for information about '{query}'. Click this link to see search results directly."
            },
            {
                "title": f"Bing Search: {query}",
                "url": f"https://www.bing.com/search?q={quote_plus(query)}",
                "description": f"Search Bing for information about '{query}'. Click this link to see search results directly."
            },
            {
                "title": f"DuckDuckGo Search: {query}",
                "url": f"https://duckduckgo.com/?q={quote_plus(query)}",
                "description": f"Search DuckDuckGo for information about '{query}'. Click this link to see search results directly."
            }
        ]
            
    except Exception as e:
        log_debug(f"API search fallback error: {str(e)}")
        # Return a generic result with the query so users can at least get something
        return [
            {
                "title": f"Search failed: {query}",
                "url": f"https://www.google.com/search?q={quote_plus(query)}",
                "description": f"We encountered an error retrieving search results. Click here to search Google directly for '{query}'."
            }
        ]

def _selenium_search(query: str, num_results: int = 10):
    """Original Selenium-based search implementation for local environments"""
    search_url = f"https://www.google.com/search?q={query}&num={num_results}"
    log_debug(f"Search URL: {search_url}")
    
    driver = None
    try:
        driver = create_driver()
        log_debug("WebDriver created successfully")
        
        # Load the search page
        driver.get(search_url)
        log_debug(f"Navigated to {search_url}")
        
        # Save the page source for debugging
        if DEBUG:
            with open("google_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            log_debug("Saved initial page source to google_page_source.html")
            driver.save_screenshot("google_initial.png")
            log_debug("Saved initial screenshot to google_initial.png")
        
        # Wait for search results to load
        try:
            # Try different selectors that might indicate search results
            selectors = [
                "div.g", 
                "div[data-hveid]", 
                "div.yuRUbf", 
                "div.MjjYud",
                "h3",
                "a[href^='http']"
            ]
            
            for selector in selectors:
                try:
                    log_debug(f"Waiting for selector: {selector}")
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    log_debug(f"Found elements matching selector: {selector}")
                    break
                except TimeoutException:
                    log_debug(f"Timeout waiting for selector: {selector}")
            
            # Give a little extra time for JavaScript to execute
            log_debug("Waiting for page to fully render...")
            time.sleep(3)
            
            # Save the page source after waiting
            if DEBUG:
                with open("google_page_source_after_wait.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                log_debug("Saved page source after wait to google_page_source_after_wait.html")
                driver.save_screenshot("google_after_wait.png")
                log_debug("Saved screenshot after wait to google_after_wait.png")
            
        except Exception as e:
            log_debug(f"Exception during wait: {str(e)}")
        
        # Get the page source after JavaScript execution
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if we're being blocked or getting a CAPTCHA
        if "unusual traffic" in html_content.lower() or "captcha" in html_content.lower():
            log_debug("Google is showing a CAPTCHA or unusual traffic warning")
            if DEBUG:
                driver.save_screenshot("google_captcha.png")
            return []
        
        search_results = []
        
        # Try different selectors based on Google's current layout
        result_selectors = [
            'div.g', 
            'div.tF2Cxc', 
            'div.yuRUbf', 
            'div.MjjYud',
            'div[data-sokoban-container]',
            'div[data-header-feature="0"]'
        ]
        
        found_results = False
        for selector in result_selectors:
            result_elements = soup.select(selector)
            log_debug(f"Selector '{selector}' found {len(result_elements)} elements")
            
            if result_elements:
                found_results = True
                for element in result_elements:
                    # Try to find the title and URL
                    title_element = element.select_one('h3')
                    link_element = element.select_one('a')
                    
                    if not title_element or not link_element:
                        continue
                        
                    title = title_element.get_text(strip=True)
                    url = link_element.get('href', '')
                    
                    # Skip non-http URLs or Google internal links
                    if not url.startswith('http'):
                        continue
                        
                    # Try to find the description
                    description = ""
                    # Try different description selectors
                    desc_selectors = [
                        'div.VwiC3b', 'div.yXK7lf', 'span.st', 'div.s', 
                        'div[data-content-feature="1"]', 'div.IsZvec'
                    ]
                    
                    for desc_selector in desc_selectors:
                        desc_element = element.select_one(desc_selector)
                        if desc_element:
                            description = desc_element.get_text(strip=True)
                            break
                    
                    # If no description found, try to get any text content
                    if not description:
                        # Exclude the title from the description
                        for text_element in element.find_all(text=True):
                            if text_element.parent != title_element and text_element.strip():
                                description += text_element.strip() + " "
                        description = description.strip()
                    
                    search_results.append({
                        'title': title,
                        'url': url,
                        'description': description
                    })
                    
                    # Stop once we have enough results
                    if len(search_results) >= num_results:
                        break
                
                # If we found results with this selector, no need to try others
                if search_results:
                    break
        
        # If no results found with the main selectors, try a more generic approach
        if not found_results or not search_results:
            log_debug("No results found with primary selectors, trying generic approach")
            
            # Look for any h3 elements (likely titles) and their parent links
            h3_elements = soup.select('h3')
            log_debug(f"Found {len(h3_elements)} h3 elements")
            
            for h3 in h3_elements:
                # Find the closest anchor tag
                link = h3.find_parent('a')
                if not link:
                    # Try to find a nearby anchor tag
                    parent = h3.parent
                    link = parent.find('a') if parent else None
                
                if link and link.get('href', '').startswith('http'):
                    title = h3.get_text(strip=True)
                    url = link.get('href', '')
                    
                    # Try to find a description
                    description = ""
                    parent_div = h3.find_parent('div')
                    if parent_div:
                        # Get all text in the parent div except the title
                        for text in parent_div.find_all(text=True):
                            if text.strip() and text.strip() != title:
                                description += text.strip() + " "
                    
                    search_results.append({
                        'title': title,
                        'url': url,
                        'description': description.strip()
                    })
                    
                    if len(search_results) >= num_results:
                        break
                        
        if DEBUG:
            log_debug(f"Successfully retrieved {len(search_results)} search results for query: {query}")
            if search_results:
                log_debug(f"First result: {search_results[0]}")
                
        return search_results
    
    except Exception as e:
        error_message = f"Error performing search for query '{query}': {str(e)}"
        log_debug(error_message)
        import traceback
        log_debug(traceback.format_exc())
        return []
    
    finally:
        if driver:
            driver.quit()
            log_debug("WebDriver closed")

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