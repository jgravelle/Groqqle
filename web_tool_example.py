"""
Example script demonstrating how to use the Groqqle_web_tool class directly.

This is a minimal example that shows the structure
without requiring actual execution of the code.
"""

def example_groqqle_web_tool():
    """Show example code for using Groqqle_web_tool class."""
    
    print("=== Groqqle_web_tool Usage Example ===")
    print("```python")
    print("from Groqqle_web_tool import Groqqle_web_tool")
    print("")
    print("# Initialize the tool with your API key and configuration")
    print("groqqle_tool = Groqqle_web_tool(")
    print("    api_key='your_groq_api_key_here',")
    print("    provider_name='groq',  # Can also use 'anthropic' if configured")
    print("    num_results=10,        # Number of search results to return")
    print("    max_tokens=4096,       # Max tokens for AI responses")
    print("    model='llama3-8b-8192', # Model to use")
    print("    temperature=0.0,        # Temperature for generation")
    print("    comprehension_grade=8   # Target reading level (1-15)")
    print(")")
    print("")
    print("# Perform a web search")
    print("query = 'latest advancements in artificial intelligence'")
    print("results = groqqle_tool.run(query)")
    print("")
    print("# Process the search results")
    print("for i, result in enumerate(results, 1):")
    print("    print(f\"Result {i}:\")")
    print("    print(f\"Title: {result['title']}\")")
    print("    print(f\"URL: {result['url']}\")")
    print("    print(f\"Description: {result['description'][:100]}...\\n\")")
    print("")
    print("# Summarize content from a specific URL")
    print("if results:")
    print("    first_url = results[0]['url']")
    print("    summary = groqqle_tool.summarize_url(first_url)")
    print("    ")
    print("    print(\"URL Summary:\")")
    print("    print(f\"Title: {summary['title']}\")")
    print("    print(f\"Description: {summary['description']}\")")
    print("```")
    
    print("\n=== Environment Setup ===")
    print("Make sure you have set the appropriate API keys in your environment variables or .env file:")
    print("```env")
    print("GROQ_API_KEY=your_groq_api_key_here")
    print("ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional, if using Anthropic")
    print("```")
    
    print("\n=== Required Dependencies ===")
    print("The following dependencies need to be installed:")
    print("1. requests - For HTTP requests")
    print("2. beautifulsoup4 - For parsing HTML")
    print("3. python-dotenv - For loading environment variables")
    print("4. pocketgroq / groq - For API integration")
    print("5. selenium & webdriver-manager - For web search functionality")
    
    print("\nYou can install these with:")
    print("```bash")
    print("pip install -r requirements.txt")
    print("```")
    
    print("\n=== Integration with AI Assistants ===")
    print("For integrating with PocketGroq:")
    print("```python")
    print("from pocketgroq import GroqProvider")
    print("from Groqqle_web_tool import Groqqle_web_tool")
    print("")
    print("# Set up the provider and tool")
    print("groq_provider = GroqProvider(api_key='your_groq_api_key_here')")
    print("groqqle_tool = Groqqle_web_tool(api_key='your_groq_api_key_here')")
    print("")
    print("# Define the tool for PocketGroq")
    print("tools = [")
    print("    {")
    print("        \"type\": \"function\",")
    print("        \"function\": {")
    print("            \"name\": \"groqqle_web_search\",")
    print("            \"description\": \"Perform a web search using Groqqle\",")
    print("            \"parameters\": {")
    print("                \"type\": \"object\",")
    print("                \"properties\": {")
    print("                    \"query\": {")
    print("                        \"type\": \"string\",")
    print("                        \"description\": \"The search query\"")
    print("                    }")
    print("                },")
    print("                \"required\": [\"query\"]")
    print("            }")
    print("        }")
    print("    }")
    print("]")
    print("")
    print("def groqqle_web_search(query):")
    print("    results = groqqle_tool.run(query)")
    print("    return results")
    print("")
    print("# Use the tool in your project")
    print("user_message = \"Search for the latest developments in quantum computing\"")
    print("system_message = \"You are a helpful assistant. Use the Groqqle web search tool to find information.\"")
    print("")
    print("response = groq_provider.generate(")
    print("    system_message,")
    print("    user_message,")
    print("    tools=tools,")
    print("    tool_choice=\"auto\"")
    print(")")
    print("")
    print("print(response)")
    print("```")

if __name__ == "__main__":
    example_groqqle_web_tool()