"""Four-screen Streamlit product foundation for the research assistant."""

import streamlit as st

from frontend.utils.api_client import ask_research_backend, build_query_payload
from frontend.utils.errors import BackendRequestError
from frontend.utils.library import (
    LibraryDocument,
    load_library_documents,
    search_library_documents,
)


def clear_research_state() -> None:
    """Clear the active question, answer, citations, and errors."""
    for key in (
        "research_question",
        "research_response",
        "workspace_error",
        "workspace_state",
        "last_request",
    ):
        st.session_state.pop(key, None)


def render_landing() -> None:
    """Introduce the product and expose the two primary entry points."""
    st.header("Research smarter with your library")
    st.write(
        "Find concise, citation-backed explanations grounded in the "
        "university's academic document collection."
    )

    st.markdown("### From discovery to synthesis")
    flow_columns = st.columns(4)
    for column, number, title, description in zip(
        flow_columns,
        ("01", "02", "03", "04"),
        ("Discover", "Search", "Investigate", "Synthesize"),
        (
            "Start with a research question.",
            "Find relevant library documents.",
            "Inspect evidence and metadata.",
            "Build a grounded answer with sources.",
        ),
    ):
        with column:
            st.caption(number)
            st.markdown(f"#### {title}")
            st.write(description)

    st.markdown("### Begin your research")
    start_column, library_column = st.columns(2)
    with start_column:
        with st.container(border=True):
            st.markdown("#### Research workspace")
            st.write("Ask a question and review the answer with citations.")
            st.page_link(RESEARCH_PAGE, label="Start researching", icon=":material/search:")
    with library_column:
        with st.container(border=True):
            st.markdown("#### Library documents")
            st.write("Search the academic collection before you ask.")
            st.page_link(LIBRARY_PAGE, label="Browse documents", icon=":material/library_books:")


def render_research_workspace() -> None:
    """Render the synthesis screen and its backend response states."""
    st.subheader("Research workspace")
    st.caption("Synthesize evidence into a concise, citation-backed response.")
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
            )

    if submitted:
        if not question.strip():
            st.warning("Enter a research question before asking the library.")
            return
        st.session_state["research_question"] = question.strip()
        st.session_state["workspace_state"] = "loading"
        st.session_state.pop("workspace_error", None)
        with st.spinner("Preparing your research request..."):
            st.session_state["last_request"] = build_query_payload(
                question.strip()
            )
            try:
                response = ask_research_backend(
                    question.strip()
                )
                st.session_state["research_response"] = response
                st.session_state["workspace_state"] = (
                    "no_evidence" if not response["citations"] else "answer"
                )
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
            elif state in {"answer", "no_evidence"}:
                st.write(st.session_state["research_response"]["answer"])
                if state == "no_evidence":
                    st.warning("No supporting evidence was found in the library collection.")
            elif state == "loading":
                st.info("Preparing your grounded answer...")
            else:
                st.info("Your grounded answer will appear here after you ask a question.")

    with sources_column:
        st.markdown("### SOURCES / CITATIONS")
        with st.container(border=True):
            if st.session_state.get("workspace_state") in {"answer", "no_evidence"}:
                citations = st.session_state["research_response"]["citations"]
                if citations:
                    for index, citation in enumerate(citations, start=1):
                        title = citation.get("title") or citation.get("document_id")
                        page = citation.get("page")
                        metadata = citation.get("metadata", {})
                        with st.container(border=True):
                            st.markdown(f"**[{index}] {title}**")
                            details = [
                                metadata.get("author"),
                                (
                                    f"Page {page}"
                                    if page is not None
                                    else None
                                ),
                                metadata.get("document_type"),
                                str(metadata.get("year"))
                                if metadata.get("year")
                                else None,
                            ]
                            details = [detail for detail in details if detail]
                            if details:
                                st.caption(" · ".join(details))
                            if metadata.get("subject"):
                                st.caption(f"Subject: {metadata['subject']}")
                            if citation.get("excerpt"):
                                st.write(citation["excerpt"])
                            if metadata.get("source_url"):
                                st.link_button(
                                    "Open source",
                                    metadata["source_url"],
                                    key=f"citation-source-{index}",
                                )
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
        )

    if follow_up_submitted:
        if not follow_up.strip():
            st.warning("Enter a follow-up question before submitting.")
            return
        st.session_state["research_question"] = follow_up.strip()
        st.session_state["workspace_state"] = "loading"
        st.session_state.pop("workspace_error", None)
        with st.spinner("Preparing your follow-up..."):
            try:
                response = ask_research_backend(
                    follow_up.strip()
                )
                st.session_state["research_response"] = response
                st.session_state["workspace_state"] = (
                    "no_evidence" if not response["citations"] else "answer"
                )
            except BackendRequestError as error:
                st.session_state["workspace_error"] = str(error)
                st.session_state["workspace_state"] = "error"

    if st.button("Clear research", type="secondary"):
        clear_research_state()
        st.rerun()


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
        key="library_query",
    )
    filter_column, year_column = st.columns(2)
    document_types = sorted(
        {
            document.metadata.document_type
            for document in documents
            if document.metadata.document_type
        }
    )
    years = sorted(
        {document.metadata.year for document in documents if document.metadata.year},
        reverse=True,
    )
    with filter_column:
        selected_type = st.selectbox(
            "Document type",
            ["All types", *document_types],
            key="library_document_type",
        )
    with year_column:
        selected_year = st.selectbox(
            "Year",
            ["All years", *years],
            key="library_year",
        )
    if st.button("Reset document filters"):
        for key in ("library_query", "library_document_type", "library_year"):
            st.session_state.pop(key, None)
        st.rerun()

    results = search_library_documents(documents, query)
    if selected_type != "All types":
        results = [
            document
            for document in results
            if document.metadata.document_type == selected_type
        ]
    if selected_year != "All years":
        results = [
            document
            for document in results
            if document.metadata.year == selected_year
        ]
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
            st.session_state["selected_document"] = library_document
            st.switch_page(INVESTIGATION_PAGE)


