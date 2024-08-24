# Groqqle.py

```python
import streamlit as st
import json
from PIL import Image
import base64
from agents.Web_Agent import Web_Agent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_groq_api_key():
    # Try to get the API key from environment variables or .env file
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        # If not found, check if it's stored in session state
        if 'groq_api_key' not in st.session_state:
            # If not in session state, prompt the user
            st.warning("Groq API Key not found. Please enter your API key below:")
            api_key = st.text_input("Groq API Key", type="password")
            if api_key:
                st.session_state.groq_api_key = api_key
        else:
            api_key = st.session_state.groq_api_key
    else:
        # If found in environment, store it in session state
        st.session_state.groq_api_key = api_key
    
    return api_key

def main():
    st.set_page_config(page_title="Groqqle Clone", layout="wide")

    # Custom CSS (same as before)
    st.markdown(""" 
    <style>
    .stApp {
        max-width: 100%;
    }
    .main {
        padding-top: 50px;
        padding-left: 20%;
        padding-right: 20%;
    }
    .stButton>button {
        background-color: #f8f9fa;
        border: 1px solid #f8f9fa;
        border-radius: 4px;
        color: #3c4043;
        font-family: arial,sans-serif;
        font-size: 14px;
        margin: 11px 4px;
        padding: 0 16px;
        line-height: 27px;
        height: 36px;
        min-width: 120px;
        text-align: center;
        cursor: pointer;
        user-select: none;
        white-space: nowrap;
        width: 100%;
    }
    .search-container {
        max-width: 600px;
        margin: 0 auto;
    }
    .search-results {
        max-width: 600px;
        margin: 0 auto;
        text-align: left;
        padding: 0;
    }
    .search-result {
        margin-bottom: 20px;
    }
    .search-result-title {
        font-size: 18px;
        color: #1a0dab;
        text-decoration: none;
    }
    .search-result-url {
        font-size: 14px;
        color: #006621;
    }
    .search-result-description {
        font-size: 14px;
        color: #545454;
    }
    </style>
    """, unsafe_allow_html=True)

    # Get Groq API Key
    api_key = get_groq_api_key()

    if not api_key:
        st.error("Please provide a valid Groq API Key to use the application.")
        return

    # Initialize Web_Agent with the API key
    agent = Web_Agent(api_key)

    # Center the content for the search bar and buttons
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    # Groqqle logo
    st.image("images/logo.png", width=272)

    # Search bar with 'Enter' key functionality
    query = st.text_input("", key="search_bar", on_change=perform_search)

    # Buttons and checkbox
    col1, col2, col3 = st.columns([2,1,2])
    with col1:
        if st.button("Groqqle Search", key="search_button"):
            perform_search()
    with col3:
        json_results = st.checkbox("JSON Results", value=False, key="json_results")

    st.markdown('</div>', unsafe_allow_html=True)

    # Display results
    if st.session_state.get('search_results'):
        display_results(st.session_state.search_results, json_results)

def perform_search():
    query = st.session_state.search_bar
    if query and 'groq_api_key' in st.session_state:
        with st.spinner('Searching...'):
            results = Web_Agent(st.session_state.groq_api_key).process_request(query)
        st.session_state.search_results = results

def display_results(results, json_format=False):
    if results:
        st.markdown("---")
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        st.markdown("### Search Results")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if json_format:
            st.json(results)
        else:
            st.markdown('<div class="search-results">', unsafe_allow_html=True)
            for result in results:
                st.markdown(f"""
                <div class="search-result">
                    <a href="{result['url']}" class="search-result-title" target="_blank">{result['title']}</a>
                    <div class="search-result-url">{result['url']}</div>
                    <div class="search-result-description">{result['description']}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("No results found.")

if __name__ == "__main__":
    main()
```

# agents\Base_Agent.py

```python
from abc import ABC, abstractmethod
from typing import Any
from providers.provider_factory import ProviderFactory

class Base_Agent(ABC):
    def __init__(self, api_key):
        self.provider = ProviderFactory.get_provider(api_key)
        self.model = ProviderFactory.get_model()

    @abstractmethod
    def process_request(self, request: str) -> Any:
        """
        Process the user's request and return a response.
        
        Args:
        request (str): The user's request to be processed.
        
        Returns:
        Any: The processed response.
        """
        pass

    def _create_summary_prompt(self, content: str, user_request: str) -> str:
        """
        Create a summary prompt for the LLM provider.
        
        Args:
        content (str): The content to be summarized.
        user_request (str): The original user request.
        
        Returns:
        str: The formatted summary prompt.
        """
        return f"""
        Given the following content:
        {content}

        Respond to the user's request: "{user_request}"
        
        Provide a concise and relevant summary that directly addresses the user's request.
        """

    def _summarize_content(self, content: str, user_request: str) -> str:
        """
        Summarize the given content using the LLM provider.
        
        Args:
        content (str): The content to be summarized.
        user_request (str): The original user request.
        
        Returns:
        str: The summarized content.
        """
        summary_prompt = self._create_summary_prompt(content, user_request)
        return self.provider.generate(summary_prompt)
```

