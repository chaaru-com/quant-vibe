# 🌌 Quant-Vibe Architecture 3.0

Autonomous Multi-Agent Ingestion, Backtesting & Defensive Circuit Guardrails for quantitative trading hypotheses.

## Overview

Quant-Vibe Architecture 3.0 translates discretionary "vibes" or natural language strategies into quantitative backtests. It coordinates specialized agents inside a secure, monitored feedback loop:

1. **Hypothesis Agent**: Parses raw strategy prompts into structured technical indicator parameters (EMA/SMA windows).
2. **Backtest Coder Agent**: Autonomously writes Python code using `pandas` and `numpy` to implement backtest logic.
3. **Active Defense (Circuit Breaker)**: Dynamically inspects the generated script statically for unauthorized imports (AgBOM validation) and lookahead bias (ensuring appropriate `.shift(1)` signals), and monitors real-time drawdown to terminate execution if risk limits are breached.
4. **Sandbox Executor**: Runs the strategy code inside an isolated environment.
5. **Risk Evaluator Agent**: Processes the backtest output, computes Sharpe Ratio, maximum drawdown, and win rates, and outputs a formatted Markdown report.

---

## Getting Started

### 1. Install Dependencies

Ensure you have Python 3.10+ installed. Clone the repository, navigate to the `quant` folder, and install the required libraries:

```bash
pip install -r requirements.txt
```

### 2. Fetch and Ingest Market Data

Download historical data for the Nifty 100 index (`^CNX100`) from Yahoo Finance and clean/populate the local SQLite database:

```bash
# 1. Download historical data (generates nifty100_historical.csv)
python download_data.py

# 2. Clean volume anomalies & ingest to SQLite (generates nifty100.db)
python data_janitor.py
```

### 3. Run the Streamlit Application

Start the web application dashboard locally:

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` to use the strategy simulator dashboard!

---

## File Structure

- `app.py`: Streamlit dashboard and UI visualization.
- `quant_desk.py`: Multi-agent pipeline orchestrating the Hypothesis, Coder, and Risk Evaluator agents.
- `circuit_breaker.py`: The security sandbox/guardrails (static analysis, dependency analysis, drawdown guardrails).
- `sandbox.py`: Sandbox runner for executing code.
- `download_data.py` & `data_janitor.py`: Scripts to download and prepare SQLite database.
- `mcp_server.py`: Model Context Protocol server skeleton to expose database tools.
- `requirements.txt`: Python package dependencies.