def render_document_investigation() -> None:
    """Provide the evidence-inspection screen defined by the product flow."""
    st.subheader("Document investigation")
    st.caption("Inspect a source before using it in your research synthesis.")

    document = st.session_state.get("selected_document")
    if document is None:
        st.info("Select a document from Library documents to investigate it.")
        st.page_link(LIBRARY_PAGE, label="Browse library documents", icon=":material/library_books:")
        return

    metadata = document.metadata
    st.markdown(f"### {metadata.title or metadata.document_id}")
    details = [
        ("Document ID", metadata.document_id),
        ("Author", metadata.author),
        ("Type", metadata.document_type),
        ("Year", str(metadata.year) if metadata.year else None),
        ("Subject", metadata.subject),
    ]
    detail_columns = st.columns(2)
    for index, (label, value) in enumerate(details):
        with detail_columns[index % 2]:
            st.caption(label)
            st.write(value or "Not available")

    st.markdown("### Relevant evidence")
    if document.excerpt:
        with st.container(border=True):
            st.write(document.excerpt)
    else:
        st.info("No processed excerpt is available for this document.")

    if metadata.source_url:
        st.link_button("Open source", metadata.source_url)
    st.page_link(
        LIBRARY_PAGE,
        label="Back to library documents",
        icon=":material/arrow_back:",
    )
    st.page_link(
        RESEARCH_PAGE,
        label="Use this source in research",
        icon=":material/arrow_forward:",
    )


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="University Library Research Assistant",
        page_icon=":books:",
        layout="wide",
    )
    st.title("University Library Research Assistant")
    page = st.navigation(
        [HOME_PAGE, LIBRARY_PAGE, INVESTIGATION_PAGE, RESEARCH_PAGE]
    )
    page.run()


HOME_PAGE = st.Page(render_landing, title="Home", icon=":material/home:")
LIBRARY_PAGE = st.Page(
    render_library_documents,
    title="Library documents",
    icon=":material/library_books:",
)
INVESTIGATION_PAGE = st.Page(
    render_document_investigation,
    title="Document investigation",
    icon=":material/menu_book:",
)
RESEARCH_PAGE = st.Page(
    render_research_workspace,
    title="Research workspace",
    icon=":material/search:",
)


if __name__ == "__main__":
    main()
