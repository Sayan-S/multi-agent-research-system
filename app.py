import os
import time
import threading
import pandas as pd
import streamlit as st

for key in ("OPENAI_API_KEY", "SERPAPI_API_KEY"):
    if key not in os.environ and key in st.secrets:
        os.environ[key] = st.secrets[key]

from workflow import run_research

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Multi-Agent Research Assistant")
st.write(
    "Research a topic using three AI agents: "
    "Researcher, Analyst, and Report Writer."
)

topic = st.text_area(
    "Enter your research question",
    placeholder="Example: What is the impact of electric vehicles in India by 2030?",
    height=100,
)

if st.button("Run Research", type="primary"):
    if not topic.strip():
        st.warning("Please enter a research question.")
    else:
        # Layout placeholders for progress visualization
        status_box = st.empty()
        progress_bar = st.empty()
        chart_box = st.empty()

        # Shared control dictionary across threads
        job = {
            "done": False,
            "percent": 5,
            "stage": "🔍 Scout Agent searching web sources...",
            "data_history": [5],
            "result": None,
            "error": None,
        }

        # Background worker running the actual LangGraph pipeline
        def execute_pipeline():
            try:
                job["result"] = run_research(topic.strip())
            except Exception as e:
                job["error"] = e
            finally:
                job["done"] = True

        thread = threading.Thread(target=execute_pipeline)
        thread.start()

        # UI loop to animate progress and line graph smoothly while running
        while not job["done"]:
            # Incrementally bump percentage so user sees continuous activity
            if job["percent"] < 35:
                job["percent"] += 3
                job["stage"] = "🔍 Researcher Agent searching web & compiling evidence..."
            elif job["percent"] < 70:
                job["percent"] += 2
                job["stage"] = "📊 Analyst Agent synthesizing trends, risks & implications..."
            elif job["percent"] < 92:
                job["percent"] += 1
                job["stage"] = "✍️ Report Writer formatting executive briefing & citations..."

            # Record history for the line graph
            job["data_history"].append(job["percent"])

            # 1. Update text status
            status_box.markdown(f"**{job['stage']}** ({job['percent']}%)")

            # 2. Update progress bar
            progress_bar.progress(job["percent"] / 100)

            # 3. Update line chart showing steady progression
            chart_data = pd.DataFrame(
                {"Progress (%)": job["data_history"]}
            )
            chart_box.line_chart(chart_data, height=140)

            time.sleep(0.4)

        thread.join()

        # Handle Errors or Final Display
        if job["error"]:
            status_box.empty()
            progress_bar.empty()
            chart_box.empty()
            st.error("The workflow failed. Check your API keys, internet connection, and terminal error.")
            st.exception(job["error"])
        else:
            # Complete the bar to 100%
            job["data_history"].append(100)
            status_box.markdown("**✅ Research completed! (100%)**")
            progress_bar.progress(1.0)
            chart_box.line_chart(pd.DataFrame({"Progress (%)": job["data_history"]}), height=140)
            time.sleep(0.5)

            # Clear loading visuals to keep page clean
            status_box.empty()
            progress_bar.empty()
            chart_box.empty()

            st.success("Research completed!")

            result = job["result"]
            st.subheader("Final Research Report")
            st.markdown(result["report"])

            st.subheader("Research Findings")
            st.markdown(result["research_notes"])

            st.subheader("Analyst's Insights")
            st.markdown(result["analysis"])

            st.subheader("Sources")
            for item in result["search_results"]:
                title = item["title"]
                link = item["link"]

                if link:
                    st.markdown(f"- [{title}]({link})")
                else:
                    st.markdown(f"- {title}")