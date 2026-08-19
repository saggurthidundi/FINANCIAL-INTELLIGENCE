import streamlit as st
import plotly.express as px
import pandas as pd

def render_gemini_header(username: str = "Dundi"):
    st.markdown(f"""
    <div style="margin-top: 10px; margin-bottom: 25px;">
        <h1 style="font-size: 2.6rem; font-weight: 700; margin-bottom: 2px;">
            <span class="gemini-gradient-text">Hello, {username}</span>
        </h1>
        <p style="color: #9aa0a6; font-size: 1.15rem; margin-top: 0;">
            How can I help you analyze financial filings or query structured databases today?
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_prompt_chip(title: str, subtitle: str, icon: str = "✨"):
    return f"""
    <div class="gemini-chip">
        <div style="font-size: 1.2rem; margin-bottom: 8px;">{icon}</div>
        <div style="color: #e3e3e3; font-weight: 600; font-size: 0.95rem; margin-bottom: 4px;">{title}</div>
        <div style="color: #9aa0a6; font-size: 0.82rem;">{subtitle}</div>
    </div>
    """

def render_gemini_chart(df: pd.DataFrame, x: str, y: str, title: str):
    fig = px.bar(
        df,
        x=x,
        y=y,
        title=title,
        template="plotly_dark",
        color_discrete_sequence=["#4E80EE"],
        text_auto=".2s"
    )
    fig.update_layout(
        paper_bgcolor="#1e1f20",
        plot_bgcolor="#1e1f20",
        font=dict(family="Google Sans, sans-serif", color="#9aa0a6"),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig, use_container_width=True)