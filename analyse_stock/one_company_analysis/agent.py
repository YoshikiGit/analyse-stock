from google.adk.agents.sequential_agent import SequentialAgent

from .agents import (
    analyst_agent,
    fundamental_agent,
    macro_agent,
    news_agent,
    price_agent,
    technical_agent,
)

root_agent = SequentialAgent(
    name="stock_orchestrator",
    description="銘柄コードを受け取り、各調査エージェントに順次調査を依頼し、最終的な投資判断をまとめる。",
    sub_agents=[
        price_agent,
        technical_agent,
        fundamental_agent,
        macro_agent,
        news_agent,
        analyst_agent,
    ],
)
