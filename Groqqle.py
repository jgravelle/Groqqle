import os
import sys
import argparse
import streamlit as st
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import requests
import logging

from agents.Web_Agent import Web_Agent

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
            "mixtral-8x7b-32768": {"id": "mixtral-8x7b-32768", "context_window": 32768},
            "llama2-70b-4096": {"id": "llama2-70b-4096", "context_window": 4096}
        }

def get_groq_api_key(api_key_arg: str = None) -> str:
    api_key = api_key_arg or os.getenv('GROQ_API_KEY')
    log_debug(f"GROQ_API_KEY from environment: {'Found' if api_key else 'Not found'}")
    
    if not api_key:
        if 'groq_api_key' not in st.session_state:
            st.warning("To access all models and ensure good results, RUN GROQQLE LOCALLY!")
            st.warning("Groq API Key not found in environment. Please enter your API key below:")
            api_key = st.text_input("Groq API Key", type="password")
            if api_key:
                st.session_state.groq_api_key = api_key
                st.session_state.models = fetch_groq_models(api_key)  # Fetch models after API key is entered
                st.experimental_rerun()  # Rerun the app to update the sidebar
            log_debug("API key entered by user and stored in session state")
        else:
            api_key = st.session_state.groq_api_key
            log_debug("API key retrieved from session state")
    else:
        st.session_state.groq_api_key = api_key
        log_debug("API key from environment stored in session state")
    
    return api_key

def update_sidebar(models):
    with st.sidebar:
        st.title("Settings")
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
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.01
        )

        # Comprehension Grade slider
        grade_labels = [
            "1st Grade", "2nd Grade", "3rd Grade", "4th Grade", "5th Grade",
            "6th Grade", "7th Grade", "8th Grade", "9th Grade", "10th Grade",
            "11th Grade", "12th Grade", "Baccalaureate", "Masters", "PhD"
        ]
        selected_grade = st.selectbox(
            "Comprehension Grade",
            options=grade_labels,
            index=st.session_state.comprehension_grade - 1  # Adjust index from grade level
        )
        log_debug(f"Selected comprehension grade: {selected_grade}")
        selected_grade_index = grade_labels.index(selected_grade) + 1
        log_debug(f"Selected comprehension grade index: {selected_grade_index}")
        st.session_state.comprehension_grade = selected_grade_index
        log_debug(f"Updated comprehension grade in session state: {st.session_state.comprehension_grade}")

