import pyautogui as gui

import time
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from PIL import Image

def main():
    # 履歴一覧の縦座標の固定
    ROW_1_POSITION = 1372.0
    
    # 出現した座標
    historyList = []
    historyRow1 = [(1436.0, ROW_1_POSITION), (1501.0, ROW_1_POSITION), (1566.0, ROW_1_POSITION), (1625.0, ROW_1_POSITION),(1693.0, ROW_1_POSITION), (1763.0, ROW_1_POSITION), (1829.0, ROW_1_POSITION)]
    
    try:
        # ブラウザを開く。
        #driver = webdriver.Chrome(executable_path='./chromedriver')
        # 対象のサイトに遷移する
        #driver.get('https://www.verajohn.com/ja')

        #time.sleep(0.5)
        
        #mailAddress = driver.find_element_by_css_selector('#signin-mail')
        #mailAddress.clear()
        #mailAddress.send_keys("ysklove.music1stsight@gmail.com")
        
        #password = driver.find_element_by_css_selector('#signin-pass')
        #password.clear()
        #password.send_keys("0425Yoshiki")
        
        # ログインボタン押下
        #button = driver.find_element_by_css_selector('#edit-submit-signin')
        #button.click()
        #time.sleep(2)
        # crazytimeへ
        #driver.get('https://www.verajohn.com/ja/game/live-crazy-time')
        #time.sleep(13)

        # 統計表示

        #driver.set_window_position(25, 25)
        #driver.set_window_size(1300, 800)
       
        #time.sleep(5)
       
        # 画像認識
        #s = gui.screenshot()
        #s.save('screenshot1.png')
        s =Image.open("./screenshot1.png")
        

            
        # 座標の文ループする
        for point in historyRow1:
            color = s.getpixel((point))
            #色の赤成分を取り出す
            colorR = color[0]
            colorG = color[1]
            colorB = color[2]
            print(color)
            if colorR < 200 and colorG > 200 and colorB > 200:
                print("1da")
            if colorR > 200 and colorG > 180 and colorB < 140:
                print("2da")
            if colorR > 200 and colorG < 210 and  colorB > 200:
                print("5da")
            if colorR >= 200 and colorG < 190 and colorB > 220:
                print("10da")
            if colorR > 160 and colorB < 60:
                print("key")
            if colorR > 210 and colorG > 210 and colorB > 210:
                print("mato")
                
        #右下の1を取得
        img = list(gui.locateAllOnScreen("../resource/img/init-1.png", region=(690, 500, 1290, 1100), grayscale=True, confidence=0.85))
        print("1の数")
        print(len(img))
        
        #右下の2を取得
        img2 = list(gui.locateAllOnScreen("../resource/img/init-2.png", region=(690, 500, 1290, 1100),  grayscale=True, confidence=0.85))
        print("2の数")
        print(len(img2))
        
        #右下の10を取得
        img10 = list(gui.locateAllOnScreen("../resource/img/init-10.png", region=(690, 500, 1290, 1100),  grayscale=True, confidence=0.85))
        print("10の数")
        print(len(img10))


    except Exception as ex:
        print(ex)
        
main()

#def worker():
#    print(time.gmtime())
#    time.sleep(8)

#def mainloop(time_interval, f):
#    now = time.time()
#    while True:
#        t = threading.Thread(target=f)
#        t.setDaemon(True)
#        t.start()
#        t.join()
#        wait_time = time_interval - ( (time.time() - now) % time_interval )
#        time.sleep(wait_time)

#mainloop(5, worker)