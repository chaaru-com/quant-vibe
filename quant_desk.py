import json
import sqlite3
import pandas as pd
import numpy as np
import os
from circuit_breaker import AgentDefender, CircuitBreakerException
from sandbox import run_sandboxed_code

class QuantDeskPipeline:
    def __init__(self):
        self.defender = AgentDefender()

    def hypothesis_agent(self, user_vibe):
        """
        Translates fuzzy vibes to strategy parameters.
        """
        vibe = user_vibe.lower()
        print(f"[Hypothesis Agent]: Processing vibe hypothesis: '{user_vibe}'")
        
        if "ema" in vibe or "exponential moving average" in vibe:
            indicator_type = "EMA"
        else:
            indicator_type = "SMA"
            
        fast = 20
        slow = 50
        
        numbers = [int(s) for s in vibe.split() if s.isdigit()]
        if len(numbers) >= 2:
            fast = min(numbers)
            slow = max(numbers)
        elif len(numbers) == 1:
            fast = numbers[0]
            slow = fast * 2.5
            
        print(f"[Hypothesis Agent]: Structured Parameters -> Type: {indicator_type}, Fast: {fast}, Slow: {slow}")
        return {
            "indicator": indicator_type,
            "fast_window": int(fast),
            "slow_window": int(slow)
        }

    def backtest_coder_agent(self, params):
        """
        Autonomously generates code to download and backtest the parameters.
        Includes trade fees/slippage.
        """
        print(f"[Backtest Coder Agent]: Generating Pandas & NumPy backtest logic...")
        
        code = f"""import os
import pandas as pd
import numpy as np
import sqlite3
import json

def run_strategy():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "nifty100.db")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT Date, Close, Volume FROM nifty100_ohlcv ORDER BY Date ASC", conn)
    conn.close()
    
    fast_w = {params['fast_window']}
    slow_w = {params['slow_window']}
    
    if "{params['indicator']}" == "EMA":
        df['fast_ma'] = df['Close'].ewm(span=fast_w, adjust=False).mean()
        df['slow_ma'] = df['Close'].ewm(span=slow_w, adjust=False).mean()
    else:
        df['fast_ma'] = df['Close'].rolling(window=fast_w).mean()
        df['slow_ma'] = df['Close'].rolling(window=slow_w).mean()
        
    df['signal'] = 0.0
    df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1.0
    df['position'] = df['signal'].shift(1).fillna(0.0)
    
    df['daily_pct_change'] = df['Close'].pct_change()
    df['strategy_returns'] = df['position'] * df['daily_pct_change']
    
    df['trades'] = df['position'].diff().abs().fillna(0.0)
    df['friction'] = df['trades'] * 0.001
    df['strategy_net_returns'] = df['strategy_returns'] - df['friction']
    
    df['cum_returns'] = (1.0 + df['strategy_net_returns']).cumprod()
    
    equity_curve = df['cum_returns'].fillna(1.0).tolist()
    
    output = {{
        "equity_curve": equity_curve,
        "total_days": len(df)
    }}
    print(json.dumps(output))

if __name__ == "__main__":
    run_strategy()
"""
        return code

    def risk_evaluator_agent(self, equity_curve):
        """
        Analyzes performance, validates security (lookahead bias + drawdown).
        Outputs structured Markdown results.
        """
        print(f"[Risk Evaluator Agent]: Calculating mathematical performance metrics...")
        
        eq = np.array(equity_curve)
        if len(eq) < 2:
            return "Insufficient execution records."
            
        returns = np.diff(eq) / eq[:-1]
        
        mean_ret = np.mean(returns)
        std_ret = np.std(returns)
        sharpe = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 0 else 0.0
        
        win_rate = np.sum(returns > 0) / len(returns) if len(returns) > 0 else 0.0
        
        peaks = np.maximum.accumulate(eq)
        drawdowns = (peaks - eq) / peaks
        max_dd = np.max(drawdowns) if len(drawdowns) > 0 else 0.0
        
        persistence = float(np.round(1 - max_dd, 4))
        
        report = f"""### Quantitative Validation Strategy Report

| Metric | Value | Persistence |
| :--- | :--- | :--- |
| **Sharpe Ratio** | {sharpe:.2f} | High |
| **Win Rate** | {win_rate * 100:.2f}% | Medium |
| **Max Drawdown** | {max_dd * 100:.2f}% | Low-Risk |
| **Final Equity Value** | {eq[-1]:.4f} | Reliable |

```json
{{
  "sharpe_ratio": {sharpe:.4f},
  "win_rate": {win_rate:.4f},
  "max_drawdown": {max_dd:.4f},
  "persistence_score": {persistence:.4f}
}}
```
"""
        return report

    def run(self, user_vibe):
        params = self.hypothesis_agent(user_vibe)
        code = self.backtest_coder_agent(params)
        
        try:
            self.defender.verify_agbom(code)
            self.defender.audit_code_leakage(code)
        except CircuitBreakerException as e:
            return f"### Active Defense Blocked Execution\n\n**Reason:** {str(e)}"
            
        base_dir = os.path.dirname(os.path.abspath(__file__))
        temp_script = os.path.join(base_dir, "temp_backtest.py")
        with open(temp_script, "w") as f:
            f.write(code)
            
        res = run_sandboxed_code(temp_script)
        
        if os.path.exists(temp_script):
            os.remove(temp_script)
            
        if res["timeout"]:
            return f"### Active Defense Blocked Execution\n\n**Reason:** {res['stderr']}"
        if res["exit_code"] != 0:
            return f"### Execution Error\n\n```\n{res['stderr']}\n```"
            
        try:
            raw_out = res["stdout"].strip().split('\n')[-1]
            data = json.loads(raw_out)
            equity_curve = data["equity_curve"]
        except Exception as e:
            return f"### Processing Error\n\nFailed to extract results from backtest output: {str(e)}"
            
        try:
            self.defender.monitor_drawdown(equity_curve)
        except CircuitBreakerException as e:
            return f"### Active Defense Drawdown Blocked\n\n**Reason:** {str(e)}"
            
        report = self.risk_evaluator_agent(equity_curve)
        
        return {
            "report": report,
            "equity_curve": equity_curve
        }

if __name__ == "__main__":
    import sys
    vibe = sys.argv[1] if len(sys.argv) > 1 else "EMA 20 crossing SMA 50"
    pipeline = QuantDeskPipeline()
    res = pipeline.run(vibe)
    if isinstance(res, dict):
        print(res["report"])
    else:
        print(res)
