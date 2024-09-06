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
    def __init__(self, api_key, provider_name='groq', num_results=10, max_tokens=4096, model="mixtral-8x7b-32768", temperature=0.5, comprehension_grade=8, summary_length=300):
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

    def process_request(self, user_request: str) -> list:
        log_debug(f"Processing request: {user_request}")
        log_debug(f"Using comprehension grade: {self.comprehension_grade}, temperature: {self.temperature}")
        try:
            if self._is_url(user_request):
                log_debug(f"Request is a URL: {user_request}")
                return self._process_url_request(user_request)
            else:
                log_debug(f"Request is a search query: {user_request}")
                return self._process_web_search(user_request)
        except Exception as e:
            log_debug(f"Error in process_request: {str(e)}")
            log_debug(f"Traceback:\n{traceback.format_exc()}")
            if os.environ.get('DEBUG') == 'True':
                print(f"Error in Web_Agent: {str(e)}")
            return [{"title": "Error", "url": "", "description": f"An error occurred while processing your request: {str(e)}"}]
        
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
            return [{"title": "Error", "url": url, "description": "Failed to retrieve content from the URL."}]

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