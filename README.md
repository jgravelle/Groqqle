# Groqqle: Your AI-Powered Search Engine

![Groqqle Logo](https://github.com/user-attachments/assets/1ff3686d-130f-4b63-ae4d-f0cf7bb6562e)


Groqqle is an innovative, AI-powered search engine that combines the power of large language models with web search capabilities. It offers both a user-friendly web interface and a robust API for seamless integration into your projects.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

## 🌟 Features

- 🔍 Advanced search capabilities powered by AI
- 🖥️ Intuitive web interface for easy searching
- 🚀 Fast and efficient results using Groq's high-speed inference
- 🔌 RESTful API for programmatic access
- 🔒 Secure handling of API keys
- 📊 Option to view results in JSON format
- 🔄 Extensible architecture for multiple AI providers

![Groqqle Features](image-5.png)    

## 🛠️ Installation

1. Clone the repository:
   ```
   git clone https://github.com/jgravelle/Groqqle.git
   cd Groqqle
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the project root and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## 🚀 Usage

### Web Interface

1. Start the Groqqle application:
   ```
   streamlit run Groqqle.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Enter your search query in the search bar and click "Groqqle Search" or press Enter.

4. View your results! Toggle the "JSON Results" checkbox to see the raw JSON data.

![Groqqle Web Interface](image-2.png)

### API

The Groqqle API allows you to programmatically access search results. Here's how to use it:

1. Start the Groqqle application in API mode:
   ```
   python Groqqle.py api
   ```

2. The API server will start running on `http://127.0.0.1:5000`.

3. Send a POST request to `http://127.0.0.1:5000/search` with the following JSON body:
   ```json
   {
     "query": "your search query"
   }
   ```

   Note: The API key is now managed through environment variables, so you don't need to include it in the request.

4. The API will return a JSON response with your search results.

Example using Python's `requests` library:

```python
import requests

url = "http://127.0.0.1:5000/search"
data = {
    "query": "Groq"
}
response = requests.post(url, json=data)
results = response.json()
print(results)

Make sure you have set the `GROQ_API_KEY` in your environment variables or `.env` file before starting the API server.
```

![Groqqle API Usage](image-3.png)

## 🔄 AI Providers

While Groqqle is optimized for use with Groq's lightning-fast inference capabilities, we've also included stubbed-out provider code for Anthropic. This demonstrates how easily other AI providers can be integrated into the system. 

Please note that while other providers can be added, they may not match the exceptional speed offered by Groq. Groq's high-speed inference is a key feature that sets Groqqle apart in terms of performance.

### Why Groqqle is Helpful: Focus on the API Feature

**Groqqle** is a powerful AI-driven search engine designed to enhance search capabilities by integrating advanced AI models with high-speed web search. The **API feature** is one of the most significant aspects of Groqqle, offering robust programmatic access to its search functionalities. Here’s why the Groqqle API is particularly useful:

#### 1. **Seamless Integration into Applications**
   - The Groqqle API allows developers to integrate advanced AI-powered search directly into their applications, websites, or services. This enables them to leverage Groqqle's capabilities without requiring users to interact with a separate web interface.
   
#### 2. **Customizable Search Solutions**
   - By using the API, developers can tailor search functionalities to meet specific business needs, such as filtering results, customizing search algorithms, or integrating with other data sources. This flexibility makes Groqqle suitable for a wide range of applications, from e-commerce platforms to research tools.

#### 3. **High-Speed Performance**
   - Powered by Groq’s high-speed inference, the API delivers search results quickly, even when handling complex queries. This ensures a smooth and efficient user experience, critical for real-time applications.

#### 4. **JSON Format for Easy Data Handling**
   - The API returns results in JSON format, a standard data format that's easy to parse and manipulate in most programming languages. This simplifies the integration process and allows developers to quickly incorporate search results into their applications.

#### 5. **Secure and Scalable**
   - Groqqle's API uses secure handling of API keys, ensuring that only authorized requests are processed. This security is essential for protecting sensitive data and maintaining trust with users. Additionally, the API is designed to be scalable, allowing it to handle increasing demand as your project grows.

#### 6. **Extensibility with Multiple AI Providers**
   - Although optimized for Groq’s models, the API’s architecture is extensible, allowing developers to integrate other AI providers as needed. This flexibility is ideal for projects that may require different AI capabilities or want to experiment with various models.

#### **Use Cases for the Groqqle API**

- **E-commerce Platforms:** Implementing advanced search functionality to help users find products faster and more accurately based on their queries.
- **Content Management Systems:** Enabling powerful content search and retrieval across large databases, enhancing user experience and content discovery.
- **Research and Analytics Tools:** Providing quick and relevant search results for researchers needing to sift through vast amounts of data.
- **Customer Support Systems:** Integrating with chatbots or helpdesk software to provide instant answers to customer inquiries by searching a knowledge base.
- **News Aggregators:** Allowing for real-time search and aggregation of news articles based on user interests.

The Groqqle API is a versatile tool that empowers developers to build intelligent, responsive, and scalable search functionalities into their projects, enhancing the overall user experience and meeting specific business objectives.

## 🤝 Contributing

We welcome contributions to Groqqle! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information.  Mention J. Gravelle in your docs (README, etc.) and/or code.  He's kind of full of himself.

## 📞 Contact

J. Gravelle - j@gravelle.us - https://j.gravelle.us

Project Link: [https://github.com/jgravelle/Groqqle](https://github.com/jgravelle/Groqqle)

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for their powerful and incredibly fast language models
- [Streamlit](https://streamlit.io/) for the amazing web app framework
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance API framework
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for web scraping capabilities

![Groqqle Footer](https://github.com/user-attachments/assets/1ff3686d-130f-4b63-ae4d-f0cf7bb6562e)
