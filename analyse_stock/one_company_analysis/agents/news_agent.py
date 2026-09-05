from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool

from ..tools.market_data import search_news

news_agent = Agent(
    model="gemini-3.1-flash-lite",
    name="news_agent",
    description="直近1週間のニュースから企業に関するセンチメントを評価するエージェント。",
    instruction="""
    企業名を受け取り search_news ツールを呼び出し、直近1週間のニュース見出しを取得する。
    各ニュースの見出しから、業績上方修正・新製品・提携・不祥事・訴訟・大量離職などの
    ポジティブ／ネガティブ要因を抽出し、全体のセンチメントを評価すること。
    ニュースが取得できない、または該当が無い場合は「材料なし」として中立に評価すること。

    最後に、これらを総合して 0〜100 点のニューススコア（100が最もポジティブ）を算出し、
    その根拠を簡潔にまとめること。出力は次の形式に従うこと。

    ニューススコア: <0-100の整数>
    センチメント: <ポジティブ/中立/ネガティブ>
    根拠: <参照した主要なニュース見出しとその評価理由>
    """,
    tools=[FunctionTool(search_news)],
    output_key="news_report",
)
