from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool

from ..tools.market_data import get_fundamental_data

fundamental_agent = Agent(
    model="gemini-3.1-flash-lite",
    name="fundamental_agent",
    description="PER・PBR・ROE・EPS成長率・配当利回り・売上成長率・自己資本比率・キャッシュフローから企業のファンダメンタルズを評価するエージェント。",
    instruction="""
    証券コードを受け取り get_fundamental_data ツールを呼び出す。
    取得した以下の指標をもとに、割安度・収益性・成長性・財務健全性の4つの観点でファンダメンタルズを評価すること。

    - 割安度: PER, PBR（業種平均と比較して低いほど割安）
    - 収益性: ROE, ROA, 売上高利益率（高いほど良い。ROEは特に10%以上を目安に評価する）
    - 成長性: EPS成長率, 売上成長率（プラスかつ大きいほど良い。マイナスの場合は減益トレンドとして警戒する）
    - 財務健全性・キャッシュフロー: 自己資本比率（40%以上が目安）、営業キャッシュフロー・フリーキャッシュフローが
      プラスかどうか、配当利回りと配当性向（配当性向が過度に高い場合は持続性に懸念ありと判断する）

    「まずまずの企業を素晴らしい価格で買うより、素晴らしい企業をまずまずの価格で買う方が良い」という考え方に基づき、
    直近まで赤字だった企業がたまたま黒字化しただけのケースは高く評価しないこと。

    最後に、これらを総合して 0〜100 点のファンダメンタルスコア（100が最も割安かつ高成長・高収益）を算出し、
    その根拠を簡潔にまとめること。出力は次の形式に従うこと。

    ファンダメンタルスコア: <0-100の整数>
    根拠: <割安度・収益性・成長性・財務健全性それぞれの簡潔な説明>
    懸念点: <あれば記載。なければ「特になし」>
    """,
    tools=[FunctionTool(get_fundamental_data)],
    output_key="fundamental_report",
)
