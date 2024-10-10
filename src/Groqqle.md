# Groqqle.py

```python
import argparse
import logging
import os
import re
import requests
import streamlit as st
import tldextract
import traceback

from agents.Web_Agent import Web_Agent
from agents.News_Agent import News_Agent
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from urllib.parse import quote_plus, unquote_plus, urlparse

# Load environment variables from .env file
load_dotenv()

# Set up logging only if DEBUG is True in .env
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

if DEBUG:
    logging.basicConfig(
        filename='debug_info.txt',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8',
        force=True
    )
else:
    # Set up a null handler to avoid "No handler found" warnings
    logging.getLogger().addHandler(logging.NullHandler())

def log_debug(message):
    if DEBUG:
        logging.debug(sanitize_message(message))

def sanitize_message(message):
    try:
        return message.encode("utf-8").decode("utf-8")
    except UnicodeEncodeError:
        return message.encode("ascii", "ignore").decode("ascii")

@st.cache_data
def fetch_groq_models(api_key):
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json()['data']
        return {model['id']: model for model in models}
    except Exception as e:
        log_debug(f"Error fetching Groq models: {str(e)}")
        return {
            "llama3-8b-8192": {"id": "llama3-8b-8192", "context_window": 32768},
            "llama2-70b-4096": {"id": "llama2-70b-4096", "context_window": 4096}
        }

def get_groq_api_key(api_key_arg: str = None) -> str:
    # Check URL parameters first
    query_params = st.query_params
    url_api_key = query_params.get("api_key")
    if url_api_key:
        url_api_key = unquote_plus(url_api_key)
        log_debug("API key found in URL parameters")
        st.session_state.groq_api_key = url_api_key
        st.session_state.api_key_source = 'manual'
        return url_api_key

    # Then check function argument
    if api_key_arg:
        log_debug("API key found in function argument")
        st.session_state.groq_api_key = api_key_arg
        st.session_state.api_key_source = 'argument'
        return api_key_arg

    # Then check environment variable
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        log_debug("API key found in environment variable")
        st.session_state.groq_api_key = api_key
        st.session_state.api_key_source = 'environment'
        return api_key

    # Finally, check session state
    if 'groq_api_key' in st.session_state:
        log_debug("API key retrieved from session state")
        if 'api_key_source' not in st.session_state:
            st.session_state.api_key_source = 'session'
        return st.session_state.groq_api_key
    
    # If no API key is found, initialize api_key_source
    st.session_state.api_key_source = 'none'
    return None

def is_url(text: str) -> bool:
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def validate_api_key(api_key):
    # This is a placeholder function. In a real-world scenario, you'd want to
    # make a test call to the Groq API to validate the key.
    return bool(api_key) and len(api_key) > 10

def extract_url_and_prompt(query: str):
    # Regular expression to find URLs in the query
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, query)
    
    if urls:
        image_url = urls[0]
        # Remove the URL from the query to get the custom prompt
        custom_prompt = query.replace(image_url, '').strip()
        if not custom_prompt:
            custom_prompt = "What's in this image?"
        return image_url, custom_prompt
    return None, None

def process_image(query: str, api_key: str):
    image_url, custom_prompt = extract_url_and_prompt(query)
    if not image_url:
        return None

    try:
        agent = Web_Agent(
            api_key,
            num_results=1,
            max_tokens=st.session_state.context_window,
            model="llava-v1.5-7b-4096-preview",
            temperature=st.session_state.temperature,
            comprehension_grade=st.session_state.comprehension_grade,
            summary_length=st.session_state.summary_length
        )
        results = agent._process_image_request(image_url, custom_prompt)
        if results and isinstance(results, list) and len(results) > 0:
            results[0]['prompt_used'] = custom_prompt
        return results
    except Exception as e:
        st.error(f"An error occurred while processing the image: {str(e)}")
        if os.environ.get('DEBUG') == 'True':
            st.error(traceback.format_exc())
        return [{
            "title": "Error",
            "url": image_url,
            "description": f"An error occurred while analyzing the image: {str(e)}",
            "prompt_used": custom_prompt
        }]

def update_search_type():
    if st.session_state.search_type == 'News':
        st.session_state.previous_temperature = st.session_state.temperature
        st.session_state.temperature = 0
    else:
        st.session_state.temperature = st.session_state.previous_temperature
    st.session_state.search_results = None  # Clear previous results when switching search type

def update_sidebar(models):
    with st.sidebar:
        st.title("Settings")
        
        # Move API key input to sidebar
        api_key = st.text_input("Groq API Key", type="password", key="api_key_input")
        if api_key:
            st.session_state.groq_api_key = api_key
            st.session_state.api_key_source = 'manual'
            st.session_state.models = fetch_groq_models(api_key)
        
        st.session_state.num_results = st.slider(
            "Number of Results", 
            min_value=1, 
            max_value=50, 
            value=st.session_state.num_results, 
            step=1
        )
        st.session_state.summary_length = st.slider(
            "URL Summary Length (words)", 
            min_value=50, 
            max_value=2000, 
            value=st.session_state.summary_length, 
            step=10
        )
        st.session_state.selected_model = st.selectbox(
            "Select Model", 
            list(models.keys()),
            index=list(models.keys()).index(st.session_state.selected_model) if st.session_state.selected_model in models else 0
        )

        # Context window slider
        max_context = models[st.session_state.selected_model]['context_window']
        st.session_state.context_window = st.slider(
            "Context Window",
            min_value=1024,
            max_value=max_context,
            value=min(st.session_state.context_window, max_context),
            step=1024
        )

        # Temperature slider
        if 'previous_temperature' not in st.session_state:
            st.session_state.previous_temperature = 0.0

        is_news_search = st.session_state.get('search_type', 'Web') == 'News'
        
        if is_news_search:
            st.session_state.temperature = 0
            st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.01,
                disabled=True,
                key="temp_slider"
            )
        else:
            st.session_state.temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.previous_temperature,
                step=0.01,
                key="temp_slider"
            )
            st.session_state.previous_temperature = st.session_state.temperature

        # Comprehension Grade slider
        grade_labels = [
            "1st Grade", "2nd Grade", "3rd Grade", "4th Grade", "5th Grade",
            "6th Grade", "7th Grade", "8th Grade", "9th Grade", "10th Grade",
            "11th Grade", "12th Grade", "Baccalaureate", "Masters", "PhD"
        ]
        selected_grade = st.selectbox(
            "Comprehension Grade",
            options=grade_labels,
            index=st.session_state.comprehension_grade - 1
        )
        st.session_state.comprehension_grade = grade_labels.index(selected_grade) + 1

def main(api_key_arg: str = None, num_results: int = 10, max_tokens: int = 4096, default_summary_length: int = 300):
    st.set_page_config(page_title="Groqqle", layout="wide", initial_sidebar_state="collapsed")

    # Initialize session state
    if 'num_results' not in st.session_state:
        st.session_state.num_results = num_results
    if 'summary_length' not in st.session_state:
        st.session_state.summary_length = default_summary_length
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "llama3-8b-8192"
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.0
    if 'comprehension_grade' not in st.session_state:
        st.session_state.comprehension_grade = 8
    if 'context_window' not in st.session_state:
        st.session_state.context_window = max_tokens
    if 'models' not in st.session_state:
        st.session_state.models = {
            "llama3-8b-8192": {"id": "llama3-8b-8192", "context_window": 32768},
            "llama2-70b-4096": {"id": "llama2-70b-4096", "context_window": 4096}
        }
    if 'search_type' not in st.session_state:
        st.session_state.search_type = "Web"
    if 'api_key_source' not in st.session_state:
        st.session_state.api_key_source = 'none'

    api_key = get_groq_api_key(api_key_arg)

    # Update sidebar (which now includes API key input)
    update_sidebar(st.session_state.models)

    # Main content
    st.markdown("""
    <style>
    .main-content {
        display: flex;
        justify-content: space-between;
    }
    .search-container {
        flex: 2;
        padding-right: 20px;
    }
    .image-analysis {
        flex: 1;
        padding-left: 20px;
        border-left: 1px solid #e0e0e0;
    }
    .stApp {
        max-width: 100%;
    }
    .main {
        padding-top: 20px;
        padding-left: 10%;
        padding-right: 10%;
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

    # Always display the interface, even if no API key is provided
    main_col, image_col = st.columns([3, 1])

    with main_col:
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
        # Only include the API key in the URL if it was manually entered
        logo_url = "."
        if st.session_state.api_key_source == 'manual' and api_key:
            logo_url = f"?api_key={quote_plus(api_key)}"

        clickable_image_html = f"""
            <div class="search-container" style="align:left">
                <a href="{logo_url}">
                    <img src="https://j.gravelle.us/groqqle_logo.png" width="272" />
                </a>
            </div>
            """
        st.markdown(clickable_image_html, unsafe_allow_html=True)

        query = st.text_input("Enter search criteria or a link. URLs can be for articles, web pages, foreign language content, or images.", key="search_bar")

        col1, col2, col3, col4 = st.columns([2,1,1,2])
        with col1:
            if st.button("Groqqle Search", key="search_button"):
                perform_search()
        with col2:
            search_type = st.radio("Search Type", ["Web", "News"], index=0, key="search_type", on_change=update_search_type)
        with col4:
            json_results = st.checkbox("JSON Results", value=False, key="json_results")

        if query:
            if not validate_api_key(api_key):
                st.error("Please enter a valid Groq API Key in the sidebar to use Groqqle.")
            else:
                image_url, _ = extract_url_and_prompt(query)
                if image_url:
                    with st.spinner('Analyzing image...'):
                        image_results = process_image(query, api_key)
                        if image_results:
                            st.session_state.image_analysis = image_results[0]['description']
                            st.session_state.image_url = image_url
                            st.session_state.image_prompt = image_results[0].get('prompt_used', "What's in this image?")
                elif is_url(query):
                    with st.spinner('Summarizing URL...'):
                        summary = summarize_url(query, api_key, st.session_state.comprehension_grade, st.session_state.temperature)
                        display_results([summary], json_results, api_key)
                elif 'search_results' in st.session_state and st.session_state.search_results:
                    display_results(st.session_state.search_results, json_results, api_key)
                else:
                    st.info("Enter a search query and click 'Groqqle Search' to see results.")

        st.markdown('</div>', unsafe_allow_html=True)

    with image_col:
        st.markdown('<div class="image-analysis">', unsafe_allow_html=True)
        if 'image_analysis' in st.session_state and 'image_url' in st.session_state:
            st.image(st.session_state.image_url, use_column_width=True)
            st.markdown("### IMAGE ANALYSIS")
            st.write(f"**Prompt:** {st.session_state.image_prompt}")
            st.write(st.session_state.image_analysis)
        else:
            st.markdown("### IMAGE ANALYSIS")
            st.write("No image analyzed yet. Enter an image URL with an optional question in the search bar to analyze.")
        st.markdown('</div>', unsafe_allow_html=True)

def perform_search():
    query = st.session_state.search_bar
    api_key = st.session_state.get('groq_api_key')
    num_results = st.session_state.num_results
    summary_length = st.session_state.summary_length
    selected_model = st.session_state.selected_model
    context_window = st.session_state.context_window
    temperature = 0 if st.session_state.search_type == 'News' else st.session_state.temperature
    comprehension_grade = st.session_state.comprehension_grade
    search_type = st.session_state.search_type

    log_debug(f"perform_search: comprehension_grade = {comprehension_grade}, temperature = {temperature}, search_type = {search_type}")

    if query and api_key:
        with st.spinner('Processing...'):
            log_debug(f"Processing query: {query}")
            if query.startswith(('http://', 'https://')):
                agent = Web_Agent(
                    api_key,
                    num_results=1,
                    max_tokens=context_window,
                    model=selected_model,
                    temperature=temperature,
                    comprehension_grade=comprehension_grade,
                    summary_length=summary_length
                )
                results = [summarize_url(query, api_key, comprehension_grade, temperature)]
            elif search_type == "Web":
                agent = Web_Agent(
                    api_key,
                    num_results=num_results,
                    max_tokens=context_window,
                    model=selected_model,
                    temperature=temperature,
                    comprehension_grade=comprehension_grade,
                    summary_length=summary_length
                )
                results = agent.process_request(query)
            else:  # News search
                agent = News_Agent(
                    api_key,
                    num_results=num_results,
                    max_tokens=context_window,
                    model=selected_model,
                    temperature=temperature,
                    comprehension_grade=comprehension_grade
                )
                results = agent.process_request(query)
            
            log_debug(f"Processing completed. Number of results: {len(results)}")
        st.session_state.search_results = results
    else:
        if not api_key:
            st.error("Please provide a valid Groq API Key in the sidebar to perform the search.")
        if not query:
            st.error("Please enter a search query or URL.")

def summarize_url(url, api_key, comprehension_grade, temperature):
    if not validate_api_key(api_key):
        return {"title": "API Key Required", "url": url, "description": "A valid Groq API key is required to summarize content. Please enter it in the sidebar."}
    
    summary_length = st.session_state.summary_length
    try:
        agent = Web_Agent(
            api_key,
            num_results=1,
            max_tokens=4096,
            comprehension_grade=comprehension_grade,
            temperature=temperature,
            summary_length=summary_length
        )
        log_debug(f"Web_Agent initialized for URL summary with comprehension grade: {comprehension_grade}, temperature: {temperature}, and summary_length: {summary_length}")
        summary_result = agent.process_request(url)
        if summary_result and len(summary_result) > 0:
            return summary_result[0]
        else:
            return {"title": "Summary Error", "url": url, "description": "Unable to generate summary."}
    except Exception as e:
        log_debug(f"Error in summarize_url: {str(e)}")
        return {"title": "Summary Error", "url": url, "description": f"Error generating summary: {str(e)}"}

def display_results(results, json_format=False, api_key=None):
    log_debug(f"display_results called with {len(results)} results")
    
    if results:
        st.markdown("---")
        
        if json_format:
            st.json(results)
        else:
            for index, result in enumerate(results):
                log_debug(f"Displaying result {index}: {result['url']}")
                
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(f"#### [{result['title']}]({result['url']})")
                with col2:
                    # Use a combination of index and URL to create a unique key
                    summary_button = st.button("📝", key=f"summary_{index}_{result['url']}", help="Summarize")
                
                # Determine if this is a news search result
                is_news_search = 'timestamp' in result
                
                if is_news_search:
                    # For news search, extract root domain from URL
                    ext = tldextract.extract(result['url'])
                    source = f"{ext.domain}.{ext.suffix}"
                    st.markdown(f"*Source: {source}*")
                    st.markdown(f"*Published: {result['timestamp']}*")
                else:
                    # For web search, use the original source if available
                    source = result.get('source')
                    if source and source != 'Unknown':
                        st.markdown(f"*Source: {source}*")
                    else:
                        # Fallback to domain extraction if source is not available or Unknown
                        ext = tldextract.extract(result['url'])
                        source = f"{ext.domain}.{ext.suffix}"
                        st.markdown(f"*Source: {source}*")
                
                st.markdown(result['description'])
                
                if summary_button:
                    with st.spinner("Generating summary..."):
                        summary = summarize_url(result['url'], api_key, st.session_state.comprehension_grade, st.session_state.temperature)
                        st.markdown("---")
                        st.markdown(f"##### Summary:<br/>{summary['title']}", unsafe_allow_html=True)
                        st.markdown(f"*Source: [{summary['url']}]({summary['url']})*")
                        st.markdown(summary['description'])
                        st.markdown("---")
                
                st.markdown("---")  # Add a separator between results

    else:
        st.markdown("No results found.")

def create_api_app(api_key_arg: str = None, default_num_results: int = 10, default_max_tokens: int = 4096, default_summary_length: int = 300):
    app = Flask(__name__)

    @app.route('/search', methods=['POST'])
    def api_search():
        # Check for API key in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header.split('Bearer ')[1]
        else:
            # Fallback to environment variable if no Authorization header
            api_key = api_key_arg or os.getenv('GROQ_API_KEY')

        if not api_key:
            return jsonify({"error": "No API key provided. Please include it in the Authorization header as 'Bearer YOUR_API_KEY' or set it as an environment variable."}), 401

        data = request.json
        query = data.get('query')
        num_results = data.get('num_results', default_num_results)
        max_tokens = data.get('max_tokens', default_max_tokens)
        summary_length = data.get('summary_length', default_summary_length)
        model = data.get('model', 'llama3-8b-8192')
        temperature = data.get('temperature', 0.0)
        comprehension_grade = data.get('comprehension_grade', 8)
        search_type = data.get('search_type', 'web').lower()
        custom_prompt = data.get('custom_prompt')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400

        log_debug(f"API search endpoint hit with query: {query}, num_results: {num_results}, summary_length: {summary_length}, model: {model}, max_tokens: {max_tokens}, temperature: {temperature}, comprehension_grade: {comprehension_grade}, search_type: {search_type}, custom_prompt: {custom_prompt}")
        
        try:
            agent = Web_Agent(
                api_key, 
                num_results=num_results, 
                max_tokens=max_tokens, 
                model=model,
                temperature=temperature,
                comprehension_grade=comprehension_grade,
                summary_length=summary_length
            )

            if agent._is_image_url(query):
                results = agent._process_image_request(query, custom_prompt)
            elif search_type == 'web':
                results = agent.process_request(query)
            elif search_type == 'news':
                news_agent = News_Agent(
                    api_key, 
                    num_results=num_results,
                    max_tokens=max_tokens, 
                    model=model,
                    temperature=temperature,
                    comprehension_grade=comprehension_grade
                )
                results = news_agent.process_request(query)
            else:
                return jsonify({"error": "Invalid search type. Use 'web' or 'news'."}), 400

            return jsonify(results)
        
        except Exception as e:
            log_debug(f"Error in API search: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Groqqle application.")
    parser.add_argument('mode', nargs='?', default='app', choices=['app', 'api'], help='Run mode: "app" for Streamlit app, "api" for Flask API server')
    parser.add_argument('--api_key', type=str, help='The API key for Groq.')
    parser.add_argument('--num_results', type=int, default=10, help='Number of results to return.')
    parser.add_argument('--max_tokens', type=int, default=4096, help='Maximum number of tokens for the response.')
    parser.add_argument('--port', type=int, default=5000, help='Port number for the API server (only used in API mode).')
    parser.add_argument('--default_summary_length', type=int, default=300, help='Default summary length in words.')
    args = parser.parse_args()

    if args.mode == 'app':
        log_debug("Running in app mode")
        main(args.api_key, args.num_results, args.max_tokens, args.default_summary_length)
    elif args.mode == 'api':
        log_debug(f"Running in API mode on port {args.port}")
        app = create_api_app(args.api_key, args.num_results, args.max_tokens, args.default_summary_length)

        def print_startup_message():
            print(f"\nGroqqle API is now running!")
            print(f"Send POST requests to: http://localhost:{args.port}/search")
            print("\nExample POST request body (JSON):")
            print('''
            {
                "query": "latest developments in AI",
                "num_results": 5,
                "max_tokens": 4096,
                "summary_length": 200,
                "model": "llama3-8b-8192",
                "temperature": 0.0,
                "comprehension_grade": 8,
                "search_type": "web"  // Use "web" for web search or "news" for news search
            }
            ''')

        # Only print the startup message once
        print_startup_message()

        # Run the Flask app without debug mode
        app.run(host='0.0.0.0', port=args.port)

```

