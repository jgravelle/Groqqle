#!/usr/bin/env python3
"""
Static search example that returns hardcoded but realistic search results.
This avoids dependency and network issues while demonstrating the API format.
"""

def static_search_results(query="quantum computing"):
    """
    Return static search results for demo purposes.
    Using real search results structure but with fixed content.
    """
    
    if "quantum computing" in query.lower():
        return [
            {
                "title": "Quantum computing - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Quantum_computing",
                "description": "Quantum computing is a type of computing that uses quantum mechanical phenomena, such as superposition and entanglement, to perform operations on data. Unlike classical computing, which operates on binary bits (0s and 1s), quantum computing uses quantum bits or 'qubits'."
            },
            {
                "title": "What is quantum computing? | IBM",
                "url": "https://www.ibm.com/quantum/what-is-quantum-computing",
                "description": "Quantum computing harnesses the phenomena of quantum mechanics to deliver a huge leap forward in computation to solve certain problems. IBM Quantum is advancing quantum computing from research to reality."
            },
            {
                "title": "Quantum Computing | Microsoft Azure",
                "url": "https://azure.microsoft.com/en-us/products/quantum",
                "description": "Solve problems that would take today's computers billions of years in hours or days with Microsoft Quantum computing solutions."
            },
            {
                "title": "Quantum Computing: Definition, Basics, Present And Future",
                "url": "https://www.forbes.com/sites/bernardmarr/2021/04/05/what-is-quantum-computing-a-super-easy-explanation-for-anyone/",
                "description": "Quantum computing uses the principles of quantum physics to solve complex problems much faster than classical computers. It leverages qubits that can exist in multiple states simultaneously, enabling exponentially faster computing for specific tasks."
            },
            {
                "title": "Google Quantum AI",
                "url": "https://quantumai.google/",
                "description": "Google's quantum computing research focuses on developing quantum processors and algorithms. The Quantum AI lab has achieved breakthroughs including quantum supremacy with the Sycamore processor."
            }
        ]
    elif "artificial intelligence" in query.lower():
        return [
            {
                "title": "Artificial intelligence - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "description": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals."
            },
            {
                "title": "What is Artificial Intelligence (AI)? | IBM",
                "url": "https://www.ibm.com/cloud/learn/what-is-artificial-intelligence",
                "description": "Artificial intelligence leverages computers and machines to mimic the problem-solving and decision-making capabilities of the human mind."
            },
            {
                "title": "OpenAI - Technology company",
                "url": "https://openai.com/",
                "description": "OpenAI is an AI research and deployment company. Our mission is to ensure that artificial general intelligence benefits all of humanity."
            },
            {
                "title": "Anthropic - AI research and deployment company",
                "url": "https://www.anthropic.com/",
                "description": "Anthropic is an AI safety company building reliable, interpretable, and steerable AI systems for users through foundational models like Claude."
            },
            {
                "title": "What Is Artificial Intelligence? (AI)",
                "url": "https://www.investopedia.com/terms/a/artificial-intelligence-ai.asp",
                "description": "Artificial intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and act like humans. The term may also be applied to any machine that exhibits traits associated with a human mind."
            }
        ]
    else:
        # Default results for any other query
        return [
            {
                "title": f"Search results for: {query}",
                "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "description": f"This is a demo showing the structure of search results that would be returned when searching for '{query}'. In a real implementation, these would be actual results from the web."
            },
            {
                "title": "Example Result 1",
                "url": "https://example.com/result1",
                "description": "This is an example search result that shows the format of data returned by the Groqqle API."
            },
            {
                "title": "Example Result 2",
                "url": "https://example.com/result2",
                "description": "Search results typically include a title, URL, and description snippet from the webpage."
            },
        ]

def main():
    """Demo the static search functionality"""
    print("=== Groqqle API Demo - Static Search ===\n")
    
    # Try different queries
    queries = [
        "quantum computing", 
        "artificial intelligence",
        "example query"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = static_search_results(query)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            description = result.get('description', 'No description')
            # Truncate long descriptions for display
            if len(description) > 100:
                description = description[:100] + "..."
            print(f"Description: {description}")
    
    print("\n=== This demonstrates the API response format ===")
    print("In a real implementation, these results would come from web searches")
    print("The Groqqle API returns data in this exact format:")
    print("""
    [
        {
            "title": "Result Title",
            "url": "https://example.com/page",
            "description": "Description snippet from the page..."
        },
        ...more results...
    ]
    """)

if __name__ == "__main__":
    main()