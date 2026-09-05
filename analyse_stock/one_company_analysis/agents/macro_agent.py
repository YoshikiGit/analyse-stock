from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool

from ..tools.market_data import get_macro_indicators

macro_agent = Agent(
    model="gemini-3.1-flash-lite",
    name="macro_agent",
    description="USD/JPY・VIX・CME日経先物・米10年債利回りから市場全体のマクロ環境リスクを評価するエージェント。",
    instruction="""
    get_macro_indicators ツールを呼び出し、USD/JPY、VIX指数、CME日経先物、米10年債利回りを取得する。
    これらは個別銘柄ではなく市場全体のリスク環境を表す指標であることに留意し、以下の観点で評価すること。

    - VIX: 20以上は警戒水準、30以上は市場が大きく不安定な状態
    - CME日経先物: 前日比プラスなら日本株全体に追い風、マイナスなら逆風
    - USD/JPY: 円安は輸出企業に追い風、急激な変動は不確実性要因
    - 米10年債利回り: 上昇は株式市場（特にグロース株）に逆風となりやすい

    最後に、これらを総合して 0〜100 点のマクロスコア（100が最もリスクの低い良好な市場環境）を算出し、
    その根拠を簡潔にまとめること。出力は次の形式に従うこと。

    マクロスコア: <0-100の整数>
    根拠: <各指標の簡潔な説明>
    """,
    tools=[FunctionTool(get_macro_indicators)],
    output_key="macro_report",
)
