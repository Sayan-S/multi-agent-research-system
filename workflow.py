
import os
from typing import TypedDict

from dotenv import load_dotenv
from serpapi import GoogleSearch
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.2,
)

parser = StrOutputParser()


class ResearchState(TypedDict):
    topic: str
    search_results: list
    research_notes: str
    analysis: str
    report: str


def researcher_agent(state: ResearchState):
    """Agent 1: Search the web and summarize the findings."""

    params = {
        "engine": "google",
        "q": state["topic"],
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "num": 5,
    }

    response = GoogleSearch(params).get_dict()
    results = response.get("organic_results", [])

    if not results:
        error = response.get("error", "No search results found.")
        raise ValueError(f"Web search failed: {error}")

    # Keep the relevant information and source URLs.
    formatted_results = []

    for i, item in enumerate(results, start=1):
        formatted_results.append({
            "id": i,
            "title": item.get("title", "Untitled"),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", ""),
        })

    evidence = "\n".join(
        f"[{item['id']}] {item['title']}\n"
        f"URL: {item['link']}\n"
        f"Snippet: {item['snippet']}"
        for item in formatted_results
    )

    prompt = ChatPromptTemplate.from_template("""
    You are a web research agent.

    Research question: {topic}

    Search results:
    {evidence}

    Summarize the most relevant findings.
    Distinguish evidence from assumptions.
    Preserve source reference numbers such as [1] and [2].
    Do not invent facts or statistics.
    """)

    chain = prompt | llm | parser

    notes = chain.invoke({
        "topic": state["topic"],
        "evidence": evidence,
    })

    return {
        "search_results": formatted_results,
        "research_notes": notes,
    }


def analyst_agent(state: ResearchState):
    """Agent 2: Analyze the collected research."""

    prompt = ChatPromptTemplate.from_template("""
    You are a research analyst.

    Original question:
    {topic}

    Research findings:
    {research_notes}

    Analyze the findings. Identify:
    1. Important insights and trends.
    2. Benefits and risks.
    3. Contradictions or missing evidence.
    4. Practical implications.

    Preserve source reference numbers.
    Do not invent facts or numerical data.
    Clearly mention uncertainty where necessary.
    """)

    chain = prompt | llm | parser

    analysis = chain.invoke({
        "topic": state["topic"],
        "research_notes": state["research_notes"],
    })

    return {"analysis": analysis}


def writer_agent(state: ResearchState):
    """Agent 3: Generate the final report."""

    sources = "\n".join(
        f"[{item['id']}] {item['title']} — {item['link']}"
        for item in state["search_results"]
    )

    prompt = ChatPromptTemplate.from_template("""
    You are a professional research report writer.

    Research question:
    {topic}

    Research findings:
    {research_notes}

    Analyst's conclusions:
    {analysis}

    Available sources:
    {sources}

    Write a clear report with these sections:
    1. Executive Summary
    2. Key Findings
    3. Analysis
    4. Risks and Limitations
    5. Conclusion

    Cite supporting sources using [1], [2], etc.
    Only use reference numbers from the provided sources.
    Do not invent facts, statistics, or citations.
    Keep the report concise and useful.
    """)

    chain = prompt | llm | parser

    report = chain.invoke({
        "topic": state["topic"],
        "research_notes": state["research_notes"],
        "analysis": state["analysis"],
        "sources": sources,
    })

    return {"report": report}


# Build the LangGraph workflow.
graph_builder = StateGraph(ResearchState)

graph_builder.add_node("researcher", researcher_agent)
graph_builder.add_node("analyst", analyst_agent)
graph_builder.add_node("writer", writer_agent)

graph_builder.add_edge(START, "researcher")
graph_builder.add_edge("researcher", "analyst")
graph_builder.add_edge("analyst", "writer")
graph_builder.add_edge("writer", END)

research_graph = graph_builder.compile()


def run_research(topic: str):
    """Run the complete multi-agent workflow."""

    return research_graph.invoke({
        "topic": topic,
        "search_results": [],
        "research_notes": "",
        "analysis": "",
        "report": "",
    })