# agents\Web_Agent.py

```python
import os
from tools.web_tools.WebSearch_Tool import WebSearch_Tool
from tools.web_tools.WebGetContents_Tool import WebGetContents_Tool
from tools.web_tools.WebGetLinks_Tool import WebGetLinks_Tool
from agents.Base_Agent import Base_Agent
from providers.provider_factory import ProviderFactory

class Web_Agent(Base_Agent):
    SKIP_DOMAINS = [
        'reddit.com',
        # Add more domains to skip here
    ]

    def __init__(self, api_key):
        super().__init__(api_key)
        self.tools = self._initialize_tools()

    def process_request(self, user_request: str) -> list:
        """
        Process the user's request and return a response.
        
        Args:
        user_request (str): The user's request to be processed.
        
        Returns:
        list: The processed response as a list of search result dictionaries.
        """
        try:
            return self._process_web_search(user_request)
        except Exception as e:
            if os.environ.get('DEBUG') == 'True':
                print(f"Error in Web_Agent: {str(e)}")
            return [{"title": "Error", "url": "", "description": f"An error occurred while processing your request: {str(e)}"}]

    def _process_web_search(self, user_request: str) -> list:
        search_results = self._perform_web_search(user_request)
        if not search_results:
            return [{"title": "No Results", "url": "", "description": "I'm sorry, but I couldn't find any relevant information for your request."}]

        filtered_results = self._filter_search_results(search_results)
        if not filtered_results:
            return [{"title": "No Results", "url": "", "description": "I found some results, but they were all from domains I've been instructed to skip. Could you try rephrasing your request?"}]

        return filtered_results[:10]  # Return top 10 results

    def _initialize_tools(self):
        return {
            "WebSearch_Tool": WebSearch_Tool,
            "WebGetContents_Tool": WebGetContents_Tool,
            "WebGetLinks_Tool": WebGetLinks_Tool
        }

    def _perform_web_search(self, query: str):
        return self.tools["WebSearch_Tool"](query, 10)  # Request 10 results

    def _filter_search_results(self, results):
        return [result for result in results if not any(domain in result['url'] for domain in self.SKIP_DOMAINS)]


    def _get_web_content(self, url: str) -> str:
        return self.tools["WebGetContents_Tool"](url)

    def _summarize_web_content(self, content: str, user_request: str, url: str, description: str) -> str:
        summary_prompt = self._create_summary_prompt(content, user_request, url, description)
        return self.provider.generate(summary_prompt)

    def _create_summary_prompt(self, content: str, user_request: str, url: str, description: str) -> str:
        return f"""
        Given the following web content from {url}:
        Description: {description}
        Content: {content[:2000]}  # Limit content to first 2000 characters to avoid exceeding token limits

        Respond to the user's request: "{user_request}"
        
        Provide a concise and relevant summary that directly addresses the user's request.
        Use simple, direct language and focus only on the most pertinent information.
        """

    def _combine_summaries(self, summaries: list, user_request: str) -> str:
        combined_prompt = f"""
        Given the following summaries from multiple sources:
        {' '.join(summaries)}

        Respond to the user's request: "{user_request}"
        
        Provide a concise, coherent response that addresses the user's request using the information from the summaries.
        Focus on the most relevant and important points, and present the information in a clear and organized manner.
        """
        return self.provider.generate(combined_prompt)
```

# providers\anthropic_provider.py

