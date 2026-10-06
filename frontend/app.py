"""Four-screen Streamlit product foundation for the research assistant."""

import streamlit as st

from frontend.utils.api_client import ask_research_backend, build_query_payload
from frontend.utils.errors import BackendRequestError
from frontend.utils.library import (
    LibraryDocument,
    load_library_documents,
    search_library_documents,
)


def inject_figma_theme() -> None:
    """Apply the visual language from the exported Library Assistant screens."""
    st.html(
        """
        <style>
        :root {
            --ink: #18264a;
            --muted: #65708c;
            --navy: #193b91;
            --navy-dark: #122c72;
            --lavender: #f6f7ff;
            --panel: #ffffff;
            --line: #dfe4f2;
            --teal: #00a9a2;
            --teal-soft: #d9f7f3;
            --gold: #f0ba50;
        }
        [data-testid="stAppViewContainer"] {
            background: var(--lavender);
            color: var(--ink);
        }
        [data-testid="stHeader"] {
            background: rgba(246, 247, 255, 0.96);
        }
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e4e8f3;
            min-width: 13rem;
            width: 13rem;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 0.55rem 0.45rem 0.8rem;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: var(--muted);
            font-size: 0.68rem;
            line-height: 1.35;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
            color: var(--navy);
            font-size: 0.82rem;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            padding-top: 0.2rem;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {
            color: var(--muted);
            content: "CORPUS & EXPLORATION";
            display: block;
            font-size: 0.57rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            margin: 0.65rem 0.55rem 0.35rem;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
            border-radius: 3px;
            color: #38425c;
            font-size: 0.72rem;
            margin: 0.1rem 0;
            padding: 0.42rem 0.55rem;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
            background: #eef2ff;
            color: var(--navy);
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: var(--navy);
            color: white;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] span {
            color: white;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a svg {
            height: 0.85rem;
            width: 0.85rem;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] > ul {
            gap: 0;
        }
        h1, h2, h3, h4 {
            color: var(--ink);
            letter-spacing: -0.02em;
        }
        h1 { font-size: clamp(2.1rem, 4vw, 3.7rem); line-height: 1.02; }
        h2 { font-size: 1.55rem; }
        h3 { font-size: 1.05rem; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line);
            border-radius: 10px;
            background: var(--panel);
            box-shadow: 0 8px 26px rgba(25, 59, 145, 0.07);
            transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #b9c9ee;
            box-shadow: 0 12px 30px rgba(25, 59, 145, 0.12);
            transform: translateY(-2px);
        }
        [class*="st-key-home-search"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(135deg, #ffffff 0%, #f4fbff 100%);
            border: 1px solid #c9e9ee;
            box-shadow: 0 14px 34px rgba(0, 169, 162, 0.12);
        }
        [class*="st-key-home-start"] [data-testid="stVerticalBlockBorderWrapper"],
        [class*="st-key-home-library"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(145deg, #ffffff 0%, #f7f9ff 100%);
            border-top: 3px solid var(--navy);
        }
        [class*="st-key-home-capability"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(145deg, #ffffff 0%, #f6fbff 100%);
            border-top: 3px solid var(--teal);
        }
        [class*="st-key-home-capability"] h4 {
            color: var(--navy);
        }
        [class*="st-key-home-flow"] {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid #e0e6f5;
            border-radius: 9px;
            min-height: 9rem;
            padding: 0.7rem;
        }
        [class*="st-key-home-flow"] [data-testid="stMarkdownContainer"] h4 {
            color: var(--navy);
            margin-top: 0.2rem;
        }
        [class*="st-key-home-flow"] [data-testid="stCaptionContainer"] {
            color: var(--teal);
            font-weight: 800;
        }
        [data-testid="stButton"] button,
        [data-testid="stPageLink"] a,
        [data-testid="stLinkButton"] a,
        [data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseButton-secondaryFormSubmit"],
        [data-testid="stBaseButton-primaryFormSubmit"] {
            border-radius: 5px;
            font-weight: 600;
        }
        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-primaryFormSubmit"] {
            background: var(--navy);
            border-color: var(--navy);
            color: #ffffff !important;
        }
        [data-testid="stButton"] button[kind="primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover,
        [data-testid="stBaseButton-primaryFormSubmit"]:hover {
            background: var(--navy-dark);
            border-color: var(--navy-dark);
        }
        [data-testid="stBaseButton-primary"] *,
        [data-testid="stBaseButton-primaryFormSubmit"] *,
        [data-testid="stBaseButton-secondary"] *,
        [data-testid="stBaseButton-secondaryFormSubmit"] * {
            color: inherit !important;
        }
        [data-testid="stButton"] button[kind="secondary"],
        [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseButton-secondaryFormSubmit"] {
            background: #ffffff;
            border: 1px solid #9eadd0;
            color: var(--navy) !important;
        }
        [data-testid="stButton"] button[kind="secondary"]:hover,
        [data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stBaseButton-secondaryFormSubmit"]:hover {
            background: #eef2ff;
            border-color: var(--navy);
            color: var(--navy-dark) !important;
        }
        [data-testid="stPageLink"] a,
        [data-testid="stLinkButton"] a {
            background: #ffffff;
            border: 1px solid #9eadd0;
            color: var(--navy) !important;
        }
        [data-testid="stPageLink"] a:hover,
        [data-testid="stLinkButton"] a:hover {
            background: #eef2ff;
            border-color: var(--navy);
            color: var(--navy-dark) !important;
        }
        [data-testid="stPageLink"] a *,
        [data-testid="stLinkButton"] a * {
            color: inherit !important;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-color: var(--line);
            border-radius: 5px;
            background: #ffffff;
            color: #18264a !important;
            caret-color: #18264a;
        }
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: #65708c !important;
            opacity: 1;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] *,
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea {
            color: #18264a !important;
        }
        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
            border-color: var(--navy);
            box-shadow: 0 0 0 1px var(--navy);
        }
        [data-testid="stMetric"] {
            background: white;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.8rem;
        }
        .fig-topbar,
        [class*="st-key-fig-topbar"] {
            align-items: center;
            background: white;
            border: 1px solid var(--line);
            border-radius: 4px;
            color: var(--ink);
            display: flex;
            font-size: 0.65rem;
            gap: 0.8rem;
            justify-content: space-between;
            margin: -0.4rem 0 0.8rem;
            min-height: 2rem;
            padding: 0.25rem 0.55rem;
        }
        [class*="st-key-fig-topbar"] [data-testid="stForm"] {
            border: 0;
            padding: 0;
        }
        [class*="st-key-fig-topbar"] [data-testid="stTextInput"] {
            margin: -0.4rem 0;
        }
        [class*="st-key-fig-topbar"] [data-testid="stTextInput"] input {
            font-size: 0.68rem;
            min-height: 1.8rem;
        }
        [class*="st-key-fig-topbar"] [data-testid="stFormSubmitButton"] button {
            font-size: 0.62rem;
            min-height: 1.8rem;
            padding: 0 0.45rem;
        }
        [class*="st-key-fig-topbar"] [data-testid="stBaseButton-secondaryFormSubmit"] {
            background: var(--navy);
            border-color: var(--navy);
            color: #ffffff !important;
        }
        .fig-brand { color: var(--navy); font-size: 0.69rem; font-weight: 800; }
        .fig-brand small { color: var(--muted); display: block; font-size: 0.45rem; letter-spacing: 0.06em; }
        .fig-chip {
            background: var(--teal-soft);
            border-radius: 999px;
            color: #007d78;
            font-size: 0.55rem;
            font-weight: 700;
            padding: 0.22rem 0.55rem;
        }
        .fig-eyebrow {
            color: #007d78;
            font-size: 0.66rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }
        .fig-hero {
            background: linear-gradient(135deg, #f1f7ff 0%, #fff 54%, #eefbfd 100%);
            border: 1px solid #d9e5f6;
            border-radius: 12px;
            padding: 3rem 2rem 2.5rem;
            text-align: center;
        }
        .fig-hero p { color: var(--muted); margin: 0 auto 1.2rem; max-width: 720px; }
        .fig-label {
            color: var(--muted);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .fig-evidence {
            border-left: 3px solid var(--teal);
            background: #f3fbfb;
            padding: 0.8rem 1rem;
        }
        .fig-muted { color: var(--muted); font-size: 0.8rem; }
        .fig-sidebar-brand {
            border-bottom: 1px solid var(--line);
            color: var(--navy);
            font-size: 0.78rem;
            font-weight: 800;
            line-height: 1.15;
            padding: 0.3rem 0.45rem 0.8rem;
        }
        .fig-sidebar-brand small {
            color: var(--muted);
            display: block;
            font-size: 0.46rem;
            letter-spacing: 0.07em;
            margin-top: 0.25rem;
        }
        </style>
        """
    )


