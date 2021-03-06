import gspread
import json
import selenium
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from time import sleep
import os
import csv
import pandas as pd
import io
from urllib import request
import urllib.parse
import re
from PIL import Image
from selenium.webdriver.support.select import Select
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
                 # パスを通すためのコード
import traceback
from selenium.common.exceptions import TimeoutException
import sys
from datetime import datetime, date, timedelta
import datetime
import pyautogui as pag
import pyocr
import pyocr.builders
import pyscreeze
from pyscreeze import ImageNotFoundException
import cv2
import pyperclip #クリップボードへのコピーで使用 
import tkinter
##git diff
#今日
now = '{0:%Y%m%d}'.format(datetime.datetime.now())
#Pandas.dfの準備

jsonf = "webscraping-7ad1c-bc2ff42a463d.json"
spread_sheet_key = "1kLMppQEqZyx8xQDyTVodsrUkze78cmbj-AqpL2UECdU"
profile_path = '\\Users\\saita\\AppData\\Local\\Google\\Chrome\\User Data\\seleniumpass'


item_not_list = open("item_not_list.txt").read().splitlines()

#chrome,Chrome Optionsの設定
options = Options()
#options.add_argument('--headless')                 # headlessモードを使用する
#options.add_argument('--disable-gpu')              # headlessモードで暫定的に必要なフラグ(そのうち不要になる)
options.add_argument('--disable-extensions')       # すべての拡張機能を無効にする。ユーザースクリプトも無効にする
options.add_argument('--proxy-server="direct://"') # Proxy経由ではなく直接接続する
options.add_argument('--proxy-bypass-list=*')      # すべてのホスト名
options.add_argument('--start-maximized')          # 起動時にウィンドウを最大化する
# options.add_argument('--incognito')          # シークレットモードの設定を付与
options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
options.add_argument('--user-data-dir=' + profile_path)
options.add_argument('--lang=ja')

options.add_argument("--remote-debugging-port=9222") 
# Google Spread Sheetsにアクセス
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonf, scope)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = spread_sheet_key
worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1
f = worksheet
##Tesseractのpath
path='C:\\Program Files\\Tesseract-OCR'
os.environ['PATH'] = os.environ['PATH'] + path

##global関数##
global startline
global pricecut

