import time
import urllib.request
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup


@dataclass
class StockInfo:
    name: str
    basic_info: {}

    # コンストラクタを定義
    def __init__(self, name, basic_info):

        # メンバ
        self.name = name
        self.basic_info = basic_info


# 値が設定されていなければskip
def hyphen_check(self, targetStr):
    if ("-" in targetStr):
        return False
    return True
# /hyphen_check


def shape_format(self, targetStr):
    shapedStr = targetStr.rstrip("倍")
    shapedStr = shapedStr.replace(',', '')
    return float(shapedStr)
# 株をフィルタ


def set_condition(self, basic_info, keyList):
    # print(keyList)
    # PER
    if self.hyphen_check(basic_info[keyList[5]]):
        if self.shape_format(basic_info[keyList[5]]) > 15:
            print("×PER OUT")
            return False
    else:
        return False
    # PBR
    if self.hyphen_check(basic_info[keyList[7]]):
        if self.shape_format(basic_info[keyList[7]]) > 1:
            print("×PBR OUT")
            return False
    # 時価総額（300億以下）
    if self.hyphen_check(basic_info[keyList[9]]):
        if float(basic_info[keyList[9]].rstrip("百万円").replace(',', '')) > 30000:
            print("×時価総額 OUT")
            return False
    # ROE
    roe = self.shape_format(
        basic_info[keyList[7]]) / self.shape_format(basic_info[keyList[5]])
    if roe < 10 or 20 < roe:
        return False
    print("Good")
    return True
# /set_condition


# みん株URL
MINKABU_URL = "https://minkabu.jp/stock/"
CHANGE_LINE = '''
'''

market_dict = {
    '1': 'プライム市場',
    '2': 'スタンダード市場',
    '3': 'グロース市場',
    '4': 'TOPIX',
}

target_market = input(f"""
    対象の市場を番号で選択
    1：{market_dict['1']}
    2：{market_dict['2']}
    3：{market_dict['3']}
    4：{market_dict['4']}
""")

if target_market not in market_dict:
    raise Exception('選択肢に該当する数字ではありません')

try:
    # 銘柄コードの取得
    # 東証から上場企業の一覧を取得
    url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
    with urllib.request.urlopen(url) as u:
        with open('data_j.xls', 'bw') as o:
            o.write(u.read())
            xlsCodelist = pd.read_excel("./data_j.xls")

    # 各市場を整理
    if target_market == '1':
        primeCodeList = xlsCodelist.loc[xlsCodelist["市場・商品区分"]
                                        == "プライム（内国株式）"]
        print(primeCodeList)

    elif target_market == '2':
        standardCodeList = xlsCodelist.loc[xlsCodelist["市場・商品区分"]
                                           == "スタンダード（内国株式）"]

    elif target_market == '3':
        print("===グロース（内国株式） 母数 ===")
        growthCodeList = xlsCodelist.loc[xlsCodelist["市場・商品区分"]
                                         == "グロース（内国株式）"]
        print(len(growthCodeList))

    elif target_market == '4':
        # TOPIXを整理
        topix100CodeList = xlsCodelist.loc[xlsCodelist["規模区分"].isin(
            ["TOPIX Core30",  "TOPIX Large70"])]
        topix500CodeList = xlsCodelist.loc[xlsCodelist["規模区分"].isin(
            ["TOPIX Core30",  "TOPIX Large70",  "TOPIX Mid400"])]
        topix1000CodeList = xlsCodelist.loc[xlsCodelist["規模区分"].isin(
            ["TOPIX Core30",  "TOPIX Large70",  "TOPIX Mid400", "TOPIX Small 1"])]
        topixCodeList = xlsCodelist.loc[xlsCodelist["規模区分"].isin(
            ["TOPIX Core30",  "TOPIX Large70",  "TOPIX Mid400", "TOPIX Small 1", "TOPIX Small 2"])]

    print(CHANGE_LINE)

    tmpIndex = 0

    # 対象市場の期待株
    all_info = []
    for index in topixCodeList.index:

        url = MINKABU_URL + str(topixCodeList.iloc[tmpIndex, 1])

        if 0 <= tmpIndex <= 600:
            print("■アクセス先URL")
            print(url)
            print(CHANGE_LINE)

            # 遅延でアクセス
            time.sleep(2)
            html = requests.get(url)

            # BeautifulSoupのHTMLパーサーを生成
            soup = BeautifulSoup(html.content, "html.parser")

            # データ格納用のディクショナリを準備

            basic_info = {}
            keyList = {}

            # 全<li>要素を抽出
            li_all = soup.find_all('li')

            listIndex = 0

            for li in li_all:
                # <li>要素内の<dt>要素を抽出
                dt = li.find('dt')
                if dt is None:
                    # <dt>要素がなければ処理不要
                    continue
                    # <li>要素内の<dd>要素を抽出（始値〜購入金額）
                dd = li.find('dd')

                # <dt><dd>要素から文字列を取得
                key = dt.text
                keyList[listIndex] = key

                # print(key)
                value = dd.text

                # TOP情報をディクショナリに格納
                basic_info[key] = value

                listIndex = listIndex + 1

            if set_condition(basic_info, keyList) == True:
                stockInfo = StockInfo(
                    topixCodeList.iloc[tmpIndex, 2], basic_info)
                all_info.append(stockInfo)

            tmpIndex = tmpIndex + 1
            print(CHANGE_LINE)

    if len(all_info) != 0:
        copy_text = ""
        print("完了しました")
        print("===== all_info =====")
        print(all_info)

    else:
        print("候補が存在しませんでした。")

except Exception as ex:
    print(ex)
