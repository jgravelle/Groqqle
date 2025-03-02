# Groqqle Troubleshooting Guide

This guide addresses common issues and their solutions when running Groqqle locally or in cloud environments.

## Common Error Messages

### "Unable to retrieve search results in cloud environment"

This error occurs when the search functionality fails in a cloud environment like Streamlit Cloud.

**Solutions:**

1. **Update WebSearch_Tool.py**: We've enhanced the `_api_search` function with multiple fallback methods that don't require Selenium or a browser.

2. **Configure Bing Search API**: For more reliable search results:
   - Get a free Bing Search API key from [Microsoft Azure](https://portal.azure.com/#create/Microsoft.CognitiveServicesBingSearch)
   - Add the key to your Streamlit secrets (`BING_API_KEY`)

3. **Try Different Search Methods**: The updated code automatically tries multiple search methods:
   - Direct Google scraping (lightweight)
   - Bing API (if key is available)
   - Brave Search scraping
   - DuckDuckGo Lite scraping
   - DuckDuckGo API

### "ModuleNotFoundError: No module named 'tldextract'"

This error occurs when required packages are missing.

**Solutions:**

1. **Install the missing package**:
   ```
   pip install tldextract
   ```

2. **Install all requirements**:
   ```
   pip install -r requirements.txt
   ```

3. **For cloud deployment**, use:
   ```
   pip install -r requirements-cloud.txt
   ```

### "Chrome/Firefox/Browser not found" errors

These errors occur when trying to use Selenium in environments without a browser.

**Solutions:**

1. **Run in cloud-detection mode**: The updated code automatically detects cloud environments and uses browser-free alternatives.

2. **Force cloud mode**: Set `STREAMLIT_CLOUD=1` in your environment variables to force cloud mode even on local machines:
   ```
   export STREAMLIT_CLOUD=1
   ```

### API Key Issues

**Solutions:**

1. **Check key format**: Groq API keys should start with `gsk_` and be longer than 10 characters

2. **Multiple key sources**: The application checks for API keys in this order:
   - URL parameters (`?api_key=gsk_...`)
   - Streamlit secrets
   - Function arguments
   - Environment variables
   - Session state

3. **For Streamlit Cloud**: Configure API keys in Streamlit secrets management

## Performance Optimization

### Slow Search in Cloud Environments

**Solutions:**

1. **Bing API Key**: Add a Bing Search API key for faster, more reliable search
   
2. **Reduce Results**: Lower the number of results in settings to speed up searches
   
3. **Use Direct Links**: For specific content, paste the complete URL in the search box

### Memory Usage Issues

**Solutions:**

1. **Limit Context Window**: Use a smaller context window in settings
   
2. **Reduce Summary Length**: Set a lower summary length (e.g., 200 words)
   
3. **Clear Cache**: Add a "Clear Cache" button to your app:
   ```python
   if st.button("Clear Cache"):
       st.cache_data.clear()
   ```

## Installation and Setup Issues

### Local Installation

1. **Create a virtual environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```
   streamlit run Groqqle.py
   ```

### Cloud Deployment

1. **Use cloud-specific requirements**:
   ```
   pip install -r requirements-cloud.txt
   ```

2. **Configure Streamlit secrets**

3. **Set appropriate environment variables**

## Getting Help

If you continue to experience issues:

1. **Enable Debug Mode**: Set `DEBUG=True` in .env or environment variables
2. **Check Logs**: Examine debug_info.txt and Streamlit logs
3. **Open an Issue**: Provide detailed error information and steps to reproduce