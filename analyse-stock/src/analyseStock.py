import pyautogui as gui
import pandas as pd
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib.request

def main():
    
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


    except Exception as ex:
        print(ex)
        
main()