# Groqqle_web_tool.py

```python
from typing import Dict, Any, List
from tools.web_tools.WebSearch_Tool import WebSearch_Tool
from tools.web_tools.WebGetContents_Tool import WebGetContents_Tool
from providers.provider_factory import ProviderFactory

class Groqqle_web_tool:
    def __init__(self, api_key: str, provider_name: str = 'groq', num_results: int = 10, max_tokens: int = 4096, model: str = "llama3-8b-8192", temperature: float = 0.0, comprehension_grade: int = 8):
        self.api_key = api_key
        self.num_results = num_results
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temperature
        self.comprehension_grade = comprehension_grade
        self.provider = ProviderFactory.get_provider(provider_name, api_key)

    def run(self, query: str) -> List[Dict[str, Any]]:
        search_results = self._perform_web_search(query)
        filtered_results = self._filter_search_results(search_results)
        deduplicated_results = self._remove_duplicates(filtered_results)
        return deduplicated_results[:self.num_results]

    def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        return WebSearch_Tool(query, self.num_results * 2)

    def _filter_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [result for result in results if result['description'] and result['title'] != 'No title' and result['url'].startswith('https://')]

    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_urls = set()
        unique_results = []
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        return unique_results

    def _summarize_web_content(self, content: str, url: str) -> Dict[str, str]:
        summary_prompt = self._create_summary_prompt(content, url)
        summary = self.provider.generate(
            summary_prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return self._format_summary(summary, url)

    def _create_summary_prompt(self, content: str, url: str) -> str:
        grade_descriptions = {
            1: "a 6-year-old in 1st grade", 2: "a 7-year-old in 2nd grade", 3: "an 8-year-old in 3rd grade",
            4: "a 9-year-old in 4th grade", 5: "a 10-year-old in 5th grade", 6: "an 11-year-old in 6th grade",
            7: "a 12-year-old in 7th grade", 8: "a 13-year-old in 8th grade", 9: "a 14-year-old in 9th grade",
            10: "a 15-year-old in 10th grade", 11: "a 16-year-old in 11th grade", 12: "a 17-year-old in 12th grade",
            13: "a college undergraduate", 14: "a master's degree student", 15: "a PhD candidate"
        }
        grade_description = grade_descriptions.get(self.comprehension_grade, "an average adult")

        return f"""
        Summarize the following web content from {url} for {grade_description}:
        {content}

        Your task is to provide a comprehensive and informative synopsis of the main subject matter, along with an SEO-optimized headline. Follow these guidelines:

        1. Generate an SEO-optimized headline that:
        - Captures user interest without sensationalism
        - Accurately represents the main topic
        - Uses relevant keywords
        - Is concise
        - Maintains professionalism
        - Does not begin with anything akin to "Imagine" or "Picture this"
        
        2. Format your headline exactly as follows:
        HEADLINE: [Your SEO-optimized headline here]

        3. Write your summary using the inverted pyramid style:
        - Start with a strong lede (opening sentence) that entices readers and summarizes the most crucial information
        - Present the most important information first
        - Follow with supporting details and context
        - End with the least essential information

        4. Adjust the language complexity strictly targeted to the reading level for {grade_description}.

        5. Clearly explain the main topic or discovery being discussed
        6. Highlight key points, findings, or arguments presented in the content
        7. Provide relevant context or background information that helps understand the topic
        8. Mention any significant implications, applications, or future directions discussed
        9. If applicable, include important quotes or statistics that support the main points

        Use a neutral, journalistic tone, and ensure that you're reporting the facts as presented in the content, not adding personal opinions or speculation.

        Format your response as follows:
        HEADLINE: [Your SEO-optimized headline here]

        [Your comprehensive summary here, following the inverted pyramid style]
        """

    def _format_summary(self, summary: str, url: str) -> Dict[str, str]:
        parts = summary.split('\n', 1)
        if len(parts) == 2 and parts[0].startswith('HEADLINE:'):
            headline = parts[0].replace('HEADLINE:', '').strip()
            body = parts[1].strip()
        else:
            sentences = summary.split('. ')
            headline = sentences[0].strip()
            body = '. '.join(sentences[1:]).strip()

        if not headline or headline == "Summary of Web Content":
            headline = f"Summary of {url.split('//')[1].split('/')[0]}"

        return {
            "title": headline,
            "url": url,
            "description": body
        }

    def summarize_url(self, url: str) -> Dict[str, str]:
        content = WebGetContents_Tool(url)
        if content:
            return self._summarize_web_content(content, url)
        else:
            return {"title": "Error", "url": url, "description": "Failed to retrieve content from the URL.  Some sites prohibit summarization.  Click URL to go there directly."}
```