```python
import anthropic
import os
from typing import Dict, Any

from providers.base_provider import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is not set in environment variables")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        data = {
            "model": os.environ.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620'),
            "messages": [{"role": "user", "content": prompt}]
        }
        response = self.send_request(data)
        processed_response = self.process_response(response)
        return processed_response['choices'][0]['message']['content']

    def get_available_models(self) -> Dict[str, int]:
        return {
            "claude-3-5-sonnet-20240620": 4096,
            "claude-3-opus-20240229": 4096,
            "claude-3-sonnet-20240229": 4096,
            "claude-3-haiku-20240307": 4096,
            "claude-2.1": 100000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000,
        }
                
    def process_response(self, response: Any) -> Dict[str, Any]:
        if response is not None:
            return {
                "choices": [
                    {
                        "message": {
                            "content": response.content[0].text
                        }
                    }
                ]
            }
        return None
    
    def send_request(self, data: Dict[str, Any]) -> Any:
        try:
            model = data['model']
            max_tokens = min(data.get('max_tokens', 4096), self.get_available_models()[model])
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=data.get('temperature', 0.1),
                messages=[
                    {"role": "user", "content": message["content"]}
                    for message in data['messages']
                ]
            )
            return response
        except anthropic.APIError as e:
            if os.environ.get('DEBUG') == 'True':
                print(f"Anthropic API error: {e}")
            raise Exception(f"Anthropic API error: {str(e)}")
```

# providers\base_provider.py

```python

from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    def send_request(self, data):
        pass

    @abstractmethod
    def process_response(self, response):
        pass
    
```

# providers\groq_provider.py

```python
import json
import os
import requests

from providers.base_provider import BaseLLMProvider

DEBUG = os.environ.get('DEBUG') == 'True'

class Groq_Provider(BaseLLMProvider):
    def __init__(self, api_url=None):
        self.api_key = os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key is not set in environment variables")
        self.api_url = api_url or "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt):
        data = {
            "model": os.environ.get('GROQ_MODEL', 'mixtral-8x7b-32768'),
            "messages": [{"role": "user", "content": prompt}]
        }
        response = self.send_request(data)
        processed_response = self.process_response(response)
        return processed_response['choices'][0]['message']['content']

    def get_available_models(self):
        if DEBUG:
            print("GROQ: get_available_models")
        response = requests.get("https://api.groq.com/openai/v1/models", headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        if response.status_code == 200:
            models = response.json().get("data", [])
            return [model["id"] for model in models]
        else:
            raise Exception(f"Failed to retrieve models: {response.status_code}")

    def process_response(self, response):
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed with status code {response.status_code}")

    def send_request(self, data):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        json_data = json.dumps(data) if isinstance(data, dict) else data
        response = requests.post(self.api_url, data=json_data, headers=headers)
        return response
```

# providers\provider_factory.py

```python
import os
from providers.groq_provider import Groq_Provider

class ProviderFactory:
    @staticmethod
    def get_provider(api_key):
        return Groq_Provider(api_key)

    @staticmethod
    def get_model():
        return os.environ.get('DEFAULT_MODEL', 'mixtral-8x7b-32768')
```

# tools\Base_Tool.py

```python
# tools/Base_Tool.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Base_Tool(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the tool's main functionality.
        
        Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        Any: The result of the tool's execution.
        """
        pass

    def _validate_input(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Validate the input data for the tool.
        
        Args:
        data (Dict[str, Any]): The input data to validate.
        
        Returns:
        Optional[str]: An error message if validation fails, None otherwise.
        """
        return None

    def _format_output(self, result: Any) -> Dict[str, Any]:
        """
        Format the output of the tool execution.
        
        Args:
        result (Any): The raw result of the tool execution.
        
        Returns:
        Dict[str, Any]: The formatted output.
        """
        return {"result": result}

    def _handle_error(self, error: Exception) -> str:
        """
        Handle and format any errors that occur during tool execution.
        
        Args:
        error (Exception): The error that occurred.
        
        Returns:
        str: A formatted error message.
        """
        return f"An error occurred: {str(error)}"
```

# tools\web_tools\Weather_US_Tool.py

