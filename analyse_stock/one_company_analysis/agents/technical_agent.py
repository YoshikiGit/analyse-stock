from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool

from ..tools.market_data import get_technical_indicators

technical_agent = Agent(
    model="gemini-3.1-flash-lite",
    name="technical_agent",
    description="テクニカル指標（RSI・MACD・ボリンジャーバンド・移動平均線）から短期〜中期のトレンドを評価するエージェント。",
    instruction="""
    証券コードを受け取り get_technical_indicators ツールを呼び出す。
    取得した RSI, MACD, ボリンジャーバンド, 移動平均線(5/25/75日) をもとに、
    以下の観点でテクニカル評価を行うこと。

    - RSI: 70以上は買われすぎ、30以下は売られすぎと判断する
    - MACD: MACDがシグナルを上抜けていれば買いシグナル、下抜けていれば売りシグナル
    - ボリンジャーバンド: %bが1に近いほど上限に接近（過熱）、0に近いほど下限に接近（売られすぎ）
    - 移動平均線: 5日線>25日線>75日線なら上昇トレンド、逆順なら下降トレンド

    最後に、これらを総合して 0〜100 点のテクニカルスコア（100が最も強気）を算出し、
    その根拠を簡潔にまとめること。出力は次の形式に従うこと。

    テクニカルスコア: <0-100の整数>
    トレンド判定: <上昇/下降/レンジ>
    根拠: <RSI・MACD・BB・移動平均線それぞれの簡潔な説明>
    """,
    tools=[FunctionTool(get_technical_indicators)],
    output_key="technical_report",
)
