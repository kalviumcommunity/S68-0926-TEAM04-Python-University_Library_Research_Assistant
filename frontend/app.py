"""Streamlit shell for the University Library Research Assistant."""

import streamlit as st


def render_research_workspace() -> None:
    """Render the research workspace without calling an API."""
    st.subheader("Research workspace")
    st.caption(
        "Ask a question about the university library collection. "
        "The research assistant will return a grounded answer with sources."
    )

    with st.container(border=True):
        with st.form("research_question_form"):
            question = st.text_area(
                "Research question",
                placeholder="For example: What are the main findings of this thesis?",
                height=120,
            )
            submitted = st.form_submit_button(
                "Ask the library",
                type="primary",
                disabled=not question.strip(),
            )

    if submitted:
        st.session_state["research_question"] = question.strip()

    if "research_question" not in st.session_state:
        st.info("Start by entering a research question above.")
    else:
        st.subheader("Answer")
        st.warning(
            "The backend and retrieval pipeline are not connected yet. "
            "This is a temporary UI state, not an AI-generated answer."
        )

        st.subheader("Sources and citations")
        st.info("Page-level citations will appear here when retrieval is connected.")

    st.subheader("Follow-up questions")
    st.text_input(
        "Ask a follow-up",
        placeholder="Follow-up questions will use the current research context.",
        disabled="research_question" not in st.session_state,
    )


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="University Library Research Assistant",
        page_icon=":books:",
        layout="wide",
    )
    st.title("University Library Research Assistant")
    st.write(
        "Find concise, citation-backed explanations grounded in university "
        "library documents."
    )

    page = st.navigation(
        [
            st.Page(render_research_workspace, title="Research workspace", icon=":material/search:"),
            st.Page(
                lambda: st.info("Document browsing will be added in a future milestone."),
                title="Library documents",
                icon=":material/library_books:",
            ),
        ]
    )
    page.run()


if __name__ == "__main__":
    main()
