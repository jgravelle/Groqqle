import os
import sys
import traceback
from tools.web_tools.WebSearch_Tool import WebSearch_Tool
from tools.web_tools.WebGetContents_Tool import WebGetContents_Tool
from tools.web_tools.WebGetLinks_Tool import WebGetLinks_Tool
from agents.Base_Agent import Base_Agent

def log_debug(message):
    with open('debug_info.txt', 'a') as f:
        f.write(f"{message}\n")

log_debug(f"Current working directory: {os.getcwd()}")
log_debug(f"Current sys.path: {sys.path}")

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    log_debug(f"Added parent directory to sys.path: {parent_dir}")
log_debug(f"Updated sys.path: {sys.path}")

try:
    log_debug("Attempting to import ProviderFactory")
    from providers.provider_factory import ProviderFactory
    log_debug("ProviderFactory imported successfully")
except ImportError as e:
    log_debug(f"Error importing ProviderFactory: {str(e)}")
    log_debug(f"Traceback:\n{traceback.format_exc()}")
    ProviderFactory = None

class Web_Agent(Base_Agent):
    def __init__(self, api_key, provider_name='groq', num_results=10, max_tokens=256):
        log_debug(f"Initializing Web_Agent with provider_name: {provider_name}, num_results: {num_results}, max_tokens: {max_tokens}")
        if not api_key:
            log_debug("API key is missing or empty")
            raise ValueError("API key is required")
        if ProviderFactory is None:
            log_debug("ProviderFactory is None. Raising ImportError.")
            raise ImportError("ProviderFactory is not available. Please check your project structure.")
        
        self.api_key = api_key
        self.num_results = num_results
        self.max_tokens = max_tokens

        try:
            log_debug(f"Attempting to get provider with API key: {api_key[:5]}...")
            self.provider = ProviderFactory.get_provider(provider_name, api_key)
            log_debug("Provider obtained successfully")
            log_debug("Attempting to get model")
            self.model = ProviderFactory.get_model()
            log_debug("Model obtained successfully")
            log_debug("Initializing tools")
            self.tools = self._initialize_tools()
            log_debug("Tools initialized successfully")
        except Exception as e:
            log_debug(f"Error in Web_Agent.__init__: {str(e)}")
            log_debug(f"Traceback:\n{traceback.format_exc()}")
            raise

    def process_request(self, user_request: str) -> list:
        log_debug(f"Processing request: {user_request}")
        try:
            log_debug(f"Calling _process_web_search with num_results: {self.num_results}")
            results = self._process_web_search(user_request)
            log_debug(f"_process_web_search completed. Number of results: {len(results)}")
            return results
        except Exception as e:
            log_debug(f"Error in process_request: {str(e)}")
            log_debug(f"Traceback:\n{traceback.format_exc()}")
            if os.environ.get('DEBUG') == 'True':
                print(f"Error in Web_Agent: {str(e)}")
            return [{"title": "Error", "url": "", "description": f"An error occurred while processing your request: {str(e)}"}]

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
        log_debug(f"Deduplication completed. Number of unique results: {len(unique_results)}")
        return unique_results

    def _get_web_content(self, url: str) -> str:
        return self.tools["WebGetContents_Tool"](url)

    def _summarize_web_content(self, content: str, user_request: str, url: str, description: str) -> str:
        summary_prompt = self._create_summary_prompt(content, user_request, url, description)
        return self.provider.generate(summary_prompt, max_tokens=self.max_tokens)

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
        return self.provider.generate(combined_prompt, max_tokens=self.max_tokens)