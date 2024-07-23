import csv
from datetime import date, timedelta
import time
import urllib.request
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup


@dataclass
class StockInfo:
    url: str
    name: str
    basic_info: dict

    def __init__(self, url, name, basic_info):
        self.url = url
        self.name = name
        self.basic_info = basic_info


# 値が設定されていなければskip
def hyphen_check(targetStr):
    if "-" in targetStr:
        return False
    return True


def cleansing_data(basic_info):
    closing_price_key = ""
    for key in basic_info:
        if "倍" in basic_info[key]:
            basic_info[key] = basic_info[key].rstrip("倍")
        elif "百万円" in basic_info[key]:
            basic_info[key] = basic_info[key].rstrip("百万円")
        elif "円" in basic_info[key]:
            basic_info[key] = basic_info[key].rstrip("円")
        elif "株" in basic_info[key]:
            basic_info[key] = basic_info[key].rstrip("株")

        if "前日終値" in key:
            closing_price_key = key

        basic_info[key] = basic_info[key].replace(",", "")

    basic_info["前日終値"] = basic_info[closing_price_key]
    del basic_info[closing_price_key]


# 条件に合う株をフィルタ
def filter_by_condition(basic_info):
    # PER
    if hyphen_check(basic_info["PER(調整後)"]):
        if float(basic_info["PER(調整後)"]) > 15:
            print("PER：×")
            return False
        else:
            print("PER：○")
    else:
        return False

    # PBR
    if hyphen_check(basic_info["PBR"]):
        if float(basic_info["PBR"]) > 1:
            print("PBR：×")
            return False
        else:
            print("PBR：○")
    else:
        print("PBR：×")
        return False
    # 時価総額（300億以下）
    # if hyphen_check(basic_info['時価総額']):
    #    if float(basic_info['時価総額']) > 30000:
    #        print("×時価総額 OUT")
    #        return False

    # ROE
    roe = (float(basic_info["PBR"])) / float((basic_info["PER(調整後)"])) * 100

    if roe < 10:
        print("ROE：×")
        return False
    else:
        print("ROE：○")

    # 前日の日付を計算
    per_day_money = float(basic_info["前日終値"]) * float(basic_info["出来高"])
    if per_day_money < 1000000000:
        print("1日に動いた額：×")
        return False

    print("Good")
    return True


def _write_csv(all_info):
    with open("output.csv", "w", newline="") as csvfile:
        header = [
            [
                "社名",
                "url",
                "始値",
                "高値",
                "安値",
                "配当利回り",
                "単元株数（株）",
                "PER(調整後)",
                "PSR",
                "PBR",
                "出来高（株）",
                "時価総額",
                "発行済株数（株）",
                "株主優待",
                "購入金額",
                "前日終値",
            ]
        ]
        writer = csv.writer(csvfile)
        writer.writerows(header)
        for stock_info in all_info:
            tmp_data = []
            tmp_data.append(stock_info.name)
            tmp_data.append(stock_info.url)
            for value in stock_info.basic_info.values():
                tmp_data.append(value)

            writer.writerows([tmp_data])


# みん株URL
MINKABU_URL = "https://minkabu.jp/stock/"
# 日本取引所グループURL
JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"

market_dict = {
    "1": "プライム市場",
    "2": "スタンダード市場",
    "3": "グロース市場",
    "4": "TOPIX",
}

target_market = input(
    f"""
    対象の市場を番号で選択
    1：{market_dict['1']}
    2：{market_dict['2']}
    3：{market_dict['3']}
    4：{market_dict['4']}
"""
)

if target_market not in market_dict:
    raise Exception("選択肢に該当する数字ではありません")

print(market_dict[str(target_market)] + "を選択")

try:
    # 銘柄コードの取得
    # 東証から上場企業の一覧を取得
    with urllib.request.urlopen(JPX_URL) as u:
        with open("data_j.xls", "bw") as o:
            o.write(u.read())
            xlsCodelist = pd.read_excel("./data_j.xls")

    # 各市場をフィルタ
    if target_market == "1":
        filterdMarketList = xlsCodelist.loc[
            xlsCodelist["市場・商品区分"] == "プライム（内国株式）"
        ]
    elif target_market == "2":
        filterdMarketList = xlsCodelist.loc[
            xlsCodelist["市場・商品区分"] == "スタンダード（内国株式）"
        ]
    elif target_market == "3":
        filterdMarketList = xlsCodelist.loc[
            xlsCodelist["市場・商品区分"] == "グロース（内国株式）"
        ]
    elif target_market == "4":
        # TOPIXを整理
        filterdMarketList = xlsCodelist.loc[
            xlsCodelist["規模区分"].isin(
                [
                    "TOPIX Core30",
                    "TOPIX Large70",
                    "TOPIX Mid400",
                    "TOPIX Small 1",
                    "TOPIX Small 2",
                ]
            )
        ]

    # 対象市場の期待株
    all_info = []
    for index, val in enumerate(filterdMarketList.index):
        # if len(all_info) > 5:
        #     break

        if len(str(filterdMarketList.iloc[index, 1])) != 4:
            continue

        url = MINKABU_URL + str(filterdMarketList.iloc[index, 1])

        print("\n" + "■アクセス先URL")
        print(url + "\n")

        # 遅延でアクセス
        time.sleep(2)
        html = requests.get(url)

        # BeautifulSoupのHTMLパーサーを生成
        soup = BeautifulSoup(html.content, "html.parser")

        # データ格納用のディクショナリを準備
        basic_info = {}

        reference_indicators = soup.select("[class='ly_vamd']")

        key_list_index = 0

        for ri in reference_indicators:

            th = ri.find("th")
            td = ri.find("td")

            if th == None or td == None:
                continue

            key = th.text
            indicator_value = td.text

            # TOP情報をディクショナリに格納
            basic_info[key] = indicator_value
            key_list_index = key_list_index + 1

        cleansing_data(basic_info)
        print("Done：cleansing_data")
        print(basic_info)

        if filter_by_condition(basic_info) == True:
            stockInfo = StockInfo(
                url,
                filterdMarketList.iloc[index, 2],
                basic_info,
            )
            all_info.append(stockInfo)

    if len(all_info) != 0:
        print("完了")
        print("===== all_info =====")
        print(all_info)
        # CSVファイルにデータを書き込む
        _write_csv(all_info)

    else:
        print("候補が存在しませんでした。")

except Exception as ex:
    print(ex)
