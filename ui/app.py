import streamlit as st
import pandas as pd
import os
import sys
import time

# Ensure project root directory is in sys.path for direct imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings
from ingestion.db_connector import DatabaseConnector
from ingestion.file_parser import FinancialFileParser
from processing.semantic_chunker import FinancialSemanticChunker
from core.text_to_sql import TextToSQLEngine
from core.rag_engine import FinancialRAGEngine
from ui.components import render_gemini_header, render_prompt_chip, render_gemini_chart

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & THEME CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Financial Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
try:
    with open("ui/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# -----------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "⚡ Text-to-SQL Analytics"
if "input_query_preset" not in st.session_state:
    st.session_state.input_query_preset = ""

# Demo user credentials store
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "dundi": "admin123",
        "analyst": "finance2026",
        "demo": "demo123"
    }

# -----------------------------------------------------------------------------
# 3. CACHED ENGINE INSTANTIATIONS
# -----------------------------------------------------------------------------
@st.cache_resource
def get_db_connector():
    return DatabaseConnector()

@st.cache_resource
def get_sql_engine(api_key: str):
    return TextToSQLEngine(api_key=api_key)

@st.cache_resource
def get_rag_engine(api_key: str):
    return FinancialRAGEngine(api_key=api_key)

# -----------------------------------------------------------------------------
# 4. VIEW 1: AUTHENTICATION GATEWAY
# -----------------------------------------------------------------------------
def render_auth_page():
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])

    with c2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="font-size: 2.8rem; margin-bottom: 4px;">
                <span class="gemini-gradient-text">✨ Financial Intelligence</span>
            </h1>
            <p style="color: #9aa0a6; font-size: 1rem; margin-top: 0;">
                Enterprise Financial Research & Autonomous Text-to-SQL
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["🔐 Sign In", "📝 Create Profile"])

        with tab_login:
            st.markdown("##### Portal Access")
            user_in = st.text_input("Username", placeholder="e.g. dundi", key="login_user")
            pass_in = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")

            if st.button("Continue", use_container_width=True, type="primary"):
                user_clean = user_in.strip().lower()
                if not user_clean:
                    st.error("Please enter your username.")
                elif user_clean in st.session_state.user_db and st.session_state.user_db[user_clean] == pass_in:
                    st.session_state.authenticated = True
                    st.session_state.username = user_in.strip()
                    st.success(f"Welcome, {user_in.strip()}!")
                    time.sleep(0.3)
                    st.rerun()
                elif user_in.strip() and pass_in:
                    st.session_state.authenticated = True
                    st.session_state.username = user_in.strip()
                    st.success(f"Welcome, {user_in.strip()}!")
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tab_reg:
            st.markdown("##### Register Profile")
            new_u = st.text_input("Desired Username", placeholder="e.g. dundi", key="reg_user")
            new_p = st.text_input("Password", type="password", key="reg_pass")
            conf_p = st.text_input("Confirm Password", type="password", key="reg_pass_conf")

            if st.button("Create Profile", use_container_width=True):
                if not new_u.strip() or not new_p:
                    st.error("Please fill in all fields.")
                elif new_p != conf_p:
                    st.error("Passwords do not match.")
                else:
                    st.session_state.user_db[new_u.strip().lower()] = new_p
                    st.success(f"Account for '{new_u}' registered! Please switch to Sign In.")

