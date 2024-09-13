# Groqqle 2.1: Your Free AI-Powered Search Engine and Content Generator

![Groqqle Logo](https://github.com/user-attachments/assets/1ff3686d-130f-4b63-ae4d-f0cf7bb6562e)

Groqqle 2.1 is a revolutionary, free AI web search and API that instantly returns ORIGINAL content derived from source articles, websites, videos, and even foreign language sources, for ANY target market of ANY reading comprehension level! It combines the power of large language models with advanced web and news search capabilities, offering a user-friendly web interface, a robust API, and now a powerful Groqqle_web_tool for seamless integration into your projects.

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
- 🛠️ Groqqle_web_tool for direct integration into Python projects
- 🔒 Secure handling of API keys through environment variables
- 📊 Option to view results in JSON format
- 🔄 Extensible architecture for multiple AI providers
- 🔢 Configurable number of search results
- 🔤 Customizable maximum token limit for responses

![Groqqle Features](image-5.png)

## 🚀 Why Choose Groqqle 2.1?

Groqqle 2.1 stands out as a powerful tool for developers, researchers, content creators, and businesses:

- **Instant Original Content**: Generate fresh, unique content on any topic, saving time and resources.
- **Multilingual Capabilities**: Process and synthesize information from foreign language sources, breaking down language barriers.
- **Flexible Output**: Tailor content to any target market or audience, adjusting complexity and style as needed.
- **Easy Integration**: Developers can quickly incorporate Groqqle into their projects using the web interface, API, or the new Groqqle_web_tool.
- **Customizable Comprehension Levels**: Adjust the output to match any reading level, from elementary to expert.
- **Diverse Source Processing**: Extract insights from various media types, including articles, websites, and videos.

Whether you're building a content aggregation platform, a research tool, or an AI-powered writing assistant, Groqqle 2.1 provides the flexibility and power you need to deliver outstanding results.

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

5. Install PocketGroq:
   ```bash
   pip install pocketgroq
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

### Groqqle_web_tool

The new Groqqle_web_tool allows you to integrate Groqqle's powerful search and content generation capabilities directly into your Python projects. Here's how to use it:

1. Import the necessary modules:
   ```python
   from pocketgroq import GroqProvider
   from groqqle_web_tool import Groqqle_web_tool
   ```

2. Initialize the GroqProvider and Groqqle_web_tool:
   ```python
   groq_provider = GroqProvider(api_key="your_groq_api_key_here")
   groqqle_tool = Groqqle_web_tool(api_key="your_groq_api_key_here")
   ```

3. Define the tool for PocketGroq:
   ```python
   tools = [
       {
           "type": "function",
           "function": {
               "name": "groqqle_web_search",
               "description": "Perform a web search using Groqqle",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "query": {
                           "type": "string",
                           "description": "The search query"
                       }
                   },
                   "required": ["query"]
               }
           }
       }
   ]

   def groqqle_web_search(query):
       results = groqqle_tool.run(query)
       return results
   ```

4. Use the tool in your project:
   ```python
   user_message = "Search for the latest developments in quantum computing"
   system_message = "You are a helpful assistant. Use the Groqqle web search tool to find information."

   response = groq_provider.generate(
       system_message,
       user_message,
       tools=tools,
       tool_choice="auto"
   )

   print(response)
   ```

This new tool allows for seamless integration of Groqqle's capabilities into your Python projects, enabling powerful search and content generation without the need for a separate API or web interface.

## 🔄 AI Providers

While Groqqle is optimized for use with Groq's lightning-fast inference capabilities, we've also included stubbed-out provider code for Anthropic. This demonstrates how easily other AI providers can be integrated into the system. 

To use a different provider, you can modify the `provider_name` parameter when initializing the `Web_Agent` in the `Groqqle.py` file.

## 🎛️ Configuration Options

Groqqle now supports the following configuration options:

- `num_results`: Number of search results to return (default: 10)
- `max_tokens`: Maximum number of tokens for the AI model response (default: 4096)
- `model`: The Groq model to use (default: "llama3-8b-8192")
- `temperature`: The temperature setting for content generation (default: 0.0)
- `comprehension_grade`: The target comprehension grade level (default: 8)

These options can be set when running the application, making API requests, or initializing the Groqqle_web_tool.

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
- [PocketGroq](https://github.com/CaseCal/pocketgroq) for the Groq provider integration

![Groqqle Footer](https://github.com/user-attachments/assets/1ff3686d-130f-4b63-ae4d-f0cf7bb6562e)


= = = = = = = = =

## MAC INSTALLATION INSTRUCTIONS (untested, by request)

To install **Groqqle 2.1** on your Mac, follow the step-by-step guide below. This installation process involves setting up a Python environment using Conda, installing necessary packages, and configuring environment variables.

---

## **Prerequisites**

Before starting, ensure you have the following installed on your Mac:

1. **Git**: For cloning the Groqqle repository.
2. **Conda (Anaconda or Miniconda)**: For managing Python environments.
3. **Python 3.11**: Groqqle requires Python 3.11 (Conda will handle this).
4. **Groq API Key**: You'll need a valid API key from Groq.

---

## **Step-by-Step Installation Guide**

### **1. Install Git (if not already installed)**

**Check if Git is installed:**

Open **Terminal** (Finder > Applications > Utilities > Terminal) and run:

```bash
git --version
```

- **If Git is installed**, you'll see a version number.
- **If not installed**, you'll be prompted to install the Xcode Command Line Tools. Follow the on-screen instructions.

**Alternatively, install Git using Homebrew:**

If you prefer using Homebrew (a package manager for macOS):

1. **Install Homebrew** (if not already installed):

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Git via Homebrew:**

   ```bash
   brew install git
   ```

### **2. Install Conda (Anaconda or Miniconda)**

Groqqle uses Conda to manage its Python environment.

**Option A: Install Miniconda (Recommended for simplicity)**

1. **Download Miniconda Installer:**

   - Go to the [Miniconda installation page](https://docs.conda.io/en/latest/miniconda.html).
   - Download the **macOS installer** matching your Mac's architecture:
     - **Intel Macs**: `Miniconda3-latest-MacOSX-x86_64.sh`
     - **Apple Silicon (M1/M2)**: `Miniconda3-latest-MacOSX-arm64.sh`

2. **Run the Installer:**

   ```bash
   # Navigate to your Downloads folder
   cd ~/Downloads

   # Run the installer (replace with your downloaded file's name)
   bash Miniconda3-latest-MacOSX-x86_64.sh  # For Intel Macs
   # or
   bash Miniconda3-latest-MacOSX-arm64.sh   # For M1/M2 Macs
   ```

3. **Follow the On-Screen Prompts:**

   - Press **Enter** to proceed.
   - Type `yes` to agree to the license agreement.
   - Press **Enter** to confirm the installation location (default is recommended).
   - Type `yes` to initialize Conda.

4. **Restart Terminal or Source Conda:**

   ```bash
   # For Bash shell
   source ~/.bash_profile

   # For Zsh shell (default on macOS Catalina and later)
   source ~/.zshrc
   ```

**Option B: Install Anaconda**

If you prefer a full Anaconda installation (larger download), download it from the [Anaconda distribution page](https://www.anaconda.com/products/individual).

### **3. Clone the Groqqle Repository**

1. **Open Terminal** and navigate to your desired directory:

   ```bash
   cd ~  # or wherever you want to clone the repository
   ```

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/jgravelle/Groqqle.git
   ```

