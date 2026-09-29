"""Streamlit shell for the University Library Research Assistant."""

import streamlit as st

from frontend.utils.api_client import ask_research_backend, build_query_payload
from frontend.utils.errors import BackendRequestError
from frontend.utils.library import (
    LibraryDocument,
    load_library_documents,
    search_library_documents,
)


def render_research_workspace() -> None:
    """Render the research workspace and its backend response states."""
    st.subheader("Research workspace")
    st.caption(
        "Ask a question about the university library collection. "
        "The research assistant will return a grounded answer with sources."
    )

    with st.container(border=True):
        st.markdown("#### Ask a research question")
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
        st.session_state["workspace_state"] = "loading"
        st.session_state.pop("workspace_error", None)
        with st.spinner("Preparing your research request..."):
            st.session_state["last_request"] = build_query_payload(
                question.strip()
            )
            try:
                st.session_state["research_response"] = ask_research_backend(
                    question.strip()
                )
                st.session_state["workspace_state"] = "answer"
            except BackendRequestError as error:
                st.session_state["workspace_error"] = str(error)
                st.session_state["workspace_state"] = "error"

    st.markdown("### QUESTION")
    with st.container(border=True):
        if st.session_state.get("research_question"):
            st.write(st.session_state["research_question"])
        else:
            st.info("Your submitted research question will appear here.")

    answer_column, sources_column = st.columns(2)
    with answer_column:
        st.markdown("### ANSWER")
        with st.container(border=True):
            state = st.session_state.get("workspace_state")
            if state == "error":
                st.error(st.session_state["workspace_error"])
            elif state == "answer":
                st.write(st.session_state["research_response"]["answer"])
            elif state == "loading":
                st.info("Preparing your grounded answer...")
            else:
                st.info("Your grounded answer will appear here after you ask a question.")

    with sources_column:
        st.markdown("### SOURCES / CITATIONS")
        with st.container(border=True):
            if st.session_state.get("workspace_state") == "answer":
                citations = st.session_state["research_response"]["citations"]
                if citations:
                    for citation in citations:
                        title = citation.get("title") or citation.get("document_id")
                        page = citation.get("page")
                        page_label = f" — page {page}" if page else ""
                        st.markdown(f"- **{title}**{page_label}")
                else:
                    st.info("No citations were returned for this question.")
            else:
                st.info("Citations will appear here with the grounded answer.")

    st.markdown("### FOLLOW-UP")
    with st.form("follow_up_form"):
        follow_up = st.text_input(
            "Follow-up question",
            placeholder="Ask a follow-up using the same research context.",
        )
        follow_up_submitted = st.form_submit_button(
            "Ask follow-up",
            type="secondary",
            disabled=not follow_up.strip(),
        )

    if follow_up_submitted:
        st.session_state["research_question"] = follow_up.strip()
        st.session_state["workspace_state"] = "loading"
        st.session_state.pop("workspace_error", None)
        with st.spinner("Preparing your follow-up..."):
            try:
                st.session_state["research_response"] = ask_research_backend(
                    follow_up.strip()
                )
                st.session_state["workspace_state"] = "answer"
            except BackendRequestError as error:
                st.session_state["workspace_error"] = str(error)
                st.session_state["workspace_state"] = "error"


@st.cache_data
def get_library_documents() -> list[LibraryDocument]:
    """Cache the local catalog while allowing a manual refresh."""
    return load_library_documents()


def render_library_documents() -> None:
    """Render document discovery from the real processed catalog."""
    st.subheader("Library documents")
    st.caption(
        "Search the academic documents currently available in the processed "
        "library catalog."
    )

    documents = get_library_documents()
    if not documents:
        st.warning("The document repository is empty.")
        return

    query = st.text_input(
        "Search documents",
        placeholder="Search by title, author, subject, or document ID",
    )
    results = search_library_documents(documents, query)
    st.caption(f"{len(results)} of {len(documents)} documents")

    if not results:
        st.info("No documents match your search.")
        return

    for library_document in results:
        render_document_card(library_document)


def render_document_card(library_document: LibraryDocument) -> None:
    """Render one document using only fields present in the catalog."""
    metadata = library_document.metadata
    with st.container(border=True):
        st.markdown(f"#### {metadata.title or metadata.document_id}")
        details = [
            value
            for value in (
                metadata.author,
                metadata.document_type,
                str(metadata.year) if metadata.year else None,
                metadata.subject,
            )
            if value
        ]
        if details:
            st.caption(" · ".join(details))
        if library_document.excerpt:
            st.write(library_document.excerpt[:500].rstrip() + "...")
        else:
            st.caption("No processed text excerpt is available.")

        if metadata.source_url:
            st.link_button("Open source", metadata.source_url)
        if st.button(
            "Use in research",
            key=f"use-{metadata.document_id}",
        ):
            st.session_state["research_question"] = (
                f"Help me research the document: {metadata.title or metadata.document_id}"
            )
            st.session_state["workspace_state"] = "idle"
            st.info("Document selected. Continue in the Research workspace.")


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
                render_library_documents,
                title="Library documents",
                icon=":material/library_books:",
            ),
        ]
    )
    page.run()


if __name__ == "__main__":
    main()
