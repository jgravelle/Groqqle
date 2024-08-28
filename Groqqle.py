import os
import sys
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agents.Web_Agent import Web_Agent

with open('debug_info.txt', 'w') as f:
    f.write(f"Current working directory: {os.getcwd()}\n")
    f.write(f"Current sys.path: {sys.path}\n")

def get_groq_api_key():
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        if 'groq_api_key' not in st.session_state:
            st.warning("Groq API Key not found. Please enter your API key below:")
            api_key = st.text_input("Groq API Key", type="password")
            if api_key:
                st.session_state.groq_api_key = api_key
        else:
            api_key = st.session_state.groq_api_key
    else:
        st.session_state.groq_api_key = api_key
    
    return api_key

def main():
    st.set_page_config(page_title="Groqqle", layout="wide")

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

    api_key = get_groq_api_key()

    if not api_key:
        st.error("Please provide a valid Groq API Key to use the application.")
        return

    try:
        agent = Web_Agent(api_key)
    except Exception as e:
        with open('debug_info.txt', 'a') as f:
            f.write(f"Error initializing Web_Agent: {str(e)}\n")
        st.error(f"Error initializing Web_Agent: {str(e)}")
        return

    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    st.image("images/logo.png", width=272)

    query = st.text_input("Search query", key="search_bar", on_change=perform_search, label_visibility="collapsed")

    col1, col2, col3 = st.columns([2,1,2])
    with col1:
        if st.button("Groqqle Search", key="search_button"):
            perform_search()
    with col3:
        json_results = st.checkbox("JSON Results", value=False, key="json_results")

    st.markdown('</div>', unsafe_allow_html=True)

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

def create_api_app():
    app = Flask(__name__)

    @app.route('/search', methods=['POST'])
    def api_search():
        data = request.json
        query = data.get('query')
        if not query:
            return jsonify({"error": "No query provided"}), 400

        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return jsonify({"error": "Groq API Key not set"}), 500

        agent = Web_Agent(api_key)
        results = agent.process_request(query)
        return jsonify(results)

    return app

if __name__ == "__main__":
    main()