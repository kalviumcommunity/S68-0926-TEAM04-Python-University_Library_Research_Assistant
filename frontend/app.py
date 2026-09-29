"""Streamlit shell for the University Library Research Assistant."""

import streamlit as st

from frontend.utils.api_client import (
    BackendNotConfiguredError,
    ask_research_backend,
    build_query_payload,
)
from frontend.utils.library import (
    LibraryDocument,
    load_library_documents,
    search_library_documents,
)


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
        with st.spinner("Preparing your research request..."):
            st.session_state["last_request"] = build_query_payload(
                question.strip()
            )
            try:
                st.session_state["research_response"] = ask_research_backend(
                    question.strip()
                )
                st.session_state["workspace_state"] = "answer"
            except BackendNotConfiguredError as error:
                st.session_state["workspace_error"] = str(error)
                st.session_state["workspace_state"] = "error"

    if "research_question" not in st.session_state:
        st.markdown("### QUESTION")
        st.info("Ask a research question to see the answer and sources here.")
    else:
        st.markdown("### QUESTION")
        st.write(st.session_state["research_question"])
        st.markdown("### ANSWER")
        if st.session_state.get("workspace_state") == "error":
            st.error(st.session_state["workspace_error"])
        elif st.session_state.get("workspace_state") == "answer":
            response = st.session_state["research_response"]
            st.write(response["answer"])
        else:
            st.info("Your answer will appear here.")

        st.markdown("### SOURCES / CITATIONS")
        if st.session_state.get("workspace_state") == "answer":
            st.write(st.session_state["research_response"]["citations"])
        else:
            st.info("Citations will appear here when the backend is connected.")

    st.subheader("Follow-up questions")
    st.text_input(
        "Ask a follow-up",
        placeholder="Follow-up questions will use the current research context.",
        disabled="research_question" not in st.session_state,
    )


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
            st.session_state["selected_document_id"] = metadata.document_id
            st.session_state["research_question"] = (
                f"Help me research the document: {metadata.title or metadata.document_id}"
            )
            st.session_state["workspace_state"] = "idle"
            st.info("Document selected. Continue in the Research workspace.")


def render_document_viewer() -> None:
    """Render a stable-ID document selection placeholder."""
    st.subheader("Document investigation")
    document_id = st.session_state.get("selected_document_id")
    if not document_id:
        st.info("Select a document from Library documents to investigate it.")
        return

    documents = get_library_documents()
    selected = next(
        (document for document in documents if document.metadata.document_id == document_id),
        None,
    )
    if selected is None:
        st.error("The selected document is no longer available in the catalog.")
        return

    st.markdown(f"### {selected.metadata.title or document_id}")
    st.caption(f"Document ID: {document_id}")
    if selected.excerpt:
        st.write(selected.excerpt)
    else:
        st.info("No processed text is available for this document.")


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
            st.Page(
                render_document_viewer,
                title="Document investigation",
                icon=":material/menu_book:",
            ),
        ]
    )
    page.run()


if __name__ == "__main__":
    main()
