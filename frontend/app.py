"""Streamlit shell for the University Library Research Assistant."""

import streamlit as st


def render_research_workspace() -> None:
    """Render the initial research workspace without calling an API."""
    st.subheader("Research workspace")
    st.caption(
        "Ask a question about the university library collection. "
        "Answer generation will be connected in a later milestone."
    )

    with st.container(border=True):
        question = st.text_area(
            "Research question",
            placeholder="For example: What are the main findings of this thesis?",
            height=120,
        )
        st.button("Search library", type="primary", disabled=not question.strip())

    st.subheader("Answer")
    st.info("A citation-backed answer will appear here once retrieval is connected.")

    st.subheader("Sources and citations")
    st.info("Retrieved documents and page-level citations will appear here.")


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