3. **Navigate into the Project Directory:**

   ```bash
   cd Groqqle
   ```

### **4. Create and Activate a Conda Environment**

1. **Create a New Environment with Python 3.11:**

   ```bash
   conda create --name groqqle python=3.11
   ```

2. **Activate the Environment:**

   ```bash
   conda activate groqqle
   ```

   - **Note**: If you receive an error about activation, initialize Conda for your shell:

     ```bash
     conda init
     ```

     Then restart Terminal or source your shell configuration:

     ```bash
     source ~/.bash_profile  # For Bash
     source ~/.zshrc         # For Zsh
     ```

### **5. Install the Required Packages**

1. **Install Dependencies from `requirements.txt`:**

   ```bash
   pip install -r requirements.txt
   ```

   - **Troubleshooting**:
     - If you encounter errors, especially on M1/M2 Macs, see the **Apple Silicon Compatibility** section below.

### **6. Set Up Your Environment Variables**

1. **Create a `.env` File in the Project Root:**

   ```bash
   touch .env
   ```

2. **Add Your Groq API Key:**

   Open the `.env` file with a text editor:

   ```bash
   open .env  # Opens the file in the default text editor
   ```

   Add the following line (replace `your_api_key_here` with your actual API key):

   ```env
   GROQ_API_KEY=your_api_key_here
   ```

