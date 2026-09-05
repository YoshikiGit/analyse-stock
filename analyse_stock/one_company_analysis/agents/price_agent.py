from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool

from ..tools.market_data import get_stock_price

price_agent = Agent(
    model="gemini-3.1-flash-lite",
    name="price_agent",
    description="指定銘柄の現在の株価情報を取得するエージェント。",
    instruction="""
    ユーザーまたは他のエージェントから渡された証券コード（例: 7203）について
    get_stock_price ツールを呼び出し、現在値・前日終値・騰落率・出来高・時価総額を取得すること。
    取得した結果は数値を丸めず、そのまま簡潔な日本語のサマリとして報告する。
    """,
    tools=[FunctionTool(get_stock_price)],
    output_key="price_report",
)
