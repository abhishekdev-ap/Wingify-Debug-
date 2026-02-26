## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, read_data_tool, analyze_investment_tool, create_risk_assessment_tool

## Task 1: Verify the uploaded financial document
verification = Task(
    description=(
        "Verify that the uploaded document is a valid financial document.\n"
        "Read the document using the Financial Document Reader tool.\n"
        "Identify the document type (e.g., quarterly report, annual filing, earnings update).\n"
        "Extract key metadata: company name, reporting period, date of publication.\n"
        "Confirm that the document contains financial data suitable for analysis.\n"
        "Flag any issues such as incomplete data, corrupted content, or non-financial content."
    ),
    expected_output=(
        "A verification report containing:\n"
        "- Document type classification\n"
        "- Company name and reporting period\n"
        "- Confirmation of financial data availability\n"
        "- List of key financial sections found (e.g., Income Statement, Balance Sheet, Cash Flow)\n"
        "- Any data quality issues or warnings"
    ),
    agent=verifier,
    tools=[read_data_tool],
    async_execution=False,
)

## Task 2: Analyze the financial document based on user query
analyze_financial_document = Task(
    description=(
        "Perform a comprehensive financial analysis of the document to address the user's query: {query}.\n"
        "Read the financial document thoroughly using the Financial Document Reader tool.\n"
        "Extract and analyze key financial metrics including revenue, profit margins, EPS, debt ratios, "
        "and cash flow figures.\n"
        "Identify important trends, year-over-year changes, and notable financial events.\n"
        "Search the internet for relevant market context and industry benchmarks if needed.\n"
        "Provide data-backed insights that directly address the user's query."
    ),
    expected_output=(
        "A detailed financial analysis report including:\n"
        "- Executive summary of key findings\n"
        "- Key financial metrics with actual figures from the document\n"
        "- Trend analysis and year-over-year comparisons\n"
        "- Industry context and benchmarks (from internet research)\n"
        "- Direct answers to the user's specific query\n"
        "- All figures must be sourced from the actual document"
    ),
    agent=financial_analyst,
    tools=[read_data_tool, search_tool],
    async_execution=False,
)

## Task 3: Investment analysis based on financial data
investment_analysis = Task(
    description=(
        "Based on the financial analysis, provide well-reasoned investment recommendations.\n"
        "Review the financial data and analysis results from the previous task.\n"
        "Evaluate the company's financial health, growth prospects, and competitive positioning.\n"
        "Consider the user's query context: {query}\n"
        "Provide actionable investment insights with supporting data from the financial document.\n"
        "Include appropriate risk disclaimers and regulatory compliance notes."
    ),
    expected_output=(
        "A professional investment analysis report including:\n"
        "- Investment thesis summary (bull case and bear case)\n"
        "- Valuation assessment based on key financial ratios\n"
        "- Growth catalysts and potential headwinds\n"
        "- Specific, data-backed investment recommendations\n"
        "- Risk factors to consider\n"
        "- Disclaimer: This analysis is for informational purposes only and does not constitute financial advice"
    ),
    agent=investment_advisor,
    tools=[read_data_tool, analyze_investment_tool],
    async_execution=False,
)

## Task 4: Risk assessment of the financial position
risk_assessment = Task(
    description=(
        "Conduct a thorough risk assessment based on the financial document data.\n"
        "Analyze the company's financial risk profile including debt levels, liquidity, "
        "market exposure, and operational risks.\n"
        "Consider the user's query context: {query}\n"
        "Identify and categorize risks by severity and likelihood.\n"
        "Suggest risk mitigation strategies where applicable.\n"
        "Use established risk assessment frameworks for systematic evaluation."
    ),
    expected_output=(
        "A comprehensive risk assessment report including:\n"
        "- Risk summary with overall risk rating\n"
        "- Detailed breakdown by risk category (market, credit, liquidity, operational)\n"
        "- Risk severity matrix (high/medium/low for each identified risk)\n"
        "- Key risk indicators from the financial data\n"
        "- Recommended risk mitigation strategies\n"
        "- Comparison to industry risk benchmarks where available"
    ),
    agent=risk_assessor,
    tools=[read_data_tool, create_risk_assessment_tool],
    async_execution=False,
)