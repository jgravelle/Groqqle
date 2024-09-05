# Groqqle 2.0: Your Free AI-Powered Search Engine and Content Generator

![Groqqle Logo](https://github.com/user-attachments/assets/1ff3686d-130f-4b63-ae4d-f0cf7bb6562e)

Groqqle 2.0 is a revolutionary, free AI web search and API that instantly returns ORIGINAL content derived from source articles, websites, videos, and even foreign language sources, for ANY target market of ANY reading comprehension level! It combines the power of large language models with advanced web and news search capabilities, offering both a user-friendly web interface and a robust API for seamless integration into your projects.

Developers can instantly incorporate Groqqle into their applications, providing a powerful tool for content generation, research, and analysis across various domains and languages.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)

## 🌟 Features

- 🔍 Advanced search capabilities powered by AI, covering web and news sources
- 📝 Instant generation of ORIGINAL content based on search results
- 🌐 Ability to process and synthesize information from various sources, including articles, websites, videos, and foreign language content
- 🎯 Customizable output for ANY target market or audience
- 📚 Adjustable reading comprehension levels to suit diverse user needs
- 🖥️ Intuitive web interface for easy searching and content generation
- 🚀 Fast and efficient results using Groq's high-speed inference
- 🔌 RESTful API for quick integration into developer projects
- 🔒 Secure handling of API keys through environment variables
- 📊 Option to view results in JSON format
- 🔄 Extensible architecture for multiple AI providers
- 🔢 Configurable number of search results
- 🔤 Customizable maximum token limit for responses

![Groqqle Features](image-5.png)

## 🚀 Why Choose Groqqle 2.0?

Groqqle 2.0 stands out as a powerful tool for developers, researchers, content creators, and businesses:

- **Instant Original Content**: Generate fresh, unique content on any topic, saving time and resources.
- **Multilingual Capabilities**: Process and synthesize information from foreign language sources, breaking down language barriers.
- **Flexible Output**: Tailor content to any target market or audience, adjusting complexity and style as needed.
- **Easy Integration**: Developers can quickly incorporate Groqqle into their projects, enhancing applications with powerful search and content generation capabilities.
- **Customizable Comprehension Levels**: Adjust the output to match any reading level, from elementary to expert.
- **Diverse Source Processing**: Extract insights from various media types, including articles, websites, and videos.

Whether you're building a content aggregation platform, a research tool, or an AI-powered writing assistant, Groqqle 2.0 provides the flexibility and power you need to deliver outstanding results.


## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jgravelle/Groqqle.git
   cd Groqqle
   ```

2. Set up a Conda environment:
   ```bash
   conda create --name groqqle python=3.11
   conda activate groqqle
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the project root and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

## 🚀 Usage

### Web Interface

1. Start the Groqqle application using Streamlit:
   ```bash
   streamlit run Groqqle.py
   ```

2. Open your web browser and navigate to the URL provided in the console output (typically `http://localhost:8501`).

3. Enter your search query in the search bar.

4. Choose between "Web" and "News" search using the radio buttons.

5. Click "Groqqle Search" or press Enter.

6. View your results! Toggle the "JSON Results" checkbox to see the raw JSON data.

7. For both web and news results, you can click the "📝" button next to each result to get a summary of the article or webpage.

![Groqqle Web Interface](image-2.png)

### API

The Groqqle API allows you to programmatically access search results for both web and news. Here's how to use it:

1. Start the Groqqle application in API mode:
   ```bash
   python Groqqle.py api --num_results 20 --max_tokens 4096
   ```

2. The API server will start running on `http://127.0.0.1:5000`.

3. Send a POST request to `http://127.0.0.1:5000/search` with the following JSON body:
   ```json
   {
     "query": "your search query",
     "num_results": 20,
     "max_tokens": 4096,
     "search_type": "web"  // Use "web" for web search or "news" for news search
   }
   ```

   Note: The API key is managed through environment variables, so you don't need to include it in the request.

4. The API will return a JSON response with your search results in the order: title, description, URL, source, and timestamp (for news results).

Example using Python's `requests` library:

```python
import requests

url = "http://127.0.0.1:5000/search"
data = {
    "query": "Groq",
    "num_results": 20,
    "max_tokens": 4096,
    "search_type": "news"  # Change to "web" for web search
}
response = requests.post(url, json=data)
results = response.json()
print(results)
```

Make sure you have set the `GROQ_API_KEY` in your environment variables or `.env` file before starting the API server.

