import sys
import logging
import threading
import time

import subprocess
# import paramiko
import socket
from playsound import playsound
import multiprocessing
import os
from mcstatus import MinecraftServer
import requests
from PIL import Image, ImageDraw

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'MC Outpost'
        self.left = 1000
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # move to center screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.statusBar().showMessage('Message in statusbar.')

        button = QPushButton('PyQt5 button', self)
        button.setToolTip('This is an example button')
        button.move(100,70)
        button.clicked.connect(self.on_click)

        # buttonReply = QMessageBox.question(self, 'PyQt5 message', "Do you like PyQt5?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # if buttonReply == QMessageBox.Yes:
        #     print('Yes clicked.')
        # else:
        #     print('No clicked.')

        self.show()

    @pyqtSlot()
    def on_click(self):
        print('PyQt5 button click')

# import subprocess
# # import paramiko
# import socket
# import time
# from playsound import playsound
# import multiprocessing
# import os
# from mcstatus import MinecraftServer
# import requests
# from PIL import Image, ImageDraw

# CHECK_INTERVAL = 5
# DOWN_DELAY = 60

# def main():
#     server = MinecraftServer("199.27.248.104", 10240)
#     status = None
#     ack = False
#     response = True
#     label = "SYSTEM ONLINE"

#     downTime = 0
#     previousUserCount = 0

#     while (True):
#         if (int(time.time() % CHECK_INTERVAL) == 0):
#             try:
#                 status = server.status()
#                 response = True
#                 ack = False
#                 label = "SYSTEM ONLINE"
#             except Exception:
#                 try:
#                     requests.get("https://www.google.com/")
#                     if response:
#                         response = False
#                         downTime = time.time()
#                         label = "!" + " SYSTEM OFFLINE " + "!"
#                 except requests.ConnectionError:
#                     label = "-" + " CONNECTIVITY FAILURE " + "-"
#                     status = None

#         os.system("cls")
#         print("{0} | Checking in: {1}s\nAcknoledged: {2}".format(label, int(CHECK_INTERVAL - time.time() % CHECK_INTERVAL), ack))
#         if (response and status):
#             print("\n{0} players online | {1} ms response time".format(status.players.online, status.latency))
#             if (status.players.online > previousUserCount):
#                 playsound("C:/Users/Gman/Desktop/WORK/sfx/Beeps/server_new_user.mp3")
#             elif (status.players.online < previousUserCount):
#                 playsound("C:/Users/Gman/Desktop/WORK/sfx/Clicks/server_lost_user.mp3")
#             previousUserCount = status.players.online

#             if (status.players.sample):
#                 for player in status.players.sample:
#                     print("> {}".format(player.name))
#         time.sleep(1)

#         if not response and not ack:
#             if (time.time() - downTime > DOWN_DELAY):
#                 ack = True
#                 alarm = multiprocessing.Process(target=alert, args=())
#                 alarm.start()
#                 input("\nAcknoledge: ")
#                 alarm.terminate()


# def alert():
#     while (True):
#         playsound("C:/Users/Gman/Desktop/WORK/sfx/Beeps/server_alarm.mp3")
#         time.sleep(1)
    
if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())



# if __name__ == "__main__":
#     main()