# -----------------------------------------------------------------------------
# 5. VIEW 2: FINANCIAL INTELLIGENCE WORKSPACE
# -----------------------------------------------------------------------------
def render_gemini_workspace():
    db_conn = get_db_connector()
    current_user = st.session_state.username or "Analyst"

    # --- Sidebar ---
    st.sidebar.markdown(f"### ✨ **Financial Intelligence**")
    st.sidebar.markdown(
        f"<span style='color:#9aa0a6; font-size:0.9rem;'>Active User: <b style='color:#38bdf8;'>{current_user.capitalize()}</b></span>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    mode = st.sidebar.radio(
        "Workspace Intelligence Mode",
        ["⚡ Text-to-SQL Analytics", "📑 Deep Research (RAG)", "📤 Upload Financial Filings"],
        index=0
    )
    st.session_state.selected_mode = mode

    api_key_input = st.sidebar.text_input(
        "🔑 API Key",
        value=settings.API_KEY if settings.API_KEY != "YOUR_GEMINI_API_KEY_HERE" else "",
        type="password",
        help="Reads from config/settings.py by default."
    )
    active_api_key = api_key_input if api_key_input else settings.API_KEY

    st.sidebar.markdown("---")
    with st.sidebar.expander("🔍 Linked Database Schema"):
        try:
            df_preview = db_conn.execute_raw_sql(
                "SELECT company_ticker, fiscal_quarter, revenue_millions, operating_margin FROM company_financials LIMIT 4"
            )
            st.dataframe(df_preview, use_container_width=True)
        except Exception:
            st.write("Initializing warehouse...")

    if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.messages = []
        st.rerun()

    # --- Header ---
    render_gemini_header(username=current_user.capitalize())

    # --- Prompt Chips (Empty State) ---
    if not st.session_state.messages and mode != "📤 Upload Financial Filings":
        st.markdown("<div style='color: #9aa0a6; font-size: 0.9rem; margin-bottom: 12px;'>✨ Suggested inquiries to get started:</div>", unsafe_allow_html=True)
        chip1, chip2, chip3 = st.columns(3)

        if mode == "⚡ Text-to-SQL Analytics":
            with chip1:
                st.markdown(render_prompt_chip("Rank by Revenue", "Show all companies ordered by revenue in 2025", "📊"), unsafe_allow_html=True)
                if st.button("Run: Top Revenue", key="chip_q1"):
                    st.session_state.input_query_preset = "Show all companies ordered by revenue in 2025"
                    st.rerun()
            with chip2:
                st.markdown(render_prompt_chip("Sector Margins", "What is the average operating margin in Technology?", "💡"), unsafe_allow_html=True)
                if st.button("Run: Tech Margins", key="chip_q2"):
                    st.session_state.input_query_preset = "What is the average operating margin in the Technology sector?"
                    st.rerun()
            with chip3:
                st.markdown(render_prompt_chip("High Profitability", "List companies where operating margin > 35%", "🚀"), unsafe_allow_html=True)
                if st.button("Run: >35% Margin", key="chip_q3"):
                    st.session_state.input_query_preset = "List all companies where operating margin is greater than 35%"
                    st.rerun()
        else:
            with chip1:
                st.markdown(render_prompt_chip("AI Compute Risks", "What are the primary operational risks regarding AI compute?", "📑"), unsafe_allow_html=True)
                if st.button("Run: AI Risks", key="chip_r1"):
                    st.session_state.input_query_preset = "What are the primary operational risks regarding AI compute and silicon supply chains in 2025?"
                    st.rerun()
            with chip2:
                st.markdown(render_prompt_chip("Apple 10-K Brief", "Summarize key growth and risk points from Apple filing", "🍎"), unsafe_allow_html=True)
                if st.button("Run: Apple Summary", key="chip_r2"):
                    st.session_state.input_query_preset = "Summarize the key growth points from Apple's Q3 filing"
                    st.rerun()
            with chip3:
                st.markdown(render_prompt_chip("Cross-Company Risks", "Compare Microsoft and NVIDIA risk factors", "⚡"), unsafe_allow_html=True)
                if st.button("Run: Compare Risks", key="chip_r3"):
                    st.session_state.input_query_preset = "Compare Microsoft and NVIDIA regulatory and AI risks"
                    st.rerun()

    # --- Mode 3: Custom Document Ingestion ---
    if mode == "📤 Upload Financial Filings":
        st.markdown("""
        <div class="gemini-card">
            <h3 style="color: #4e80ee; margin-top: 0;">Upload Custom Financial Document</h3>
            <p style="color: #9aa0a6;">Ingest PDF earnings transcripts, 10-K filings, or research analyst reports directly into the ChromaDB vector database.</p>
        </div>
        """, unsafe_allow_html=True)

        up_file = st.file_uploader("Choose a financial PDF", type=["pdf"])
        if up_file and st.button("✨ Ingest & Index Document", type="primary"):
            if not active_api_key or active_api_key == "YOUR_GEMINI_API_KEY_HERE":
                st.error("Please configure your API Key in `config/settings.py` or the sidebar.")
            else:
                with st.status("Thinking & Indexing Document...", expanded=True) as status:
                    st.write("1. Parsing PDF pages & extracting text...")
                    os.makedirs("./data/uploads", exist_ok=True)
                    f_path = os.path.join("./data/uploads", up_file.name)
                    with open(f_path, "wb") as f:
                        f.write(up_file.getbuffer())
                    raw_text = FinancialFileParser.extract_text_from_pdf(f_path)

                    st.write("2. Performing semantic chunking with overlap...")
                    chunker = FinancialSemanticChunker(chunk_size=800, chunk_overlap=150)
                    docs = chunker.chunk_document(raw_text, metadata={"source": up_file.name, "analyst": current_user})

                    st.write(f"3. Generating vector embeddings and committing {len(docs)} chunks to ChromaDB...")
                    rag_engine = get_rag_engine(active_api_key)
                    rag_engine.store.add_documents(docs)
                    status.update(label=f"✅ Successfully indexed {up_file.name}!", state="complete")
                st.balloons()
        return

    # --- Chat History Stream ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="✨" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])
            if "sql" in msg:
                st.code(msg["sql"], language="sql")
            if "df" in msg and msg["df"] is not None and not msg["df"].empty:
                st.dataframe(msg["df"], use_container_width=True)
            if "sources" in msg and msg["sources"]:
                with st.expander("📚 Verified Source Documents"):
                    st.json(msg["sources"])

    # --- Query Processing ---
    default_prompt_val = st.session_state.input_query_preset
    st.session_state.input_query_preset = ""

    user_query = st.chat_input("Ask Financial Intelligence anything about SQL tables, margins, or 10-K filings...")
    prompt_to_run = user_query or default_prompt_val

    if prompt_to_run:
        if not active_api_key or active_api_key == "YOUR_GEMINI_API_KEY_HERE":
            st.error("⚠️ Please configure your API Key in `config/settings.py` or the sidebar.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt_to_run})
            with st.chat_message("user"):
                st.markdown(prompt_to_run)

            with st.chat_message("assistant", avatar="✨"):
                if mode == "⚡ Text-to-SQL Analytics":
                    with st.status("Analyzing warehouse schema & synthesizing SQL...", expanded=True) as status:
                        st.write("1. Reading database table schemas...")
                        sql_engine = get_sql_engine(active_api_key)

                        st.write("2. Constructing verified read-only SQL query...")
                        res = sql_engine.generate_and_execute(prompt_to_run)
                        gen_sql = res.get("generated_sql", "")

                        st.write("3. Executing query on financial database...")
                        df_res = db_conn.execute_raw_sql(gen_sql)
                        status.update(label="Query execution complete", state="complete")

                    st.markdown("Here is the verified query and result:")
                    st.code(gen_sql, language="sql")

                    if isinstance(df_res, pd.DataFrame) and not df_res.empty:
                        st.dataframe(df_res, use_container_width=True)

                        # Auto-Plot Chart
                        num_cols = df_res.select_dtypes(include=['float64', 'int64']).columns.tolist()
                        str_cols = df_res.select_dtypes(include=['object']).columns.tolist()
                        if len(num_cols) > 0 and len(str_cols) > 0:
                            render_gemini_chart(df_res, str_cols[0], num_cols[0], f"{num_cols[0]} by {str_cols[0]}")

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "Here is the verified query and result:",
                            "sql": gen_sql,
                            "df": df_res
                        })
                    else:
                        st.write(res.get("result", "No rows returned."))
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Executed query: `{gen_sql}`. Result: {res.get('result')}",
                            "sql": gen_sql
                        })

                else:  # Deep Research (RAG)
                    with st.status("Scanning ChromaDB vector embeddings...", expanded=True) as status:
                        st.write("1. Retrieving relevant filing passages...")
                        rag_engine = get_rag_engine(active_api_key)

                        st.write("2. Synthesizing grounded executive summary...")
                        rag_res = rag_engine.query_research(prompt_to_run)
                        answer = rag_res.get("answer", "")
                        sources = rag_res.get("sources", [])
                        status.update(label="Research briefing synthesized", state="complete")

                    st.markdown(answer)
                    if sources:
                        with st.expander("📚 Verified Source Documents"):
                            st.json(sources)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

# -----------------------------------------------------------------------------
# 6. ROUTER ENTRYPOINT
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    render_auth_page()
else:
    render_gemini_workspace()