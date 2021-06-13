import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import requests
from dataclasses import dataclass

@dataclass
class StockInfo:
    name: str
    basic_info: {}

    # コンストラクタを定義
    def __init__(self, name, basic_info):

        # メンバ
        self.name = name
        self.basic_info = basic_info


class main():
    
    # 株をフィルタ
    def set_condition(basic_info, key, value ):
        
        keyList = key.split("\n")
        #print(keyList)
        valueList = value.split("\n")
        
        # ディクショナリに格納
        basic_info[key] = value
        
        
        tmpIndex = 0
        for index in keyList:
            if "PER" in index:
                #print(index)
                if float(valueList[tmpIndex].rstrip("倍")) < 15:
                    return False
                    
                
            elif "PBR" in index:
                print(index)
                
            tmpIndex = tmpIndex + 1
        return True
            
    # /set_condition   
            
            
    # みん株URL
    MINKABU_URL = "https://minkabu.jp/stock/"
    
    try:
        # 銘柄コードの取得
        ##東証から上場企業の一覧を取得
        url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
        with urllib.request.urlopen(url) as u:
            with open('data_j.xls', 'bw') as o:
                    o.write(u.read())
        codelist = pd.read_excel("./data_j.xls")
        
        ## 各市場を整理
        #firstSectionCodeList = codelist.loc[codelist["市場・商品区分"] == "市場第一部（内国株）"]
        #secondSectionCodeList = codelist.loc[codelist["市場・商品区分"] == "市場第二部（内国株）"]
        mothersCodeList = codelist.loc[codelist["市場・商品区分"] == "マザーズ（内国株）"]
        jasdaqStandardCodeList = codelist.loc[codelist["市場・商品区分"] == "JASDAQ(スタンダード・内国株）"]
        jasdaqGrowthCodeList = codelist.loc[codelist["市場・商品区分"] == "JASDAQ(グロース・内国株）"]
        ## TOPIXを整理
        #topix100CodeList = codelist.loc[codelist["規模区分"].isin([ "TOPIX Core30" ,  "TOPIX Large70" ])]
        #topix500CodeList = codelist.loc[codelist["規模区分"].isin([ "TOPIX Core30" ,  "TOPIX Large70"  ,  "TOPIX Mid400" ])]
        #topix1000CodeList = codelist.loc[codelist["規模区分"].isin([ "TOPIX Core30" ,  "TOPIX Large70"  ,  "TOPIX Mid400", "TOPIX Small 1"])]
        #topixCodeList = codelist.loc[codelist["規模区分"].isin([ "TOPIX Core30" ,  "TOPIX Large70"  ,  "TOPIX Mid400", "TOPIX Small 1", "TOPIX Small 2"])]

        tmpIndex = 0
        
        # 対象市場の期待株
        all_info = []
        for index in mothersCodeList.index:
            
            url = MINKABU_URL + str(mothersCodeList.iloc[tmpIndex,1])
            if tmpIndex == 0:
                html = requests.get(url)
                print(url)
                
                # BeautifulSoupのHTMLパーサーを生成
                soup = BeautifulSoup(html.content, "html.parser")
                
                # データ格納用のディクショナリを準備
                basic_info = {}
                # 全<li>要素を抽出
                li_all = soup.find_all('li')
                for li in li_all:
                    # <li>要素内の<dt>要素を抽出
                    dt = li.find('dt')
                    if dt is None:
                        # <dt>要素がなければ処理不要
                        continue
        
                    # <li>要素内の<dd>要素を抽出
                    dd = li.find('dd')
                    
                    # <dt><dd>要素から文字列を取得
                    key = dt.text
                    value = dd.text
                    
                    # ディクショナリに格納
                    basic_info[key] = value
                    
                if set_condition(basic_info, key, value) == True:
                    stockInfo = StockInfo(mothersCodeList.iloc[tmpIndex,2], basic_info)
                    all_info.append(stockInfo)
                    print("all_info")
                    print(all_info)
                    
            tmpIndex = tmpIndex + 1
        

    except Exception as ex:
        print(ex)
    
    