def main(api_key_arg: str = None, num_results: int = 10, max_tokens: int = 4096, default_summary_length: int = 300):
    st.set_page_config(page_title="Groqqle", layout="centered", initial_sidebar_state="collapsed")

    # Initialize session state
    if 'num_results' not in st.session_state:
        st.session_state.num_results = num_results
    if 'summary_length' not in st.session_state:
        st.session_state.summary_length = default_summary_length
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "mixtral-8x7b-32768"
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.5
    if 'comprehension_grade' not in st.session_state:
        st.session_state.comprehension_grade = 8  # Default comprehension grade
    if 'context_window' not in st.session_state:
        st.session_state.context_window = max_tokens
    if 'models' not in st.session_state:
        st.session_state.models = {
            "mixtral-8x7b-32768": {"id": "mixtral-8x7b-32768", "context_window": 32768},
            "llama2-70b-4096": {"id": "llama2-70b-4096", "context_window": 4096}
        }

    api_key = get_groq_api_key(api_key_arg)

    if api_key:
        if 'models' not in st.session_state or st.session_state.models == {
            "mixtral-8x7b-32768": {"id": "mixtral-8x7b-32768", "context_window": 32768},
            "llama2-70b-4096": {"id": "llama2-70b-4096", "context_window": 4096}
        }:
            st.session_state.models = fetch_groq_models(api_key)

    update_sidebar(st.session_state.models)

    # Main content
    st.markdown(""" 
    <style>
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

    if not api_key:
        st.error("Please provide a valid Groq API Key to use the application.")
        return

    log_debug(f"Attempting to initialize Web_Agent with API key: {'[REDACTED]' if api_key else 'None'}")
    try:
        agent = Web_Agent(
            api_key,
            num_results=st.session_state.num_results,
            max_tokens=st.session_state.context_window,
            model=st.session_state.selected_model,
            temperature=st.session_state.temperature,
            comprehension_grade=st.session_state.comprehension_grade
        )
        log_debug(f"Web_Agent initialized successfully with comprehension grade: {st.session_state.comprehension_grade}")
    except Exception as e:
        log_debug(f"Error initializing Web_Agent: {str(e)}")
        st.error(f"Error initializing Web_Agent: {str(e)}")
        return

    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    st.image("images/logo.png", width=272)

    query = st.text_input("Search query or enter a URL", key="search_bar", on_change=perform_search, label_visibility="collapsed")

    col1, col2, col3 = st.columns([2,1,2])
    with col1:
        if st.button("Groqqle Search", key="search_button"):
            perform_search()
    with col3:
        json_results = st.checkbox("JSON Results", value=False, key="json_results")

    if query.startswith('http'):
        with st.spinner('Summarizing...'):
            summary = summarize_url(query, api_key, st.session_state.comprehension_grade, st.session_state.temperature)
            display_results([summary], json_results, api_key)
    elif st.session_state.get('search_results'):
        display_results(st.session_state.search_results, json_results, api_key)

    st.markdown('</div>', unsafe_allow_html=True)

def perform_search():
    query = st.session_state.search_bar
    api_key = st.session_state.get('groq_api_key')
    num_results = st.session_state.num_results
    summary_length = st.session_state.summary_length
    selected_model = st.session_state.selected_model
    context_window = st.session_state.context_window
    temperature = st.session_state.temperature
    comprehension_grade = st.session_state.comprehension_grade

    log_debug(f"perform_search: comprehension_grade = {comprehension_grade}, temperature = {temperature}")

    if query and api_key:
        with st.spinner('Processing...'):
            log_debug(f"Processing query: {query}")
            agent = Web_Agent(
                api_key,
                num_results=num_results,
                max_tokens=context_window,
                model=selected_model,
                temperature=temperature,
                comprehension_grade=comprehension_grade,
                summary_length=summary_length
            )
            log_debug(f"Web_Agent initialized for search with comprehension grade: {comprehension_grade} and temperature: {temperature}")
            results = agent.process_request(query)
            log_debug(f"Processing completed. Number of results: {len(results)}")
        st.session_state.search_results = results
    else:
        if not api_key:
            st.error("Please provide a valid Groq API Key to perform the search.")
        if not query:
            st.error("Please enter a search query or URL.")

def summarize_url(url, api_key, comprehension_grade, temperature):
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
        st.markdown("### Search Results")
        
        if json_format:
            st.json(results)
        else:
            for index, result in enumerate(results):
                log_debug(f"Displaying result {index}: {result['url']}")
                
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(f"### [{result['title']}]({result['url']})")
                with col2:
                    summary_button = st.button("📝", key=f"summary_{result['url']}", help="Get summary")
                
                st.markdown(f"*Source: {result['url']}*")
                st.markdown(result['description'])
                
                if summary_button:
                    with st.spinner("Generating summary..."):
                        summary = summarize_url(result['url'], api_key, st.session_state.comprehension_grade, st.session_state.temperature)
                        st.markdown("---")
                        st.markdown(f"## Summary: {summary['title']}")
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
        data = request.json
        query = data.get('query')
        num_results = data.get('num_results', default_num_results)
        max_tokens = data.get('max_tokens', default_max_tokens)
        summary_length = data.get('summary_length', default_summary_length)
        model = data.get('model', 'mixtral-8x7b-32768')
        temperature = data.get('temperature', 0.5)
        comprehension_grade = data.get('comprehension_grade', 8)
        
        if not query:
            return jsonify({"error": "No query provided"}), 400

        api_key = api_key_arg or os.getenv('GROQ_API_KEY')
        if not api_key:
            return jsonify({"error": "Groq API Key not set"}), 500

        log_debug(f"API search endpoint hit with query: {query}, num_results: {num_results}, summary_length: {summary_length}, model: {model}, max_tokens: {max_tokens}, temperature: {temperature}, comprehension_grade: {comprehension_grade}")
        
        try:
            agent = Web_Agent(
                api_key, 
                num_results=num_results, 
                max_tokens=max_tokens, 
                model=model,
                temperature=temperature,
                comprehension_grade=comprehension_grade
            )
            results = agent.process_request(query)
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
            print('''// Example 1: Search query
{
    "query": "latest developments in AI",
    "num_results": 5,
    "max_tokens": 4096,
    "summary_length": 200,
    "model": "mixtral-8x7b-32768",
    "temperature": 0.5,
    "comprehension_grade": 8
}
// Example 2: URL summary
{
    "query": "https://www.example.com/article-about-ai",
    "max_tokens": 8192,
    "summary_length": 500,
    "model": "llama2-70b-4096",
    "temperature": 0.7,
    "comprehension_grade": 5
}''')

        # Only print the startup message once
        print_startup_message()

        # Run the Flask app without debug mode
        app.run(host='0.0.0.0', port=args.port)