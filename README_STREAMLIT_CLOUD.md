# Deploying Groqqle to Streamlit Cloud

This guide provides instructions for successfully running Groqqle on Streamlit Cloud, addressing the differences between local and cloud deployments.

## Setup Instructions

### 1. Fork or Clone the Repository

Fork or clone the Groqqle repository to your GitHub account.

### 2. Set Up Streamlit Cloud

- Go to [Streamlit Cloud](https://streamlit.io/cloud)
- Connect your GitHub account
- Deploy your forked Groqqle repository
- Select `Groqqle.py` as the main file

### 3. Configure Streamlit Secrets (Optional but Recommended)

For improved performance and user experience, add your Groq API key to Streamlit secrets:

1. In your Streamlit Cloud app settings, find the "Secrets" section
2. Add your Groq API key in the following format:
   ```
   GROQ_API_KEY = "gsk_your_key_here"
   ```
3. Save the secrets

### 4. Configuring Environment Variables

For additional settings, add these optional environment variables in Streamlit Cloud settings:

- `DEBUG` - Set to "True" to enable debug logging
- `STREAMLIT_CLOUD` - Set to "1" to explicitly enable cloud mode

## Cloud-Specific Adaptations

The following adaptations are made automatically when running in Streamlit Cloud:

1. **Web Search Tool**: Uses API-based search instead of Selenium (which requires browser binaries)
2. **API Key Management**: Prioritizes Streamlit secrets for API keys
3. **Logging**: Adjusted to work in cloud environments
4. **Error Handling**: Enhanced to handle cloud-specific limitations

## Using the Cloud Version

Users can interact with Groqqle in the cloud in the following ways:

1. **Enter their own API key** in the sidebar (recommended for occasional users)
2. **Use a shared API key** if you've configured one in Streamlit secrets (better for teams)
3. **Pass an API key in the URL** by using `?api_key=gsk_your_key_here` in the URL (useful for sharing specific configurations)

## Troubleshooting

If you encounter issues with the Streamlit Cloud deployment:

1. Check the application logs in Streamlit Cloud dashboard
2. Verify that the requirements are correctly installed
3. Ensure that all paths used in the code are relative, not absolute
4. Make sure your Groq API key is valid

## Performance Considerations

- The cloud version uses a more lightweight search implementation
- Image processing may be slower in the cloud environment
- Consider upgrading to a paid Streamlit plan for better performance with many users

## Additional Configuration

If you need to customize the cloud deployment further, edit the `.streamlit/cloud_config.py` file to adjust settings specific to your deployment needs.