# Multi-Agent Research and Analysis System

A beginner-friendly AI research application built with **Python,
LangChain, LangGraph, OpenAI, SerpAPI, and Streamlit**.

Enter a topic in the web interface. The workflow searches the web,
summarizes relevant results, analyzes the findings, and generates a
structured research report with source links.

## Features

-   **Streamlit interface** for entering a research topic and viewing
    results.
-   **Web research** using SerpAPI.
-   **LLM-powered research and analysis** using OpenAI through
    LangChain.
-   **LangGraph workflow** that connects the research, analysis, and
    report-writing steps.
-   **Source links** included in the report where available.
-   Simple project structure suitable for learning and extending.

## How the workflow works

1.  **Researcher:** Searches the web for the supplied topic and
    summarizes the returned search results.
2.  **Analyst:** Identifies key findings, trends, potential benefits,
    risks, and evidence gaps.
3.  **Writer:** Produces a structured report using the research and
    analysis.
4.  **Streamlit app:** Displays the report, research notes, analysis,
    and available source links.

> Note: This is a sequential LangGraph workflow with separate
> LLM-powered steps. It is a useful foundation for a multi-agent
> project, but it is not an unrestricted autonomous agent system. Search
> snippets should be checked against the original sources before relying
> on them.

## Tech stack

-   Python
-   OpenAI API
-   LangChain
-   LangGraph
-   SerpAPI
-   Streamlit
-   `python-dotenv`

## Project structure

``` text
multi_agent_research/
├── app.py
├── workflow.py
├── requirements.txt
├── .env
└── README.md
```

-   `app.py` --- Streamlit user interface.
-   `workflow.py` --- OpenAI model setup, research steps, and LangGraph
    workflow.
-   `requirements.txt` --- Python dependencies.
-   `.env` --- API keys; keep this file private.
-   `README.md` --- Project documentation.

## Prerequisites

-   Python installed on your computer.
-   An OpenAI API key with API billing/credits enabled.
-   A SerpAPI key.
-   Internet access.

A ChatGPT subscription and OpenAI API billing are separate. API usage
may incur charges according to the selected model's pricing and your
account's limits.

## Setup on Windows

### 1. Open the project folder

Open the project folder in VS Code, then open **Terminal → New
Terminal**.

### 2. Create a virtual environment

``` powershell
python -m venv .venv
```

### 3. Activate the environment

In PowerShell:

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the environment's Python
directly in the following steps:

``` powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Install dependencies

With the environment activated, run:

``` powershell
python -m pip install -r requirements.txt
```

Ensure `requirements.txt` includes the packages used by the project,
including:

``` text
streamlit
langgraph
langchain-core
langchain-openai
python-dotenv
google-search-results
```

### 5. Configure API keys

Create a `.env` file in the project root and add:

``` env
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
```

Replace the placeholder values with your own keys. Do not add quotation
marks unless your key requires them. Never publish your real keys in a
public repository.

### 6. Run the application

``` powershell
python -m streamlit run app.py
```

Streamlit will show a local URL in the terminal, usually
`http://localhost:8501`. Open that address in your browser if it does
not open automatically.

## Troubleshooting

### OpenAI authentication or quota errors

-   Confirm `OPENAI_API_KEY` is correct in `.env`.
-   Check that API billing/credits and usage limits are configured in
    your OpenAI platform account.
-   Check the selected model is available to your API account.
-   Never paste your API key into public issues, screenshots, or GitHub.

### SerpAPI errors

-   Confirm `SERPAPI_API_KEY` is correct.
-   Check your SerpAPI account's quota and usage.
-   Confirm the computer has an internet connection.

### Module not found

Activate `.venv` and run:

``` powershell
python -m pip install -r requirements.txt
```

### Port already in use

Stop the existing Streamlit process with `Ctrl+C` in its terminal, then
run the command again.

## Security

-   Keep `.env` private.
-   Add `.env` and `.venv/` to `.gitignore` before pushing the project
    to GitHub.
-   If an API key is accidentally published, revoke it and create a
    replacement.
-   Review source pages and verify important claims before using the
    generated report.

Suggested `.gitignore`:

``` gitignore
.env
.venv/
__pycache__/
*.py[cod]
```

## Future improvements

-   Add retry handling for temporary API errors and rate limits.
-   Add report download as Markdown or PDF.
-   Improve source validation and citations.
-   Add configurable search depth and report length.
-   Add tests for individual workflow nodes.
-   Track token usage and API cost.

## Learning purpose

This project demonstrates how to connect a language model to a
web-search tool and organize multiple AI tasks into a workflow. It is
intended for learning and portfolio development; review and customize
the implementation so you can explain each component confidently.
