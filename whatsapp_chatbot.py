from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtGui import QPixmap

import time
import sys
from threading import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from simon.accounts.pages import LoginPage

import openai
# Set up your API key
openai.api_key = "Put your API here"

class MainWindow(QtWidgets.QMainWindow):      
    def __init__(self):   
        super(MainWindow, self).__init__()
        uic.loadUi('gui.ui', self)
        self.connectBtn.clicked.connect(self.connect)
        self.stopBtn.clicked.connect(self.stop)   
        self.replyBtn.clicked.connect(self.replyThread)

        self.greenLight = QPixmap('greenLight.png')
        self.redLight = QPixmap('redLight.png')
        self.status.setPixmap(self.redLight)
        self.status.setScaledContents(True)        
        self.show() 

    def connect(self):

        try:
            # Creating the driver (browser)
            self.driver = webdriver.Firefox()
            # Login (Get your phone ready to read the QR code)
            login_page = LoginPage(self.driver)
            login_page.load()
            QMessageBox.about(self, "Scan QR code", "Scan QR code and wait for few seconds!")

        except:   
            QMessageBox.about(self, "Error", "Check your connection")

    def stop(self):
        self.running = False
        QMessageBox.about(self, "Script stopped", "Script stopped")
        self.status.setPixmap(self.redLight)
        self.status.setScaledContents(True)  

    def replyThread(self):      
        t1=Thread(target=self.reply)
        self.running = True
        self.status.setPixmap(self.greenLight)
        self.status.setScaledContents(True) 
        QMessageBox.about(self, "Script started", "Script started")
        t1.start()

    def reply(self):
        while self.running:
            # For getting unread chats 
            unread_chats = self.driver.find_elements('xpath',"// span[@class='l7jjieqr cfzgl7ar ei5e7seu h0viaqh7 tpmajp1w c0uhu3dl riy2oczp dsh4tgtl sy6s5v3r gz7w46tb lyutrhe2 qfejxiq4 fewfhwl7 ovhn1urg ap18qm3b ikwl5qvt j90th5db aumms1qt']")
            # In the above line Change the xpath's class name from the current time class name by inspecting span element
            # which containing the number of unread message showing the contact card inside a green circle before opening the chat room.
    
            # Open each chat using loop and read message.
            for chat in unread_chats:
                chat.click()
                
                name =  self.driver.find_element('xpath',"// span[@data-testid='conversation-info-header-chat-title']")
                print(name.text)
                # For getting message to perform action
                message = self.driver.find_elements('xpath',"//div[@class='copyable-text']")
                # print last massage in chat
                print(message[len(message)-1].text)
                
                # Send the API request
                prompt = 'reply instantly, Act as if you were me and you got this message what would you reply:' + message[len(message)-1].text
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                response =response['choices'][0]['message']['content']
                print(response)
                
                
                text_input = self.driver.find_element('xpath',"//div[@title='Type a message']")
                for i in response:
                    text_input.send_keys(i)
                text_input.send_keys(Keys.RETURN) 

                # Send logs to GUI
                self.textBrowser.append(f'Sender: {name.text}')
                self.textBrowser.append(f'Message: {message[len(message)-1].text}')
                self.textBrowser.append(f'Reply: {response}')
                self.textBrowser.append('--------------------------')

                # Go back to pinned message (delete next 2 lines if you don't have a pinned chat)
                pinned = self.driver.find_element('xpath',"// span[@title='Notes']")
                pinned.click()
       
app = 0
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec_()                    