```python
# tools/web_tools/Weather_US_Tool.py

# Fetches weather information for a given US city or city/state combination.

import os
import sys
import requests
from typing import Dict, Any, Optional
from urllib.parse import quote_plus

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.Base_Tool import Base_Tool
DEBUG = os.environ.get('DEBUG') == 'True'

class Weather_US_Tool(Base_Tool):
    BASE_URL = "https://weathermateplus.com/api/location/"

    def execute(self, address: str) -> Dict[str, Any]:
        """
        Fetches weather information for a given US city or city/state combination.

        Args:
        address (str): The city or city/state combination to fetch weather for.

        Returns:
        Dict[str, Any]: A dictionary containing the weather information or an error message.
        """
        try:
            encoded_address = quote_plus(address)
            url = f"{self.BASE_URL}?address={encoded_address}"
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            return self._format_output(self._extract_relevant_data(data))
        except requests.RequestException as e:
            return self._handle_error(f"Error fetching weather data: {str(e)}")
        except KeyError as e:
            return self._handle_error(f"Error parsing weather data: {str(e)}")

    def _validate_input(self, data: Dict[str, str]) -> Optional[str]:
        if 'address' not in data:
            return "Address is required."
        if not isinstance(data['address'], str):
            return "Address must be a string."
        return None

    def _extract_relevant_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "location": data["location"],
            "currentObservation": data["currentObservation"],
            "day1": data["days"][0] if data["days"] else None
        }

    def _format_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        formatted = {
            "location": result["location"]["areaDescription"],
            "current": {
                "temperature": result["currentObservation"]["temperature"],
                "weather": result["currentObservation"]["weather"],
                "windSpeed": result["currentObservation"]["windSpeed"],
                "windDirection": result["currentObservation"]["windDirection"],
            },
            "forecast": {}
        }

        if result["day1"]:
            formatted["forecast"] = {
                "temperature": result["day1"]["temperature"],
                "shortForecast": result["day1"]["shortForecast"],
                "windSpeed": result["day1"]["windSpeed"],
                "windDirection": result["day1"]["windDirection"],
                "precipitationProbability": result["day1"]["probabilityOfPrecipitation"],
            }

        return formatted

    def _handle_error(self, error_message: str) -> Dict[str, str]:
        if DEBUG:
            print(f"Weather_US_Tool error: {error_message}")
        return {"error": error_message, "status": "error"}

if __name__ == "__main__":
    tool = Weather_US_Tool()
    address = input("Enter a US city or city, state: ")
    result = tool.execute(address)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Weather for {result['location']}:")
        print(f"Current: {result['current']['temperature']}°F, {result['current']['weather']}")
        print(f"Wind: {result['current']['windSpeed']} mph {result['current']['windDirection']}")
        print("\nForecast:")
        print(f"Temperature: {result['forecast']['temperature']}°F")
        print(f"Conditions: {result['forecast']['shortForecast']}")
        print(f"Wind: {result['forecast']['windSpeed']} {result['forecast']['windDirection']}")
        print(f"Precipitation Probability: {result['forecast']['precipitationProbability']}")
```

# tools\web_tools\WebGetContents_Tool.py

```python
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
        'Accept-Language': 'en-US,en;q=0.5',
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
```

# tools\web_tools\WebGetLinks_Tool.py

```python
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
```

# tools\web_tools\WebGetStocks_Tool.py

