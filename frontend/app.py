"""Four-screen Streamlit product foundation for the research assistant."""

import streamlit as st

from frontend.utils.api_client import ask_research_backend, build_query_payload
from frontend.utils.errors import BackendRequestError
from frontend.utils.library import (
    LibraryDocument,
    load_library_documents,
    search_library_documents,
)


def apply_theme() -> None:
    """Apply the product's calm academic visual system."""
    st.markdown(
        """
        <style>
        :root {
            --ink: #172033;
            --muted: #667085;
            --navy: #19324d;
            --blue: #2c6eaa;
            --paper: #f7f9fc;
            --line: #e3e9f1;
            --accent: #e9f2fb;
        }
        .stApp { background: var(--paper); color: var(--ink); }
        [data-testid="stHeader"] { background: rgba(247,249,252,.92); }
        [data-testid="stSidebar"] { background: #10263d; }
        [data-testid="stSidebar"] * { color: #eef5fb; }
        [data-testid="stSidebar"] button { color: #10263d; }
        h1, h2, h3, h4 { color: var(--navy); letter-spacing: -.02em; }
        h1 { font-size: 2.5rem !important; }
        [data-testid="stCaptionContainer"] { color: var(--muted); }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line);
            border-radius: 16px;
            background: rgba(255,255,255,.8);
        }
        .hero {
            padding: 2.2rem 2.4rem;
            border-radius: 22px;
            background: linear-gradient(125deg, #17324d 0%, #285d88 100%);
            color: white;
            margin: .5rem 0 2rem;
        }
        .hero h1, .hero p, .hero span { color: white !important; }
        .eyebrow {
            color: #b8d9f2 !important;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .14em;
            text-transform: uppercase;
        }
        .section-label {
            color: var(--blue);
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .13em;
            margin-top: 1.2rem;
            text-transform: uppercase;
        }
        .stat {
            background: white;
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 1rem 1.1rem;
        }
        .stat strong { color: var(--navy); font-size: 1.35rem; }
        .stButton > button, .stLinkButton > a {
            border-radius: 10px;
            font-weight: 650;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_intro(label: str, title: str, description: str) -> None:
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)
    st.header(title)
    st.caption(description)


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
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">University Library · Research Assistant</div>
          <h1>Turn library evidence into clear answers.</h1>
          <p>Discover academic sources, investigate the evidence, and build a citation-backed response in one focused workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Your research, in four steps")
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

    st.markdown("### Built for trustworthy research")
    stats = st.columns(3)
    for column, value, label in zip(
        stats,
        ("313+", "4", "100%"),
        ("indexed evidence chunks", "connected product screens", "evaluation pass rate"),
    ):
        with column:
            st.markdown(
                f'<div class="stat"><strong>{value}</strong><br><span>{label}</span></div>',
                unsafe_allow_html=True,
            )


def render_research_workspace() -> None:
    """Render the synthesis screen and its backend response states."""
    render_page_intro(
        "Synthesize",
        "Research workspace",
        "Ask a question and review the answer alongside the evidence that supports it.",
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

    st.markdown('<div class="section-label">Your question</div>', unsafe_allow_html=True)
    with st.container(border=True):
        if st.session_state.get("research_question"):
            st.write(st.session_state["research_question"])
        else:
            st.info("Your submitted research question will appear here.")

    answer_column, sources_column = st.columns(2)
    with answer_column:
        st.markdown('<div class="section-label">Grounded answer</div>', unsafe_allow_html=True)
        with st.container(border=True):
            state = st.session_state.get("workspace_state")
            if state == "error":
                st.error(st.session_state["workspace_error"])
            elif state in {"answer", "no_evidence"}:
                st.write(st.session_state["research_response"]["answer"])
                if state == "no_evidence":
                    st.warning(
                        "No supporting evidence was found in the library documents."
                    )
            elif state == "loading":
                st.info("Preparing your grounded answer...")
            else:
                st.info("Your grounded answer will appear here after you ask a question.")

    with sources_column:
        st.markdown('<div class="section-label">Sources & citations</div>', unsafe_allow_html=True)
        with st.container(border=True):
            if st.session_state.get("workspace_state") in {"answer", "no_evidence"}:
                citations = st.session_state["research_response"]["citations"]
                if citations:
                    for index, citation in enumerate(citations, start=1):
                        title = citation.get("title") or citation.get("document_id")
                        page = citation.get("page")
                        metadata = citation.get("metadata") or {}
                        with st.container(border=True):
                            st.markdown(f"**[{index}] {title}**")
                            details = [
                                citation.get("author") or metadata.get("author"),
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
                            source_url = citation.get("source_url") or metadata.get(
                                "source_url"
                            )
                            if source_url:
                                st.link_button(
                                    "Open source",
                                    source_url,
                                    key=f"citation-source-{index}",
                                )
                else:
                    st.info("No citations were returned for this question.")
            else:
                st.info("Citations will appear here with the grounded answer.")

    st.markdown('<div class="section-label">Continue exploring</div>', unsafe_allow_html=True)
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
    render_page_intro(
        "Discover",
        "Library documents",
        "Search the catalog by title, author, subject, document type, year, or document ID.",
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
    metric_columns = st.columns(2)
    metric_columns[0].metric("Matching sources", len(results))
    metric_columns[1].metric("Catalog size", len(documents))

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
            preview_page = getattr(library_document, "page", None)
            if preview_page is not None:
                st.caption(f"Preview evidence: page {preview_page}")
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
    render_page_intro(
        "Investigate",
        "Document investigation",
        "Inspect one source, its metadata, and the processed evidence before synthesizing.",
    )

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

    st.markdown("### DOCUMENT OVERVIEW")
    st.write(
        "This view focuses on one selected source and its available evidence, "
        "rather than the full document repository."
    )

    st.markdown("### SOURCE INFORMATION")
    if metadata.source_url:
        st.markdown(f"Source URL: {metadata.source_url}")
    else:
        st.caption("No source URL is available for this document.")

    st.markdown("### RELEVANT EVIDENCE")
    if document.excerpt:
        with st.container(border=True):
            evidence_page = getattr(document, "page", None)
            evidence_chunk_id = getattr(document, "chunk_id", None)
            if evidence_page is not None:
                st.caption(f"Page {evidence_page}")
            if evidence_chunk_id:
                st.caption(f"Evidence chunk: {evidence_chunk_id}")
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
    if st.button("Use this source in research", type="primary"):
        st.session_state["research_question"] = (
            f"Help me research the document: "
            f"{metadata.title or metadata.document_id}"
        )
        st.session_state["workspace_state"] = "idle"
        st.switch_page(RESEARCH_PAGE)


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="University Library Research Assistant",
        page_icon=":books:",
        layout="wide",
    )
    apply_theme()
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