def render_topbar() -> None:
    """Render the compact utility bar used by the reference screens."""
    with st.container(key="fig-topbar"):
        brand_column, corpus_column, workspace_column, term_column, search_column, status_column = st.columns(
            [1.35, 0.55, 0.8, 1.35, 2.1, 0.75],
            vertical_alignment="center",
        )
        with brand_column:
            st.markdown(
                '<div class="fig-brand">Library Assistant<small>UNIVERSITY KNOWLEDGE CORE</small></div>',
                unsafe_allow_html=True,
            )
        with corpus_column:
            st.caption("Corpus")
        with workspace_column:
            st.caption("Workspace in use")
        with term_column:
            st.markdown(
                '<span class="fig-chip">Term: Spring 2025 · 142k cataloged papers</span>',
                unsafe_allow_html=True,
            )
        with search_column:
            with st.form("catalog_search_form", border=False):
                catalog_query = st.text_input(
                    "Catalog search",
                    placeholder="Search catalog, DOI, or citations...",
                    label_visibility="collapsed",
                )
                catalog_submitted = st.form_submit_button("Search")
            if catalog_submitted:
                st.session_state["library_query"] = catalog_query.strip()
                st.switch_page(LIBRARY_PAGE)
        with status_column:
            st.markdown(
                '<span class="fig-chip">Index Online</span>',
                unsafe_allow_html=True,
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


def render_citation(citation: dict, index: int, key_prefix: str = "citation") -> None:
    """Render one citation while omitting unavailable optional fields."""
    title = citation.get("title") or citation.get("document_id") or "Library source"
    page = citation.get("page")
    metadata = citation.get("metadata") or {}
    with st.container(border=True, key="home-search"):
        st.markdown(f"**[{index}] {title}**")
        details = [
            citation.get("author") or metadata.get("author"),
            f"Page {page}" if page is not None else None,
            metadata.get("document_type"),
            str(metadata.get("year")) if metadata.get("year") else None,
        ]
        details = [detail for detail in details if detail]
        if details:
            st.caption(" · ".join(details))
        if metadata.get("subject"):
            st.caption(f"Subject: {metadata['subject']}")
        if citation.get("excerpt"):
            st.write(citation["excerpt"])
        if citation.get("chunk_id"):
            score = citation.get("score")
            score_text = (
                f" · Similarity {score:.2f}"
                if isinstance(score, (int, float))
                else ""
            )
            st.caption(f"Evidence chunk: {citation['chunk_id']}{score_text}")
        source_url = citation.get("source_url") or metadata.get("source_url")
        if source_url:
            st.link_button("Open source", source_url, key=f"{key_prefix}-source-{index}")


def render_landing() -> None:
    """Introduce the product and expose the two primary entry points."""
    st.html(
        """
        <section class="fig-hero">
          <div class="fig-eyebrow">Grounding in indexed university research documents · powered by RAG</div>
          <h1>Research smarter.<br>Find the evidence.</h1>
          <p>Ask questions across university research papers, doctoral theses, and verified course materials. Get concise, citation-backed explanations grounded directly in peer-reviewed scholarship.</p>
        </section>
        """
    )

    st.markdown("### Start with a research question")
    with st.container(border=True):
        with st.form("landing_search_form"):
            landing_question = st.text_input(
                "Research question",
                placeholder="Ask an academic question or enter a research topic",
                label_visibility="collapsed",
            )
            start = st.form_submit_button("Start researching", type="primary")
        if start:
            if landing_question.strip():
                st.session_state["research_question"] = landing_question.strip()
                st.switch_page(RESEARCH_PAGE)
            else:
                st.warning("Enter a research question before starting.")

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
            with st.container(key=f"home-flow-{number}"):
                st.caption(number)
                st.markdown(f"#### {title}")
                st.write(description)

    st.markdown("### Begin your research")
    start_column, library_column = st.columns(2)
    with start_column:
        with st.container(border=True, key="home-start"):
            st.markdown("#### Research workspace")
            st.write("Ask a question and review the answer with citations.")
            st.page_link(RESEARCH_PAGE, label="Start researching", icon=":material/search:")
    with library_column:
        with st.container(border=True, key="home-library"):
            st.markdown("#### Library documents")
            st.write("Search the academic collection before you ask.")
            st.page_link(LIBRARY_PAGE, label="Browse documents", icon=":material/library_books:")

    st.markdown("### What you can do here")
    capability_columns = st.columns(3)
    capabilities = (
        (
            "Discover sources",
            "Search the real academic catalog by title, author, subject, type, year, or document ID.",
        ),
        (
            "Inspect evidence",
            "Open one source to review its metadata, excerpt, page, chunk ID, and source link.",
        ),
        (
            "Ask with confidence",
            "Receive semantically retrieved evidence with traceable citations and an explicit no-evidence state.",
        ),
    )
    for column, (title, description) in zip(capability_columns, capabilities):
        with column:
            with st.container(border=True, key=f"home-capability-{title.lower().replace(' ', '-')}"):
                st.markdown(f"#### {title}")
                st.write(description)

    st.markdown("### How the answer is grounded")
    st.info(
        "Your question is sent to the backend, matched against the indexed library "
        "evidence using local embeddings and ChromaDB, and returned with the source "
        "document, page, excerpt, and similarity score."
    )


def render_research_workspace() -> None:
    """Render the synthesis screen and its backend response states."""
    st.markdown('<div class="fig-eyebrow">Active query expression</div>', unsafe_allow_html=True)
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
                "Run research",
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

    st.markdown("### ACTIVE QUERY")
    with st.container(border=True):
        if st.session_state.get("research_question"):
            st.write(st.session_state["research_question"])
        else:
            st.info("Your submitted research question will appear here.")

    answer_column, sources_column = st.columns(2)
    with answer_column:
        st.markdown("### SYNTHESIS & LITERATURE FINDINGS")
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
        st.markdown("### SOURCES USED")
        with st.container(border=True):
            if st.session_state.get("workspace_state") in {"answer", "no_evidence"}:
                citations = st.session_state["research_response"]["citations"]
                if citations:
                    for index, citation in enumerate(citations, start=1):
                        render_citation(citation, index)
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
    st.markdown('<div class="fig-eyebrow">Corpus index v7.8 · synchronized library catalog</div>', unsafe_allow_html=True)
    st.subheader("Search library document repository")
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
            st.session_state.pop("investigation_response", None)
            st.session_state.pop("investigation_question", None)
            st.session_state.pop("investigation_error", None)
            st.switch_page(INVESTIGATION_PAGE)


def render_document_investigation() -> None:
    """Provide the evidence-inspection screen defined by the product flow."""
    st.markdown('<div class="fig-eyebrow">Document viewer · evidence inspection</div>', unsafe_allow_html=True)
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

    st.markdown("### ASK ABOUT THIS DOCUMENT")
    st.caption(
        "Questions asked here are restricted to this selected document. "
        "Answers are returned with evidence from this source only."
    )
    with st.form(f"document_question_form_{metadata.document_id}"):
        document_question = st.text_area(
            "Your question",
            placeholder="What is the main contribution of this paper?",
            height=100,
        )
        ask_document = st.form_submit_button("Ask about this document", type="primary")

    if ask_document:
        if not document_question.strip():
            st.warning("Enter a question about this document.")
        else:
            with st.spinner("Searching this document's evidence..."):
                try:
                    response = ask_research_backend(
                        document_question.strip(),
                        {"document_id": metadata.document_id},
                    )
                    st.session_state["investigation_response"] = response
                    st.session_state["investigation_question"] = document_question.strip()
                except BackendRequestError as error:
                    st.session_state["investigation_error"] = str(error)

    if st.session_state.get("investigation_question"):
        st.markdown("### DOCUMENT ANSWER")
        st.caption(st.session_state["investigation_question"])
        if st.session_state.get("investigation_error"):
            st.error(st.session_state["investigation_error"])
        else:
            investigation_response = st.session_state.get(
                "investigation_response", {}
            )
            st.write(investigation_response.get("answer", "No answer returned."))
            citations = investigation_response.get("citations", [])
            if citations:
                st.markdown("#### Supporting evidence")
                for index, citation in enumerate(citations, start=1):
                    render_citation(citation, index, "investigation")
            else:
                st.warning(
                    "No supporting evidence was found in this document for that question."
                )

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
        initial_sidebar_state="expanded",
    )
    inject_figma_theme()
    st.sidebar.markdown(
        """
        <div class="fig-sidebar-brand">
          Library Assistant
          <small>UNIVERSITY KNOWLEDGE CORE</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_topbar()
    # Keep the original flat navigation so every existing page link and
    # selection flow remains compatible with the earlier working app.
    page = st.navigation([HOME_PAGE, LIBRARY_PAGE, INVESTIGATION_PAGE, RESEARCH_PAGE])
    page.run()


HOME_PAGE = st.Page(
    render_landing,
    title="Home",
    icon=":material/home:",
)
LIBRARY_PAGE = st.Page(
    render_library_documents,
    title="Library documents",
    icon=":material/search:",
)
INVESTIGATION_PAGE = st.Page(
    render_document_investigation,
    title="Document investigation",
    icon=":material/menu_book:",
)
RESEARCH_PAGE = st.Page(
    render_research_workspace,
    title="Research workspace",
    icon=":material/workspace_premium:",
)


if __name__ == "__main__":
    main()
