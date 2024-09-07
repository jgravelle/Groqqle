import os
import sys
import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import quote_plus, urljoin

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents.Base_Agent import Base_Agent
from providers.provider_factory import ProviderFactory

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def log_debug(message):
    if DEBUG:
        print(f"Debug: {message}")

class News_Agent(Base_Agent):
    def __init__(self, api_key, provider_name='groq', num_results=10, max_tokens=4096, model="mixtral-8x7b-32768", temperature=0.5, comprehension_grade=8):
        log_debug(f"Initializing News_Agent with provider_name: {provider_name}, num_results: {num_results}, max_tokens: {max_tokens}, model: {model}, temperature: {temperature}, comprehension_grade: {comprehension_grade}")
        
        if not api_key:
            log_debug("API key is missing or empty")
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.num_results = num_results
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temperature
        self.comprehension_grade = comprehension_grade

        try:
            log_debug(f"Attempting to get provider with API key: {api_key[:5]}...")
            self.provider = ProviderFactory.get_provider(provider_name, api_key)
            log_debug("Provider obtained successfully")
        except Exception as e:
            log_debug(f"Error in News_Agent.__init__: {str(e)}")
            raise

    def process_request(self, user_request: str) -> List[Dict[str, Any]]:
        log_debug(f"Processing request: {user_request}")
        log_debug(f"Using comprehension grade: {self.comprehension_grade}, temperature: {self.temperature}")
        
        try:
            search_results = self._perform_news_search(user_request)
            log_debug(f"News search completed. Number of results: {len(search_results)}")
            
            if not search_results:
                log_debug("No search results found")
                return [{"title": "No Results", "url": "", "description": "I'm sorry, but I couldn't find any relevant news for your request."}]

            return search_results[:self.num_results]  # Return top num_results
        except Exception as e:
            log_debug(f"Error in process_request: {str(e)}")
            return [{"title": "Error", "url": "", "description": f"An error occurred while processing your request: {str(e)}"}]

    def _perform_news_search(self, query: str) -> List[Dict[str, Any]]:
        log_debug(f"Performing news search with query: {query} and num_results: {self.num_results}")
        
        encoded_query = quote_plus(query)
        base_url = f'https://www.bing.com/news/search?q={encoded_query}&qft=interval%3d"7"&qft=sortbydate'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        results = []
        page = 1
        while len(results) < self.num_results:
            url = f"{base_url}&count={min(30, self.num_results - len(results))}&first={(page-1)*30+1}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                news_cards = soup.find_all('div', class_='news-card')
                
                if not news_cards:
                    break  # No more results found
                
                for card in news_cards:
                    if len(results) >= self.num_results:
                        break
                    
                    title_elem = card.find('a', class_='title')
                    if title_elem:
                        title = title_elem.text.strip()
                        url = urljoin("https://www.bing.com", title_elem.get('href', ''))
                        
                        snippet_elem = card.find('div', class_='snippet')
                        description = snippet_elem.text.strip() if snippet_elem else ''
                        
                        source_elem = card.find('div', class_='source')
                        source = source_elem.text.strip() if source_elem else ''
                        
                        timestamp_elem = card.find('span', attrs={'aria-label': True})
                        timestamp = timestamp_elem['aria-label'] if timestamp_elem else ''
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "description": description,
                            "source": source,
                            "timestamp": timestamp
                        })
                
                page += 1
                time.sleep(1)  # Add a small delay between requests to avoid rate limiting
            except Exception as e:
                log_debug(f"Error in _perform_news_search: {str(e)}")
                break

        log_debug(f"News search completed successfully. Number of results: {len(results)}")
        return results[:self.num_results]  # Ensure we don't return more than requested

    def _summarize_news_content(self, content: str, url: str) -> Dict[str, str]:
        log_debug(f"Summarizing content from URL: {url}")
        summary_prompt = self._create_summary_prompt(content, url)
        log_debug(f"Summary prompt: {summary_prompt[:500]}...")  # Log first 500 characters of the prompt
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
        Summarize the following news content from {url} for {grade_description}:
        {content[:6000]}  # Limit content to first 6000 characters

        Your task is to provide a comprehensive and informative synopsis of the main subject matter, along with an SEO-optimized headline. Follow these guidelines:

        1. Generate an SEO-optimized headline that:
        - Captures user interest without sensationalism
        - Accurately represents the main topic
        - Uses relevant keywords
        - Is concise (ideally 50-60 characters)
        - Maintains professionalism
        - Does not begin with anything akin to "Imagine" or "Picture this"
        
        2. Format your headline exactly as follows:
        HEADLINE: [Your SEO-optimized headline here]

        3. Write your summary using the inverted pyramid style:
        - Start with a strong lede (opening sentence) that entices readers and summarizes the most crucial information
        - Present the most important information first
        - Follow with supporting details and context
        - End with the least essential information
        - Don't mention the parts of the pyramid. Just follow the structure. No need to say "in conclusion" in the conclusion, for example.

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
        10.  Never discuss or reference the reference material, article, video, source, or author in the summary

        Use a neutral, journalistic tone, and ensure that you're reporting the facts as presented in the content, not adding personal opinions or speculation.

        Format your response as follows:
        HEADLINE: [Your SEO-optimized headline here]

        [Your comprehensive summary here, following the inverted pyramid style]
        """

    def _format_summary(self, summary: str, url: str) -> Dict[str, str]:
        parts = summary.split('\n', 1)
        if len(parts) == 2 and parts[0].startswith('HEADLINE:'):
            headline = parts[0].replace('HEADLINE:', '').strip()
            body = parts[1].strip()
        else:
            sentences = summary.split('. ')
            headline = sentences[0].strip()
            body = '. '.join(sentences[1:]).strip()

        if not headline or headline == "Summary of News Content":
            headline = f"Summary of {url.split('//')[1].split('/')[0]}"

        return {
            "title": headline,
            "url": url,
            "description": body
        }

if __name__ == "__main__":
    # Example usage
    api_key = "your_api_key_here"
    agent = News_Agent(api_key)
    results = agent.process_request("Politics")
    for result in results:
        print(f"Title: {result['title']}")
        print(f"Source: {result['source']}")
        print(f"URL: {result['url']}")
        print(f"Description: {result['description']}")
        print(f"Timestamp: {result['timestamp']}")
        print("---")