#git commit　--amend
class Listing :
    x_pre,y_pre,w_pre,h_pre = 0,0,0,0


    #textbox
    def textbox(self):

        def btn_event():
            global startline
            global pricecut
            startline = int(txt1.get())
            pricecut  = int(txt2.get())            
            root.destroy()

            

        # Tkクラス生成
        root = tkinter.Tk()
        # 画面サイズ
        root.geometry('300x200')
        # 画面タイトル
        root.title('テキストボックス')
        # ラベル
        lbl1 = tkinter.Label(text='開始する行')
        lbl1.place(x=10, y=50)
        lbl2 = tkinter.Label(text='値下げする値段(円)')
        lbl2.place(x=10, y=90)
        # テキストボックス
        txt1 = tkinter.Entry(width=20)
        txt1.place(x=130, y=50)
        txt2 = tkinter.Entry(width=20)
        txt2.place(x=130, y=90)
        # ボタン
        btn = tkinter.Button(root, text='OK', command=btn_event)
        btn.place(x=140, y=170)
        # 表示
        root.mainloop()

        # return startline,pricecut
    



        


    #スプレッドシートから必要な情報を取得する
    def getinformetion(self,line_num):
        product_name = worksheet.cell(line_num , 1).value #商品名
        description = worksheet.cell(line_num , 3).value #商品説明
        money = worksheet.cell(line_num , 2).value #金額
        image_num_first = int(worksheet.cell(line_num, 12).value)
        image_num_Last = int(worksheet.cell(line_num, 13).value)
        current_price = int(worksheet.cell(line_num, 15).value) #現在の価格
        serialno = int(worksheet.cell(line_num, 16).value) #現在の価格
        return serialno,product_name,description,money,image_num_first,image_num_Last,current_price



    
    #ポジショニング
    def posi(self,imagename):      
        print("start1")
        # for count  in range(5):
        #     try:
        #         #locateOnScreenでは左上のx座標, 左上のy座標, 幅, 高さのタプルを返す。
        print(imagename)
                
        x,y,w,h = pag.locateOnScreen('C:/Users/saita/workspace/lec_rpa/paypay/' + imagename + '.jpg',grayscale=True,confidence=.95)
        self.x_pre,self.y_pre,self.w_pre,self.h_pre = x,y,w,h
        print(x,y,w,h)
        return x,y,w,h
        #             break
        #     except ImageNotFoundException:
        #         #1秒待つ
        #         time.sleep(1)
        # ##所定の画像が見つからない場合、ひとつ前の動作を行う。

        # else:
        #     print(self.x_pre,self.y_pre,self.w_pre,self.h_pre) 
        #     self.move(self.x_pre,self.y_pre,self.w_pre,self.h_pre)
        #     x,y,w,h = pag.locateOnScreen('C:/Users/saita/workspace/lec_rpa/paypay/' + imagename + '.jpg',grayscale=True,confidence=.99)
        #     print(x,y,w,h)        
        # return x,y,w,h

    #マウス移動、クリック
    def move(self,x, y, w, h):
        center_x = x + w/2
        center_y = y + h/2
        pag.moveTo(center_x, center_y)
        pag.click()
        time.sleep(3)
    
    #画面の文字認識
    def character_recognition(self,product_name) :
        #対象の画像が見つかるまでスクロールする
        # for _ in range(30):
        #     try:
                #左画面をスクリーンショット
        sc = pag.screenshot(region=(0, 0, 1919,1079)) #始点x,y、幅、高さ
        lang = 'jpn'
        sc.save('./img/jpn.png')        
        img_path = './img/{}.png'.format(lang)
        img = Image.open(img_path)
        out_path = './img/{}_{}.png'
        tools = pyocr.get_available_tools()
        tool = tools[0]

        Line_boxes = tool.image_to_string(
            img,
            lang=lang,
            builder=pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        out = cv2.imread(img_path)
        print(str(Line_boxes))
        for d in Line_boxes:
            print(d.content)
            print(d.position)
            cv2.rectangle(out, d.position[0], d.position[1], (0, 0, 255), 2) #d.position[0]は認識した文字の左上の座標,[1]は右下
            cv2.imwrite(out_path.format(lang, 'Line_boxes'), out)  
            if(d.content== product_name): #Anacondaのアイコンを認識したらクリックする
                x1,y1 = d.position()[0]
                x2,y2 = d.position()[1]
        #     except :
        #         ##画像が見つからない場合、スクロールする
        #         pag.scroll(-100)
        #         time.sleep(0.5)
        #         print("スクロール")
        # else:
        #     print('対象が見つかりません')

        x,y,w,h = x1,y1,x2-x1,y2-y1   
        return x,y,w,h 

    
def main():
    global startline
    global pricecut
    listing = Listing()
    listing.textbox()
    print(startline)
    print(pricecut)
    line_num = startline - 1
    ##paypay起動
    x, y, w, h = listing.posi("paypay")
    listing.move(x, y, w, h)
    x, y, w, h = listing.posi("mypage")
    listing.move(x, y, w, h)
    x, y, w, h = listing.posi("shuppinsitashouhin")
    listing.move(x, y, w, h)
    ##スクロールして一番下の画面に行く
    for _ in range(20):
        pag.scroll(-100)
        time.sleep(0.5)
    time.sleep(1)

    for _ in range(120):
##画像up##
        imagenum = ''
        print("start")
        line_num = line_num + 1
        serialno,product_name,description,money,image_num_first,image_num_Last,current_price = listing.getinformetion(line_num)
        newprice = current_price - 10
        #出品する商品がない場合、強制終了
        if product_name == "finish" :
            sys.exit(1)
        else:
            pass
        
        ##値下げする商品を見つける##
        for _ in range(30):
            try:
                time.sleep(0.5)
                x, y, w, h = listing.posi("sc" + str(serialno))
                break
            except :
                ##画像が見つからない場合、スクロールする
                pag.moveTo(900, 600)
                pag.scroll(10)
                time.sleep(1)
                print("スクロール")            
        listing.move(x, y, w, h)
                   
        ##編集する##
        x, y, w, h = listing.posi("henshuusuru")
        listing.move(x, y , w, h)
        time.sleep(1)
        ##スクロール##
        for _ in range(3):
            pag.scroll(-100)
            time.sleep(1)
        ##販売価格##
        x,y,w,h = pag.locateOnScreen('C:/Users/saita/workspace/lec_rpa/paypay/' + "kakakuhenkou" + '.jpg',grayscale=True,confidence=.7)
        ##画像の下端中央をクリック##
        listing.move(x, y+50, w, h)
        for _ in range(4):
            pag.hotkey('backspace')
            pag.hotkey('delete')
        
        pyperclip.copy(newprice)
        ##スプレッドシートに書き込む##
        worksheet.update_cell(line_num, 15, str(newprice))
        pag.hotkey('ctrl', 'v')
        time.sleep(1)
        ##スクロール##
        for _ in range(3):
            pag.scroll(-100)
            time.sleep(1)
        ##変更する##
        x, y, w, h = listing.posi("henkousuru")
        listing.move(x, y, w, h)
        time.sleep(3)
        ##スクロール
        for _ in range(3):
            pag.scroll(-100)
            time.sleep(1)
        ##戻る##
        x, y, w, h = listing.posi("modoru_2")
        listing.move(x, y, w, h)
  
   
main()
        
 