```python
import requests
import os
import sys
from bs4 import BeautifulSoup
from typing import Dict, Optional
import random
import time
import unittest
from unittest.mock import patch, Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.Base_Tool import Base_Tool

class WebGetStocks_Tool(Base_Tool):
    def execute(self, symbol: str) -> Optional[Dict[str, str]]:
        """
        Retrieves stock information for a given symbol from MarketWatch.

        Args:
        symbol (str): The stock symbol to look up.

        Returns:
        Optional[Dict[str, str]]: A dictionary containing the stock information, or None if an error occurs.
        """
        session = requests.Session()

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        ]

        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            session.get("https://www.marketwatch.com/", headers=headers, timeout=10)
        except requests.RequestException as e:
            return self._handle_error(f"Error accessing MarketWatch home page: {str(e)}")

        time.sleep(random.uniform(1, 3))

        url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            intraday_element = soup.find('div', class_='element element--intraday')
            
            if not intraday_element:
                return self._handle_error(f"Could not find intraday element for {symbol}")
            
            stock_info = {
                'symbol': symbol.upper(),
                'last_price': self._safe_find(intraday_element, 'bg-quote', class_='value'),
                'change': self._safe_find(intraday_element, 'span', class_='change--point--q'),
                'change_percent': self._safe_find(intraday_element, 'span', class_='change--percent--q'),
                'volume': self._safe_find(intraday_element, 'span', class_='volume__value'),
                'last_updated': self._safe_find(intraday_element, 'span', class_='timestamp__time'),
                'close_price': self._safe_find(intraday_element, 'td', class_='table__cell u-semi'),
                'close_change': self._safe_find_nth(intraday_element, 'td', class_='table__cell', n=1),
                'close_change_percent': self._safe_find_nth(intraday_element, 'td', class_='table__cell', n=2)
            }
            
            # Remove any None values
            stock_info = {k: v for k, v in stock_info.items() if v is not None}
            
            return self._format_output(stock_info)
        
        except requests.RequestException as e:
            return self._handle_error(f"Error retrieving stock information for {symbol}: {str(e)}")

    def _safe_find(self, element, tag, class_=None, default='N/A'):
        """Safely find an element and return its text, or a default value if not found."""
        found = element.find(tag, class_=class_)
        return found.text.strip() if found else default

    def _safe_find_nth(self, element, tag, class_=None, n=0, default='N/A'):
        """Safely find the nth occurrence of an element and return its text, or a default value if not found."""
        found = element.find_all(tag, class_=class_)
        return found[n].text.strip() if len(found) > n else default

    def _validate_input(self, data: Dict[str, str]) -> Optional[str]:
        if 'symbol' not in data:
            return "Stock symbol is required."
        if not isinstance(data['symbol'], str) or len(data['symbol']) > 5:
            return "Invalid stock symbol format."
        return None

    def _format_output(self, result: Dict[str, str]) -> Dict[str, str]:
        return result  # The result is already in the desired format

    def _handle_error(self, error_message: str) -> Dict[str, str]:
        return {"error": error_message}

class TestWebGetStocksTool(unittest.TestCase):
    def setUp(self):
        self.tool = WebGetStocks_Tool()
        self.test_symbol = "AAPL"
        self.mock_html = """
        <div class="element element--intraday">
            <bg-quote class="value">150.00</bg-quote>
            <span class="change--point--q">+2.50</span>
            <span class="change--percent--q">+1.69%</span>
            <span class="volume__value">50,000,000</span>
            <span class="timestamp__time">4:00PM EDT</span>
            <td class="table__cell u-semi">147.50</td>
            <td class="table__cell">+2.50</td>
            <td class="table__cell">+1.69%</td>
        </div>
        """

    @patch('requests.Session')
    def test_successful_stock_retrieval(self, mock_session):
        mock_response = Mock()
        mock_response.text = self.mock_html
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.tool.execute(self.test_symbol)

        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['last_price'], '150.00')
        self.assertEqual(result['change'], '+2.50')
        self.assertEqual(result['change_percent'], '+1.69%')
        self.assertEqual(result['volume'], '50,000,000')

    @patch('requests.Session')
    def test_request_exception(self, mock_session):
        mock_session.return_value.get.side_effect = requests.RequestException("Connection error")

        result = self.tool.execute(self.test_symbol)

        self.assertIn('error', result)
        self.assertIn('Connection error', result['error'])

    @patch('requests.Session')
    def test_missing_intraday_element(self, mock_session):
        mock_response = Mock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.tool.execute(self.test_symbol)

        self.assertIn('error', result)
        self.assertIn('Could not find intraday element', result['error'])

    def test_validate_input_valid(self):
        data = {"symbol": "AAPL"}
        result = self.tool._validate_input(data)
        self.assertIsNone(result)

    def test_validate_input_missing_symbol(self):
        data = {}
        result = self.tool._validate_input(data)
        self.assertEqual(result, "Stock symbol is required.")

    def test_validate_input_invalid_symbol(self):
        data = {"symbol": "TOOLONG"}
        result = self.tool._validate_input(data)
        self.assertEqual(result, "Invalid stock symbol format.")

    def test_safe_find(self):
        soup = BeautifulSoup(self.mock_html, 'html.parser')
        element = soup.find('div', class_='element element--intraday')
        result = self.tool._safe_find(element, 'bg-quote', class_='value')
        self.assertEqual(result, '150.00')

    def test_safe_find_nth(self):
        soup = BeautifulSoup(self.mock_html, 'html.parser')
        element = soup.find('div', class_='element element--intraday')
        result = self.tool._safe_find_nth(element, 'td', class_='table__cell', n=1)
        self.assertEqual(result, '+2.50')

    def test_format_output(self):
        input_data = {'symbol': 'AAPL', 'last_price': '150.00'}
        result = self.tool._format_output(input_data)
        self.assertEqual(result, input_data)

    def test_handle_error(self):
        error_message = "Test error"
        result = self.tool._handle_error(error_message)
        self.assertEqual(result, {"error": "Test error"})

def print_example_command():
    print("\nExample command line to run the WebGetStocks_Tool:")
    print("python tools/web_tools/WebGetStocks_Tool.py AAPL")
    print("\n\r Running tests on this tool...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If arguments are provided, do not run the tests
        symbol = sys.argv[1]
        tool = WebGetStocks_Tool()
        result = tool.execute(symbol)
        print(result)
    else:
        # If no arguments, run the tests
        print_example_command()
        unittest.main()
        

```

# tools\web_tools\WebSearch_Tool.py

```python
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
```

