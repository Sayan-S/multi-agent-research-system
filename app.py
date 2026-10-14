import os
import threading
import time
import streamlit as st

for key in ("OPENAI_API_KEY", "SERPAPI_API_KEY"):
    if key not in os.environ and key in st.secrets:
        os.environ[key] = st.secrets[key]

from document_generators import (
    generate_pdf_report,
    generate_pptx_deck,
    generate_word_document,
)
from workflow import run_research

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Multi-Agent Research Assistant")
st.write(
    "Research a topic using three AI agents: "
    "**Researcher**, **Analyst**, and **Report Writer**."
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

        # Smooth percentage ticks
        while not job["done"]:
            if job["percent"] < 35:
                job["percent"] += 3
                job["stage"] = "🔍 Researcher Agent searching web & compiling evidence..."
            elif job["percent"] < 70:
                job["percent"] += 2
                job["stage"] = "📊 Analyst Agent synthesizing trends, risks & implications..."
            elif job["percent"] < 92:
                job["percent"] += 1
                job["stage"] = "✍️ Report Writer formatting briefing & citations..."

            status_box.markdown(f"**{job['stage']}** ({job['percent']}%)")
            progress_bar.progress(job["percent"] / 100)
            time.sleep(0.4)

        thread.join()

        if job["error"]:
            status_box.empty()
            progress_bar.empty()
            st.error("The workflow failed. Check your API keys, internet connection, and terminal error.")
            st.exception(job["error"])
        else:
            status_box.markdown("**⚙️ Compiling Word, PowerPoint, and PDF files... (98%)**")
            progress_bar.progress(0.98)

            result = job["result"]

            # Generate downloadable files in memory
            word_bytes = generate_word_document(
                topic=topic.strip(),
                report=result["report"],
                research_notes=result["research_notes"],
                analysis=result["analysis"],
                sources=result["search_results"],
            )
            pptx_bytes = generate_pptx_deck(
                topic=topic.strip(),
                report=result["report"],
                analysis=result["analysis"],
                sources=result["search_results"],
            )
            pdf_bytes = generate_pdf_report(
                topic=topic.strip(),
                report=result["report"],
                analysis=result["analysis"],
            )

            progress_bar.progress(1.0)
            time.sleep(0.3)
            status_box.empty()
            progress_bar.empty()

            st.success("Research and Presentation Files Ready!")

            # -------------------------------------------------------------
            # DOWNLOAD SECTION AT THE TOP
            # -------------------------------------------------------------
            st.markdown("### 📥 Download Presentation & Analysis Files")
            col_word, col_pptx, col_pdf = st.columns(3)

            with col_word:
                st.download_button(
                    label="📄 Download Word File (.docx)",
                    data=word_bytes,
                    file_name="Research_Analysis_Complete.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
                st.caption("Includes all site data: Report, Analyst Insights, Notes & Sources.")

            with col_pptx:
                st.download_button(
                    label="📊 Download PowerPoint (.pptx)",
                    data=pptx_bytes,
                    file_name="Presentation_Slides.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True,
                )
                st.caption("Slide deck ready for presentation.")

            with col_pdf:
                st.download_button(
                    label="📑 Download Presentation PDF (.pdf)",
                    data=pdf_bytes,
                    file_name="Executive_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.caption("Executive briefing PDF.")

            st.divider()

            # -------------------------------------------------------------
            # CONTENT VIEW AT THE BOTTOM
            # -------------------------------------------------------------
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