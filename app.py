
import streamlit as st
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
        try:
            with st.spinner(
                "Agents are researching, analyzing, and writing..."
            ):
                result = run_research(topic.strip())

            st.success("Research completed!")

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

        except Exception as error:
            st.error(
                "The workflow failed. Check your API keys, "
                "internet connection, and terminal error."
            )
            st.exception(error)
