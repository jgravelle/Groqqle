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
            "llama2-70b-4096": {"id": "llama2-70b-4096", "context_window": 4096},
            "llama-3.2-11b-vision-preview": {"id": "llama-3.2-11b-vision-preview", "context_window": 4096}
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
        url = urls[0]
        # Remove the URL from the query to get the custom prompt
        custom_prompt = query.replace(url, '').strip()
        if not custom_prompt:
            custom_prompt = "Describe this image in one sentence."
        return url, custom_prompt
    return None, None

def is_image_url(url: str) -> bool:
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    parsed_url = urlparse(url)
    return parsed_url.scheme in ['http', 'https'] and any(parsed_url.path.lower().endswith(ext) for ext in image_extensions)

def process_image(query: str, api_key: str):
    image_url, custom_prompt = extract_url_and_prompt(query)
    if not image_url:
        return None

    try:
        agent = Web_Agent(
            api_key,
            num_results=1,
            max_tokens=st.session_state.context_window,
            model="llama-3.2-11b-vision-preview",
            temperature=st.session_state.temperature,
            comprehension_grade=st.session_state.comprehension_grade,
            summary_length=st.session_state.summary_length
        )
        results = agent._process_image_request(image_url, custom_prompt)
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

        # Add Humanize checkbox
        st.session_state.humanize = st.checkbox("Humanize", value=False, key="humanize_checkbox")

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
            "llama2-70b-4096": {"id": "llama2-70b-4096", "context_window": 4096},
            "llama-3.2-11b-vision-preview": {"id": "llama-3.2-11b-vision-preview", "context_window": 4096}
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
                url, custom_prompt = extract_url_and_prompt(query)
                if url:
                    with st.spinner('Processing URL...'):
                        if is_image_url(url):
                            image_results = process_image(query, api_key)
                            if image_results:
                                st.session_state.image_analysis = image_results[0]['description']
                                st.session_state.image_url = url
                                st.session_state.image_prompt = image_results[0].get('prompt_used', "Describe this image in one sentence.")
                                display_results(image_results, json_results, api_key)
                        else:
                            summary = summarize_url(url, api_key, st.session_state.comprehension_grade, st.session_state.temperature)
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
            url, _ = extract_url_and_prompt(query)
            if url:
                if is_image_url(url):
                    results = process_image(query, api_key)
                else:
                    agent = Web_Agent(
                        api_key,
                        num_results=1,
                        max_tokens=context_window,
                        model=selected_model,
                        temperature=temperature,
                        comprehension_grade=comprehension_grade,
                        summary_length=summary_length,
                        humanize=st.session_state.humanize 
                    )
                    results = [summarize_url(url, api_key, comprehension_grade, temperature)]
            elif search_type == "Web":
                agent = Web_Agent(
                    api_key,
                    num_results=num_results,
                    max_tokens=context_window,
                    model=selected_model,
                    temperature=temperature,
                    comprehension_grade=comprehension_grade,
                    summary_length=summary_length,
                    humanize=st.session_state.humanize 
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
            summary_length=summary_length,
            humanize=st.session_state.humanize 
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
                summary_length=summary_length,
                humanize=st.session_state.humanize 
            )

            url, _ = extract_url_and_prompt(query)
            if url and is_image_url(url):
                results = process_image(query, api_key)
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
