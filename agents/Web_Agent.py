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