import streamlit as st
import pandas as pd
import numpy as np
import io
import contextlib
from quant_desk import QuantDeskPipeline

st.set_page_config(page_title="Quant-Vibe Architecture 3.0", layout="wide")

# Premium look and feel setup
st.markdown("""
<style>
    body {
        color: #e2e8f0;
        background-color: #0b0f19;
    }
    .stApp {
        background-color: #0b0f19;
    }
    h1 {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .metric-card {
        background-color: #111827;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #1f2937;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("🌌 Quant-Vibe Architecture 3.0")
st.subheader("Autonomous Multi-Agent Ingestion, Backtesting & Defensive Circuit Guardrails")

st.markdown("""
This system ingests raw time-series data using a BDD **Data Janitor**, isolates calculations through custom **MCP** database access, 
and translates discretionary "vibes" into quantitative simulations run in an ephemeral sandboxed container.
""")

# Strategy Prompt Input
vibe_input = st.text_input("Define Strategy Vibe / Hypothesis:", "EMA 20 crossing SMA 50 on high volume")

if st.button("Initialize Multi-Agent Orchestration Desk", use_container_width=True):
    # Setup capture of standard outputs to print OpenTelemetry trace logs
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        pipeline = QuantDeskPipeline()
        res = pipeline.run(vibe_input)
    
    logs = f.getvalue()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### 🪵 OpenTelemetry Trace Logs")
        formatted_logs = ""
        for line in logs.split('\n'):
            if not line.strip():
                continue
            if "[Hypothesis Agent]" in line:
                formatted_logs += f"🟠 **[agent.think]** {line}\n\n"
            elif "[Backtest Coder Agent]" in line:
                formatted_logs += f"🔵 **[agent.tool]** {line}\n\n"
            elif "[Risk Evaluator Agent]" in line:
                formatted_logs += f"🟢 **[agent.validate]** {line}\n\n"
            else:
                formatted_logs += f"▪️ {line}\n\n"
        st.markdown(formatted_logs)

    with col2:
        if isinstance(res, dict):
            st.success("Strategy Simulated Successfully under Spec-Driven Governance!")
            st.write("### 📊 Governance Strategy Report")
            st.markdown(res["report"])
            
            # Draw Equity curve chart
            eq_curve = res["equity_curve"]
            chart_df = pd.DataFrame({
                "Equity Multiplier": eq_curve
            })
            st.line_chart(chart_df, color="#6366f1")
        else:
            st.error("Active Defense Circuit Breaker Tripped!")
            st.write(res)
