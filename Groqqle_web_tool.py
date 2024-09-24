from typing import Dict, Any, List
from tools.web_tools.WebSearch_Tool import WebSearch_Tool
from tools.web_tools.WebGetContents_Tool import WebGetContents_Tool
from providers.provider_factory import ProviderFactory

class Groqqle_web_tool:
    def __init__(self, api_key: str, provider_name: str = 'groq', num_results: int = 10, max_tokens: int = 4096, model: str = "llama3-8b-8192", temperature: float = 0.0, comprehension_grade: int = 8):
        self.api_key = api_key
        self.num_results = num_results
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temperature
        self.comprehension_grade = comprehension_grade
        self.provider = ProviderFactory.get_provider(provider_name, api_key)

    def run(self, query: str) -> List[Dict[str, Any]]:
        search_results = self._perform_web_search(query)
        filtered_results = self._filter_search_results(search_results)
        deduplicated_results = self._remove_duplicates(filtered_results)
        return deduplicated_results[:self.num_results]

    def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        return WebSearch_Tool(query, self.num_results * 2)

    def _filter_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [result for result in results if result['description'] and result['title'] != 'No title' and result['url'].startswith('https://')]

    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_urls = set()
        unique_results = []
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        return unique_results

    def _summarize_web_content(self, content: str, url: str) -> Dict[str, str]:
        summary_prompt = self._create_summary_prompt(content, url)
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

        4. Adjust the language complexity strictly targeted to the reading level for {grade_description}.

        5. Clearly explain the main topic or discovery being discussed
        6. Highlight key points, findings, or arguments presented in the content
        7. Provide relevant context or background information that helps understand the topic
        8. Mention any significant implications, applications, or future directions discussed
        9. If applicable, include important quotes or statistics that support the main points

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

        if not headline or headline == "Summary of Web Content":
            headline = f"Summary of {url.split('//')[1].split('/')[0]}"

        return {
            "title": headline,
            "url": url,
            "description": body
        }

    def summarize_url(self, url: str) -> Dict[str, str]:
        content = WebGetContents_Tool(url)
        if content:
            return self._summarize_web_content(content, url)
        else:
            return {"title": "Error", "url": url, "description": "Failed to retrieve content from the URL.  Some sites prohibit summarization.  Click URL to go there directly."}