# agents\Base_Agent.py

```python
# agents/Base_Agent.py

from abc import ABC, abstractmethod
from typing import Any

class Base_Agent(ABC):
    @abstractmethod
    def process_request(self, request: str) -> Any:
        pass

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

# agents\News_Agent.py

```python
import os
import sys
import requests
import time
import tldextract

from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import quote_plus, urljoin

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents.Base_Agent import Base_Agent
from providers.provider_factory import ProviderFactory

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def log_debug(message):
    if DEBUG:
        print(f"Debug: {message}")

class News_Agent(Base_Agent):
    def __init__(self, api_key, provider_name='groq', num_results=10, max_tokens=4096, model="llama3-8b-8192", temperature=0.0, comprehension_grade=8):
        log_debug(f"Initializing News_Agent with provider_name: {provider_name}, num_results: {num_results}, max_tokens: {max_tokens}, model: {model}, temperature: {temperature}, comprehension_grade: {comprehension_grade}")
        
        if not api_key:
            log_debug("API key is missing or empty")
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.num_results = num_results
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temperature
        self.comprehension_grade = comprehension_grade

        try:
            log_debug(f"Attempting to get provider with API key: {api_key[:5]}...")
            self.provider = ProviderFactory.get_provider(provider_name, api_key)
            log_debug("Provider obtained successfully")
        except Exception as e:
            log_debug(f"Error in News_Agent.__init__: {str(e)}")
            raise

    def process_request(self, user_request: str) -> List[Dict[str, Any]]:
        log_debug(f"Processing request: {user_request}")
        log_debug(f"Using comprehension grade: {self.comprehension_grade}, temperature: {self.temperature}")
        
        try:
            search_results = self._perform_news_search(user_request)
            log_debug(f"News search completed. Number of results: {len(search_results)}")
            
            if not search_results:
                log_debug("No search results found")
                return [{"title": "No Results", "url": "", "description": "I'm sorry, but I couldn't find any relevant news for your request."}]

            return search_results[:self.num_results]  # Return top num_results
        except Exception as e:
            log_debug(f"Error in process_request: {str(e)}")
            return [{"title": "Error", "url": "", "description": f"An error occurred while processing your request: {str(e)}"}]

    def _perform_news_search(self, query: str) -> List[Dict[str, Any]]:
        log_debug(f"Performing news search with query: {query} and num_results: {self.num_results}")
        
        encoded_query = quote_plus(query)
        base_url = f'https://www.bing.com/news/search?q={encoded_query}&qft=interval%3d"7"&qft=sortbydate%3d"1" '
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        results = []
        page = 1
        while len(results) < self.num_results:
            url = f"{base_url}&count={min(30, self.num_results - len(results))}&first={(page-1)*30+1}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                news_cards = soup.find_all('div', class_='news-card')
                
                if not news_cards:
                    break  # No more results found
                
                for card in news_cards:
                    if len(results) >= self.num_results:
                        break
                    
                    title_elem = card.find('a', class_='title')
                    if title_elem:
                        title = title_elem.text.strip()
                        url = urljoin("https://www.bing.com", title_elem.get('href', ''))
                        
                        snippet_elem = card.find('div', class_='snippet')
                        description = snippet_elem.text.strip() if snippet_elem else ''
                        
                        source_elem = card.find('div', class_='source')
                        source = source_elem.text.strip() if source_elem else ''
                        
                        timestamp_elem = card.find('span', attrs={'aria-label': True})
                        timestamp = timestamp_elem['aria-label'] if timestamp_elem else ''
                        
                        # Extract the root domain from the URL
                        ext = tldextract.extract(url)
                        root_domain = f"{ext.domain}.{ext.suffix}"
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "description": description,
                            "source": root_domain,  # Use the root domain as the source
                            "timestamp": timestamp
                        })
                
                page += 1
                time.sleep(1)  # Add a small delay between requests to avoid rate limiting
            except Exception as e:
                log_debug(f"Error in _perform_news_search: {str(e)}")
                break

        log_debug(f"News search completed successfully. Number of results: {len(results)}")
        return results[:self.num_results] 

    def _summarize_news_content(self, content: str, url: str) -> Dict[str, str]:
        log_debug(f"Summarizing content from URL: {url}")
        summary_prompt = self._create_summary_prompt(content, url)
        log_debug(f"Summary prompt: {summary_prompt[:500]}...")  # Log first 500 characters of the prompt
        summary = self.provider.generate(
            summary_prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return self._format_summary(summary, url)

    def _create_summary_prompt(self, content: str, url: str) -> str:
        grade_descriptions = {
            1: "a 6-year-old in 1st grade", 2: "a 7-year-old in 2nd grade", 3: "an 8-year-old in 3rd grade",
            4: "a 9-year-old in 4th grade", 5: "a 10-year-old in 5th grade", 6: "an 11-year-old in 6th grade",
            7: "a 12-year-old in 7th grade", 8: "a 13-year-old in 8th grade", 9: "a 14-year-old in 9th grade",
            10: "a 15-year-old in 10th grade", 11: "a 16-year-old in 11th grade", 12: "a 17-year-old in 12th grade",
            13: "a college undergraduate", 14: "a master's degree student", 15: "a PhD candidate"
        }
        grade_description = grade_descriptions.get(self.comprehension_grade, "an average adult")

        log_debug(f"Selected grade description: {grade_description}")

        return f"""
            Summarize the following news content from {url} for {grade_description}:
            {content} 

            Your task is to write a new, comprehensive and informative article by creating original synopses of the main subject matter, along with an SEO-optimized headline. Your writing must stand alone as its own independent news article, without mentioning the original source, its authors, or any references to articles, videos, or materials. Follow these guidelines:

    w        1. Generate an SEO-optimized headline that:
                - Captures user interest without sensationalism
                - Accurately represents the main topic
                - Uses relevant keywords
                - Is concise (ideally 50-60 characters)
                - Maintains professionalism
                - Does not begin with anything akin to "Imagine" or "Picture this"
                - Never references the original source material (e.g.: "the article", or "the story", etc.)
                    
            2. Format your headline exactly as follows:
                HEADLINE: [Your SEO-optimized headline here]

            3. Write your article using the inverted pyramid style:
                - Start with a strong lede (opening sentence) that entices readers and summarizes the most crucial information
                - Present the most important information first
                - Follow with supporting details and context
                - End with the least essential information
                - **Don't mention the parts of the pyramid. Just follow the structure. Never say "in conclusion", for example.**

            4. Adjust the language complexity strictly targeted to the reading level for {grade_description}. This means:
                - Use vocabulary appropriate for this comprehension level
                - Adjust sentence structure complexity accordingly
                - Explain concepts in a way that would be clear to someone at this educational level
                - Do not specifically mention the target's age or grade level in your newly written article

            5. Clearly explain the main topic or discovery being discussed
            6. Highlight key points, findings, or arguments presented in the content
            7. Provide relevant context or background information that helps understand the topic
            8. Mention any significant implications, applications, or future directions discussed
            9. If applicable, include important quotes or statistics that support the main points
            10. **Never refer to the original article, its source, its author, its publisher, or itsss media format**. The article must be a complete stand-alone piece without attribution to, or mention of, the source article.

            Use a neutral, journalistic tone, and ensure that you're reporting the facts as presented in the content, not adding personal opinions or speculation.

            Format your response as follows:
            HEADLINE: [Your SEO-optimized headline here]

            [Your comprehensive news article here, following the inverted pyramid style]
            """


    def _format_summary(self, summary: str, url: str) -> Dict[str, str]:
        parts = summary.split('\n', 1)
        if len(parts) == 2 and parts[0].startswith('HEADLINE:'):
            headline = parts[0].replace('HEADLINE:', '').strip()
            body = parts[1].strip()
        else:
            sentences = summary.split('. ')
            headline = sentences[0].strip()
            body = '. '.join(sentences[1:]).strip()

        if not headline or headline == "Summary of News Content":
            headline = f"Summary of {url.split('//')[1].split('/')[0]}"

        return {
            "title": headline,
            "url": url,
            "description": body
        }

if __name__ == "__main__":
    # Example usage
    api_key = "your_api_key_here"
    agent = News_Agent(api_key)
    results = agent.process_request("Politics")
    for result in results:
        print(f"Title: {result['title']}")
        print(f"Source: {result['source']}")
        print(f"URL: {result['url']}")
        print(f"Description: {result['description']}")
        print(f"Timestamp: {result['timestamp']}")
        print("---")

```

# agents\Web_Agent.py

```python
import os
import sys
import traceback
from urllib.parse import urlparse
from tools.web_tools.WebSearch_Tool import WebSearch_Tool
from tools.web_tools.WebGetContents_Tool import WebGetContents_Tool
from tools.web_tools.WebGetLinks_Tool import WebGetLinks_Tool
from agents.Base_Agent import Base_Agent

import logging

# Set up logging only if DEBUG is True in .env
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

if DEBUG:
    logging.basicConfig(
        filename='debug_info.txt',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
else:
    # Set up a null handler to avoid "No handler found" warnings
    logging.getLogger().addHandler(logging.NullHandler())

def log_debug(message):
    if DEBUG:
        logging.debug(sanitize_message(message))

def sanitize_message(message):
    try:
        return message.encode("utf-8").decode("utf-8")
    except UnicodeEncodeError:
        return message.encode("ascii", "ignore").decode("ascii")

if DEBUG:
    log_debug(f"Current working directory: {os.getcwd()}")
    log_debug(f"Current sys.path: {sys.path}")

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    if DEBUG:
        log_debug(f"Added parent directory to sys.path: {parent_dir}")
if DEBUG:
    log_debug(f"Updated sys.path: {sys.path}")

try:
    if DEBUG:
        log_debug("Attempting to import ProviderFactory")
    from providers.provider_factory import ProviderFactory
    if DEBUG:
        log_debug("ProviderFactory imported successfully")
except ImportError as e:
    if DEBUG:
        log_debug(f"Error importing ProviderFactory: {str(e)}")
        log_debug(f"Traceback:\n{traceback.format_exc()}")
    ProviderFactory = None

class Web_Agent(Base_Agent):
    def __init__(self, api_key, provider_name='groq', num_results=10, max_tokens=4096, model="llama3-8b-8192", temperature=0.0, comprehension_grade=8, summary_length=300):
        log_debug(f"Initializing Web_Agent with provider_name: {provider_name}, num_results: {num_results}, max_tokens: {max_tokens}, model: {model}, temperature: {temperature}, comprehension_grade: {comprehension_grade}, summary_length: {summary_length}")
        if not api_key:
            log_debug("API key is missing or empty")
            raise ValueError("API key is required")
        if ProviderFactory is None:
            log_debug("ProviderFactory is None. Raising ImportError.")
            raise ImportError("ProviderFactory is not available. Please check your project structure.")
        
        self.api_key = api_key
        self.num_results = num_results
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temperature
        self.comprehension_grade = comprehension_grade
        self.summary_length = summary_length
        self.provider = ProviderFactory.get_provider(provider_name, api_key)
        self.image_handler = self._initialize_image_handler()

        try:
            log_debug(f"Attempting to get provider with API key: {api_key[:5]}...")
            self.provider = ProviderFactory.get_provider(provider_name, api_key)
            log_debug("Provider obtained successfully")
            log_debug("Initializing tools")
            self.tools = self._initialize_tools()
            log_debug("Tools initialized successfully")
        except Exception as e:
            log_debug(f"Error in Web_Agent.__init__: {str(e)}")
            log_debug(f"Traceback:\n{traceback.format_exc()}")
            raise
    

    def _initialize_image_handler(self):
        return lambda image_url, prompt: self.provider.generate(prompt, image_path=image_url)


    def process_request(self, user_request: str) -> list:
        log_debug(f"Processing request: {user_request}")
        log_debug(f"Using comprehension grade: {self.comprehension_grade}, temperature: {self.temperature}")
        try:
            if self._is_image_url(user_request):
                return self._process_image_request(user_request)
            elif self._is_url(user_request):
                return self._process_url_request(user_request)
            else:
                return self._process_web_search(user_request)
        except Exception as e:
            log_debug(f"Error in process_request: {str(e)}")
            log_debug(f"Traceback:\n{traceback.format_exc()}")
            return [{"title": "Error", "url": "", "description": f"An error occurred while processing your request: {str(e)}"}]

    def _is_image_url(self, url: str) -> bool:
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and any(parsed_url.path.lower().endswith(ext) for ext in image_extensions)

    def _process_image_request(self, image_url: str, custom_prompt: str = None) -> list:
        log_debug(f"Processing image request: {image_url}")
        default_prompt = "What's in this image?"
        prompt = custom_prompt if custom_prompt else default_prompt
        
        try:
            if self.model == "llava-v1.5-7b-4096-preview":
                description = self.provider.generate(prompt, image_path=image_url, model=self.model)
            else:
                description = self.provider.generate(f"{prompt}\n\nImage URL: {image_url}")
            
            log_debug(f"Image description generated successfully")
            return [{
                "title": "Image Analysis",
                "url": image_url,
                "description": description,
                "prompt_used": prompt
            }]
        except Exception as e:
            log_debug(f"Error in _process_image_request: {str(e)}")
            return [{
                "title": "Error",
                "url": image_url,
                "description": f"An error occurred while analyzing the image: {str(e)}",
                "prompt_used": prompt
            }]

    def _is_url(self, text: str) -> bool:
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _process_url_request(self, url: str) -> list:
        log_debug(f"Processing URL request: {url}")
        content = self._get_web_content(url)
        if content:
            summary_result = self._summarize_web_content(content, url)
            return [summary_result]
        else:
            return [{"title": "Error", "url": url, "description": "  Some sites prohibit summarization.  Click URL to go there directly."}]

    def _process_web_search(self, user_request: str) -> list:
        log_debug(f"Entering _process_web_search with num_results: {self.num_results}")
        search_results = self._perform_web_search(user_request)
        log_debug(f"Web search completed. Number of results: {len(search_results)}")
        if not search_results:
            log_debug("No search results found")
            return [{"title": "No Results", "url": "", "description": "I'm sorry, but I couldn't find any relevant information for your request."}]

        filtered_results = self._filter_search_results(search_results)
        log_debug(f"Results filtered. Number of filtered results: {len(filtered_results)}")
        if not filtered_results:
            log_debug("No results after filtering")
            return [{"title": "No Results", "url": "", "description": "I found some results, but they were all from domains I've been instructed to skip. Could you try rephrasing your request?"}]

        deduplicated_results = self._remove_duplicates(filtered_results)
        log_debug(f"Results deduplicated. Number of final results: {len(deduplicated_results[:self.num_results])}")
        return deduplicated_results[:self.num_results]  # Return top num_results unique results

    def _initialize_tools(self):
        return {
            "WebSearch_Tool": WebSearch_Tool,
            "WebGetContents_Tool": WebGetContents_Tool,
            "WebGetLinks_Tool": WebGetLinks_Tool
        }

    def _perform_web_search(self, query: str):
        log_debug(f"Performing web search with query: {query} and num_results: {self.num_results}")
        try:
            results = self.tools["WebSearch_Tool"](query, self.num_results * 2)  # Request more results to account for filtering
            log_debug(f"Web search completed successfully. Number of results: {len(results)}")
            return results
        except Exception as e:
            log_debug(f"Error in _perform_web_search: {str(e)}")
            log_debug(f"Traceback:\n{traceback.format_exc()}")
            raise

    def _filter_search_results(self, results):
        log_debug("Starting filtering process")
        filtered_results = []
        for result in results:
            if result['description'] and result['title'] != 'No title' and result['url'].startswith('https://'):
                filtered_results.append(result)
        log_debug(f"Filtering completed. Number of filtered results: {len(filtered_results)}")
        return filtered_results

    def _remove_duplicates(self, results):
        log_debug("Starting deduplication process")
        seen_urls = set()
        unique_results = []
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
            else:
                log_debug(f"Duplicate URL found and removed: {result['url']}")
        log_debug(f"Deduplication completed. Number of unique results: {len(unique_results)}")
        return unique_results

    def _get_web_content(self, url: str) -> str:
        return self.tools["WebGetContents_Tool"](url)

    def _summarize_web_content(self, content: str, url: str) -> dict:
        log_debug(f"Summarizing content from URL: {url}")
        summary_prompt = self._create_summary_prompt(content, url)
        log_debug(f"Summary prompt: {sanitize_message(summary_prompt)}")
        summary = self.provider.generate(
            summary_prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return self._format_summary(summary, url)

    def _create_summary_prompt(self, content: str, url: str) -> str:
        grade_descriptions = {
            1: "a 6-year-old in 1st grade", 2: "a 7-year-old in 2nd grade", 3: "an 8-year-old in 3rd grade",
            4: "a 9-year-old in 4th grade", 5: "a 10-year-old in 5th grade", 6: "an 11-year-old in 6th grade",
            7: "a 12-year-old in 7th grade", 8: "a 13-year-old in 8th grade", 9: "a 14-year-old in 9th grade",
            10: "a 15-year-old in 10th grade", 11: "a 16-year-old in 11th grade", 12: "a 17-year-old in 12th grade",
            13: "a college undergraduate", 14: "a master's degree student", 15: "a PhD candidate"
        }
        grade_description = grade_descriptions.get(self.comprehension_grade, "an average adult")

        log_debug(f"Selected grade description: {grade_description}")

        return f"""
        Summarize the following web content from {url} for {grade_description}:
        {content}

        Your task is to provide a comprehensive and informative synopsis of the main subject matter, along with an SEO-optimized headline. Follow these guidelines:

        1. Generate an SEO-optimized headline that:
        - Captures user interest without sensationalism
        - Accurately represents the main topic
        - Uses relevant keywords
        - Is concise
        - Maintains professionalism
        - Does not begin with anything akin to "Imagine" or "Picture this"
        
        2. Format your headline exactly as follows:
        HEADLINE: [Your SEO-optimized headline here]

        3. Write your summary using the inverted pyramid style:
        - Start with a strong lede (opening sentence) that entices readers and summarizes the most crucial information
        - Present the most important information first
        - Follow with supporting details and context
        - End with the least essential information

        4. Adjust the language complexity strictly targeted to the reading level for {grade_description}. This means:
        - Use vocabulary appropriate for this comprehension level
        - Adjust sentence structure complexity accordingly
        - Explain concepts in a way that would be clear to someone at this educational level
        - Do not specifically mention the target's age or grade level in the summary response

        5. Clearly explain the main topic or discovery being discussed
        6. Highlight key points, findings, or arguments presented in the content
        7. Provide relevant context or background information that helps understand the topic
        8. Mention any significant implications, applications, or future directions discussed
        9. If applicable, include important quotes or statistics that support the main points

        Your summary should be approximately {self.summary_length} words long. Use a neutral, journalistic tone, and ensure that you're reporting the facts as presented in the content, not adding personal opinions or speculation.

        Format your response as follows:
        HEADLINE: [Your SEO-optimized headline here]

        [Your comprehensive summary here, following the inverted pyramid style]
        """

    def _format_summary(self, summary: str, url: str) -> dict:
        # Split the summary into headline and body
        parts = summary.split('\n', 1)
        if len(parts) == 2 and parts[0].startswith('HEADLINE:'):
            headline = parts[0].replace('HEADLINE:', '').strip()
            body = parts[1].strip()
        else:
            # If no headline is found, use the first sentence as the headline
            sentences = summary.split('. ')
            headline = sentences[0].strip()
            body = '. '.join(sentences[1:]).strip()

        # If the headline is empty or still "Summary of Web Content", generate a generic one
        if not headline or headline == "Summary of Web Content":
            headline = f"Summary of {url.split('//')[1].split('/')[0]}"

        return {
            "title": headline,
            "url": url,
            "description": body
        }

    def _combine_summaries(self, summaries: list, user_request: str) -> str:
        combined_prompt = f"""
        Given the following summaries from multiple sources:
        {' '.join(summaries)}

        Respond to the user's request: "{user_request}"
        
        Provide a concise, coherent response that addresses the user's request using the information from the summaries.
        Focus on the most relevant and important points, and present the information in a clear and organized manner.
        """
        return self.provider.generate(combined_prompt, max_tokens=self.max_tokens)
```

# agents\__init__.py

```python
from .Web_Agent import Web_Agent
```

# providers\anthropic_provider.py

```python
import anthropic
import os
from typing import Dict, Any

from providers.base_provider import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Anthropic API key is not provided")
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
from typing import Dict, Any, Union, AsyncIterator, List

class BaseLLMProvider(ABC):
    @abstractmethod
    def __init__(self, api_key: str):
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Union[str, AsyncIterator[str]]:
        pass

    @abstractmethod
    def get_available_models(self) -> Dict[str, int]:
        pass

    @abstractmethod
    def process_response(self, response: Any) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def send_request(self, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def _async_create_completion(self, **kwargs) -> Union[str, AsyncIterator[str]]:
        pass

    @abstractmethod
    def _process_tool_calls(self, response: Any, tools: List[Dict[str, Any]]) -> str:
        pass

    @abstractmethod
    async def _async_process_tool_calls(self, response: Any, tools: List[Dict[str, Any]]) -> str:
        pass
```

# providers\provider_factory.py

```python
import os
import sys
from pocketgroq import GroqProvider
from providers.anthropic_provider import AnthropicProvider

# Set up logging only if DEBUG is True in .env
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def log_debug(message):
    if DEBUG:
        with open('debug_info.txt', 'a') as f:
            f.write(f"{message}\n")

if DEBUG:
    log_debug("Entering provider_factory.py")
    log_debug(f"Current working directory: {os.getcwd()}")
    log_debug(f"Current sys.path: {sys.path}")

class ProviderFactory:
    @staticmethod
    def get_provider(provider_name, api_key):
        if DEBUG:
            log_debug(f"get_provider called with provider_name: {provider_name}")
        providers = {
            'groq': GroqProvider,
            'anthropic': AnthropicProvider,
            # Add more providers here as needed
        }
        
        provider_class = providers.get(provider_name.lower())
        if provider_class is None:
            if DEBUG:
                log_debug(f"Unsupported provider: {provider_name}")
            raise ValueError(f"Unsupported provider: {provider_name}")
        
        if DEBUG:
            log_debug(f"Creating {provider_name} instance with API key")
        return provider_class(api_key)

    @staticmethod
    def get_model():
        model = os.environ.get('DEFAULT_MODEL', 'llava-v1.5-7b-4096-preview')
        if DEBUG:
            log_debug(f"get_model called, returning: {model}")
        return model

if DEBUG:
    log_debug("Exiting provider_factory.py")
```

# providers\__init__.py

```python
# This file is intentionally left empty to mark the directory as a Python package.
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
            "Accept-Language": "en-US,en;q=0.0",
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
```