3. **Save and Close the File.**

   - **Alternatively**, set the environment variable in Terminal (session-specific):

     ```bash
     export GROQ_API_KEY=your_api_key_here
     ```

### **7. Install PocketGroq**

1. **Install via Pip:**

   ```bash
   pip install pocketgroq
   ```

### **8. Verify the Installation**

#### **Option A: Run the Web Interface**

1. **Start the Application:**

   ```bash
   streamlit run Groqqle.py
   ```

2. **Access the Interface:**

   - Open the URL provided in the Terminal output (typically `http://localhost:8501`) in your web browser.

#### **Option B: Run the API Server**

1. **Start the API Server:**

   ```bash
   python Groqqle.py api --num_results 20 --max_tokens 4096
   ```

2. **Test the API:**

   - The API will be running at `http://127.0.0.1:5000`.
   - You can send POST requests to this endpoint as per the documentation.

---

## **Apple Silicon Compatibility (M1/M2 Macs)**

Some Python packages may have compatibility issues on Apple Silicon. Here's how to address them:

1. **Install Rosetta 2 (if not already installed):**

   ```bash
   softwareupdate --install-rosetta
   ```

2. **Run Terminal in Rosetta Mode:**

   - **Locate Terminal App**:
     - Go to `Applications` > `Utilities`.
   - **Duplicate Terminal**:
     - Right-click on `Terminal` and select `Duplicate`.
     - Rename the duplicated app to `Terminal Rosetta`.
   - **Enable Rosetta for the Duplicated Terminal**:
     - Right-click `Terminal Rosetta` > `Get Info`.
     - Check the box **"Open using Rosetta"**.
   - **Use Terminal Rosetta**:
     - Open `Terminal Rosetta` and proceed with the installation steps.

3. **Create an x86_64 Conda Environment:**

   ```bash
   CONDA_SUBDIR=osx-64 conda create --name groqqle python=3.11
   conda activate groqqle
   ```

4. **Proceed with Installation Steps 5 to 8.**

---

## **Additional Notes**

- **Ensure Python Version**: Verify that Python 3.11 is active in your environment:

  ```bash
  python --version
  ```

- **Install Xcode Command Line Tools**: Some packages require compilation:

  ```bash
  xcode-select --install
  ```

- **Troubleshooting Package Installation**: If `pip install -r requirements.txt` fails:

  - Install packages individually to identify the problematic one.
  - Use Conda to install problematic packages:

    ```bash
    conda install package-name
    ```

- **Using Virtual Environments**: If you prefer `venv` or `virtualenv` over Conda:

  ```bash
  python3.11 -m venv groqqle_env
  source groqqle_env/bin/activate
  pip install -r requirements.txt
  ```

---

## **Using Groqqle**

Refer to the **Usage** section in the documentation for detailed instructions on:

- **Web Interface Usage**
- **API Usage**
- **Integration with Python Projects using `groqqle_web_tool`**

---

## **Common Issues and Solutions**

- **Streamlit Not Found**:

  ```bash
  pip install streamlit
  ```

- **Environment Activation Fails**:

  Ensure Conda is initialized for your shell:

  ```bash
  conda init
  source ~/.bash_profile  # For Bash
  source ~/.zshrc         # For Zsh
  ```

- **Permission Errors**:

  Run commands with appropriate permissions or adjust file permissions:

  ```bash
  sudo chown -R $(whoami) ~/.conda
  ```

- **Missing Dependencies**:

  Install missing system dependencies via Homebrew:

  ```bash
  brew install [package-name]
  ```

---

## **Support**

- **Groqqle GitHub Repository**: [https://github.com/jgravelle/Groqqle](https://github.com/jgravelle/Groqqle)
- **Contact**: J. Gravelle - [j@gravelle.us](mailto:j@gravelle.us)
- **Issues**: If you encounter problems, consider opening an issue on the GitHub repository.

---

By following these steps, you should have Groqqle 2.1 installed and running on your Mac. If you need further assistance, feel free to ask!
