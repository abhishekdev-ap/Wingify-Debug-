## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
import requests

## Creating search tool using Serper API
@tool("Search the Internet")
def search_tool(search_query: str) -> str:
    """Search the internet for financial news, market data, and industry information.
    Use this to find current market context, competitor analysis, and industry benchmarks.
    
    Args:
        search_query (str): The search query string.
    
    Returns:
        str: Search results with titles, snippets, and links.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Search unavailable: SERPER_API_KEY not configured."
    
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": search_query, "num": 5},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("organic", [])[:5]:
            results.append(f"- {item.get('title', '')}: {item.get('snippet', '')} ({item.get('link', '')})")
        
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

## Creating custom pdf reader tool
@tool("Financial Document Reader")
def read_data_tool(file_path: str = 'data/TSLA-Q2-2025-Update.pdf') -> str:
    """Read and extract text content from the financial PDF document at the given file path.
    Use this tool to read the uploaded financial document for analysis.
    If no file_path is provided, it reads the default sample document.
    """
    from pypdf import PdfReader

    if not file_path:
        file_path = 'data/TSLA-Q2-2025-Update.pdf'

    reader = PdfReader(file_path)
    full_report = ""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            # Clean and format the financial document data
            # Remove extra whitespaces and format properly
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
            full_report += content + "\n"

    # Truncate to stay within LLM token limits (keep most important pages)
    MAX_CHARS = 8000  # ~2000 tokens, safe for all free-tier LLMs
    if len(full_report) > MAX_CHARS:
        full_report = full_report[:MAX_CHARS] + "\n\n[... Document truncated for token limit. Key financial data shown above ...]"

    return full_report


## Creating Investment Analysis Tool
@tool("Investment Analysis Tool")
def analyze_investment_tool(financial_document_data: str) -> str:
    """Process and analyze financial document data for investment insights.
    
    Args:
        financial_document_data (str): The raw text data from a financial document.
    
    Returns:
        str: Processed financial data ready for investment analysis
    """
    processed_data = financial_document_data

    # Clean up the data format - remove double spaces
    i = 0
    while i < len(processed_data):
        if processed_data[i:i+2] == "  ":  # Remove double spaces
            processed_data = processed_data[:i] + processed_data[i+1:]
        else:
            i += 1

    return processed_data


## Creating Risk Assessment Tool
@tool("Risk Assessment Tool")
def create_risk_assessment_tool(financial_document_data: str) -> str:
    """Create a risk assessment from financial document data.
    
    Args:
        financial_document_data (str): The raw text data from a financial document.
    
    Returns:
        str: Risk assessment analysis of the financial data
    """
    # Basic risk factor extraction
    risk_keywords = ["risk", "liability", "debt", "loss", "decline", "uncertainty", "volatility"]
    lines = financial_document_data.split("\n")
    risk_factors = []
    
    for line in lines:
        if any(keyword in line.lower() for keyword in risk_keywords):
            risk_factors.append(line.strip())
    
    if risk_factors:
        return "Risk factors identified:\n" + "\n".join(risk_factors[:20])
    return "No significant risk factors identified in the provided data."