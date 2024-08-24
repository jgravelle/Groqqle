import streamlit as st
import json
from PIL import Image
import base64
from agents.Web_Agent import Web_Agent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    st.set_page_config(page_title="Groqqle Clone", layout="wide")

    # Custom CSS to mimic Groqqle's style
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

    # Initialize Web_Agent
    agent = Web_Agent()

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
    if query:
        with st.spinner('Searching...'):
            results = Web_Agent().process_request(query)
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