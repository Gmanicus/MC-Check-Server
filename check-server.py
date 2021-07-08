import json
import sys
import logging
import threading
import time
from datetime import datetime, timedelta

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

import plotly.graph_objects as go
import pandas as pd

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 10230        # The port used by the server

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

        button = QPushButton('Refresh', self)
        button.setToolTip('This is an example button')
        button.move(50,400)
        button.clicked.connect(self.getSessions)

        # buttonReply = QMessageBox.question(self, 'PyQt5 message', "Do you like PyQt5?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # if buttonReply == QMessageBox.Yes:
        #     print('Yes clicked.')
        # else:
        #     print('No clicked.')

        self.show()
    
def getSessions():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        data = b''
        while True:
            newData = s.recv(1024)
            data += newData
            if not newData:
                break
    print("Received: {}".format(BytesToJSON(data)))
    return BytesToJSON(data)


def BytesToJSON(bytes):
    data = bytes.decode('utf-8').replace("'", '"')
    return json.loads(data)




def genFigure():
    weekAgo = datetime.now() - timedelta(7)

    dates = []
    users = []

    for x in range(0,6):
        dates.append( str((weekAgo + timedelta(x)).date) )

    fig = go.Figure() # init the figure

    sessions = getSessions()
    seenAuthors = []
    for s in sessions:
        timeLabel = "Hours"
        times = [ sessions[s]['start_time'], sessions[s]['end_time'] ]
        timeDif = datetime.strptime(times[1], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(times[0], '%Y-%m-%d %H:%M:%S.%f')

        if (timeDif.seconds > 3600):
            timeDif = round(timeDif.seconds / 3600, 1)
        else:
            timeLabel = "Minutes"
            timeDif = round(timeDif.seconds / 60, 1)

        fig.add_trace(go.Scatter(x=times, y=[sessions[s]['author'], sessions[s]['author']],
                                marker_color='crimson',
                                legendgroup=sessions[s]['author'],
                                name=sessions[s]['author'],
                                mode='lines',
                                hovertemplate='{0} {1}<br>{2}'.format(timeDif, timeLabel, sessions[s]['author']),
                                orientation='h',
                                showlegend=(sessions[s]['author'] not in seenAuthors) # show legend if this is the first time we've seen this author
                    ))

        seenAuthors.append(sessions[s]['author']) # Add author to seen authors

    fig.show()




if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    # app = QApplication(sys.argv)
    # ex = App()
    # sys.exit(app.exec_())

    genFigure()



# if __name__ == "__main__":
#     main()