![Groqqle API Usage](image-3.png)

### Simple and Useful Use Case Scenarios for Groqqle's API Mode

1. **Content Summarization**

   **Scenario:** A news aggregator app needs to summarize articles from various sources.

   ```python
   import requests

   def summarize_article(url):
       query = f"Summarize the main points of the article at {url}"
       response = requests.post("http://127.0.0.1:5000/search", json={"query": query})
       return response.json()["result"]

   article_url = "https://example.com/article"
   summary = summarize_article(article_url)
   print(summary)
   ```

2. **Competitive Analysis**

   **Scenario:** A business intelligence tool needs to compare a company with its competitors.

   ```python
   import requests

   def analyze_competitors(company_name, competitors):
       query = f"Compare {company_name} with its competitors: {', '.join(competitors)}"
       response = requests.post("http://127.0.0.1:5000/search", json={"query": query})
       return response.json()["result"]

   company = "TechCorp"
   competitors = ["RivalTech", "InnovaCo", "TechGiant"]
   analysis = analyze_competitors(company, competitors)
   print(analysis)
   ```

3. **Research Assistant**

   **Scenario:** An educational platform needs to provide comprehensive overviews of various topics.

   ```python
   import requests

   def research_topic(topic, depth="brief"):
       query = f"Provide a {depth} overview of {topic}, including key concepts and recent developments"
       response = requests.post("http://127.0.0.1:5000/search", json={"query": query})
       return response.json()["result"]

   topic = "Quantum Computing"
   research_result = research_topic(topic, "comprehensive")
   print(research_result)
   ```

4. **Sentiment Analysis of Product Reviews**

   **Scenario:** An e-commerce platform needs to analyze the sentiment of customer reviews.

   ```python
   import requests

   def analyze_sentiment(review):
       query = f"Analyze the sentiment of the following review: '{review}'"
       response = requests.post("http://127.0.0.1:5000/search", json={"query": query})
       return response.json()["result"]

   review = "The product is excellent and exceeded my expectations!"
   sentiment_analysis = analyze_sentiment(review)
   print(sentiment_analysis)
   ```

5. **Legal Document Summarization**

   **Scenario:** A legal firm needs to summarize lengthy legal documents into key points.

   ```python
   import requests

   def summarize_legal_document(document_url):
       query = f"Summarize the main points of the legal document at {document_url}"
       response = requests.post("http://127.0.0.1:5000/search", json={"query": query})
       return response.json()["result"]

   document_url = "https://example.com/legal-document"
   summary = summarize_legal_document(document_url)
   print(summary)
   ```

6. **News Monitoring and Analysis**

   **Scenario:** A media monitoring service needs to track and analyze news about specific topics or companies.

   ```python
   import requests

   def monitor_news(topic, days=1):
       query = f"Latest news about {topic} in the past {days} day(s)"
       response = requests.post("http://127.0.0.1:5000/search", json={
           "query": query,
           "search_type": "news",
           "num_results": 50
       })
       return response.json()["result"]

   topic = "Artificial Intelligence"
   news_analysis = monitor_news(topic, days=7)
   print(news_analysis)
   ```

## 🔄 AI Providers

While Groqqle is optimized for use with Groq's lightning-fast inference capabilities, we've also included stubbed-out provider code for Anthropic. This demonstrates how easily other AI providers can be integrated into the system. 

To use a different provider, you can modify the `provider_name` parameter when initializing the `Web_Agent` in the `Groqqle.py` file.

## 🎛️ Configuration Options

Groqqle now supports the following configuration options:

- `num_results`: Number of search results to return (default: 10)
- `max_tokens`: Maximum number of tokens for the AI model response (default: 4096)

These options can be set when running the application or when making API requests.

## 🤝 Contributing

We welcome contributions to Groqqle! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information. Mention J. Gravelle in your docs (README, etc.) and/or code. He's kind of full of himself.

## 📞 Contact

J. Gravelle - j@gravelle.us - https://j.gravelle.us

Project Link: [https://github.com/jgravelle/Groqqle](https://github.com/jgravelle/Groqqle)

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for their powerful and incredibly fast language models
- [Streamlit](https://streamlit.io/) for the amazing web app framework
- [Flask](https://flask.palletsprojects.com/) for the lightweight WSGI web application framework
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for web scraping capabilities

![Groqqle Footer](https://github.com/user-attachments/assets/1ff3686d-130f-4b63-ae4d-f0cf7bb6562e)
