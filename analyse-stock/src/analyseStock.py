import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import requests
import time
from dataclasses import dataclass
import pyperclip
import tkinter as tk
from tkinter import messagebox


@dataclass
class StockInfo:
    name: str
    basic_info: {}

    # コンストラクタを定義
    def __init__(self, name, basic_info):

        # メンバ
        self.name = name
        self.basic_info = basic_info


class Main():
    # 値が設定されていなければskip
    def hyphen_check(self, targetStr):
        if ("-" in targetStr):
            return False;
        
        return True;
    # /hyphen_check
    
    def shape_format(self, targetStr):
        shapedStr = targetStr.rstrip("倍");
        shapedStr = shapedStr.replace(',', '');
        return float(shapedStr);
    
    
    # 株をフィルタ
    def set_condition(self, basic_info, keyList):
        #print(keyList)
        
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
        roe = self.shape_format(basic_info[keyList[7]]) / self.shape_format(basic_info[keyList[5]])
        if roe < 10 or 20 < roe:
            return False
        
        print("Good")
        return True
            
    # /set_condition
                        
main = Main()      

# みん株URL
MINKABU_URL = "https://minkabu.jp/stock/"
CHANGE_LINE = '''
'''
    
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
    #mothersCodeList = codelist.loc[codelist["市場・商品区分"] == "マザーズ（内国株）"]
    #print("===マザーズ（内国株） 母数 ===")
    #print(len(mothersCodeList))
    print("=========================")
    print("=== JASDAQ(スタンダード・内国株） 母数 ===")
    #jasdaqStandardCodeList = codelist.loc[codelist["市場・商品区分"] == "JASDAQ(スタンダード・内国株）"]            
    mothersCodeList = codelist.loc[codelist["市場・商品区分"] == "JASDAQ(スタンダード・内国株）"]            
    print(len(mothersCodeList))
    print("====================================")
    print("=== JASDAQ(グロース・内国株 母数） ===")
    jasdaqGrowthCodeList = codelist.loc[codelist["市場・商品区分"] == "JASDAQ(グロース・内国株）"]
    print(len(jasdaqGrowthCodeList))
    print("=================================")

    print(CHANGE_LINE)
        
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
            
        if 0 <= tmpIndex <= 600:
            print ("■アクセス先URL")
            print (url)
            print(CHANGE_LINE)
                
            # 1s遅延でアクセス
            time.sleep(2)
            html = requests.get(url)
                
            # BeautifulSoupのHTMLパーサーを生成
            soup = BeautifulSoup(html.content, "html.parser")
                
            # データ格納用のディクショナリを準備
            
            basic_info = {}
            keyList = {}
                
            # 全<li>要素を抽出
            li_all = soup.find_all('li')
                
            listIndex = 0;
                
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

                    
                #print(key)
                value = dd.text
                    
                # TOP情報をディクショナリに格納
                basic_info[key] = value
                    
                listIndex = listIndex + 1
                    
            if main.set_condition(basic_info, keyList) == True:
                stockInfo = StockInfo(mothersCodeList.iloc[tmpIndex,2], basic_info)
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
    
    



