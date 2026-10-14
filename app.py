import os
import threading
import time
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
        # Layout placeholders for clean progress status
        status_box = st.empty()
        progress_bar = st.empty()

        job = {
            "done": False,
            "percent": 5,
            "stage": "🔍 Scout Agent searching web sources...",
            "result": None,
            "error": None,
        }

        def execute_pipeline():
            try:
                job["result"] = run_research(topic.strip())
            except Exception as e:
                job["error"] = e
            finally:
                job["done"] = True

        thread = threading.Thread(target=execute_pipeline)
        thread.start()

        # UI loop to smoothly tick percentage while the agents run
        while not job["done"]:
            if job["percent"] < 35:
                job["percent"] += 3
                job["stage"] = "🔍 Researcher Agent searching web & compiling evidence..."
            elif job["percent"] < 70:
                job["percent"] += 2
                job["stage"] = "📊 Analyst Agent synthesizing trends, risks & implications..."
            elif job["percent"] < 92:
                job["percent"] += 1
                job["stage"] = "✍️ Report Writer formatting executive briefing & citations..."

            # Update status text and progress bar
            status_box.markdown(f"**{job['stage']}** ({job['percent']}%)")
            progress_bar.progress(job["percent"] / 100)

            time.sleep(0.4)

        thread.join()

        # Clean up or show results
        if job["error"]:
            status_box.empty()
            progress_bar.empty()
            st.error("The workflow failed. Check your API keys, internet connection, and terminal error.")
            st.exception(job["error"])
        else:
            status_box.markdown("**✅ Research completed! (100%)**")
            progress_bar.progress(1.0)
            time.sleep(0.5)

            # Clear progress UI for the final report
            status_box.empty()
            progress_bar.empty()

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