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
from threading import *
import os
from mcstatus import MinecraftServer
import requests

from PyQt5 import QtWidgets, QtWebEngineWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *

import plotly.graph_objects as go
import pandas as pd

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 10230        # The port used by the server
CHECK_INTERVAL = 5

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'MC Outpost'
        self.left = 1000
        self.top = 100
        self.setFixedSize(700, 480)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        mainBar = self.menuBar()
        edit = QAction('Settings', self)
        mainBar.addAction(edit)

        #self.setGeometry(self.left, self.top, self.width, self.height)

        # move to center screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.statusBar().showMessage('Loading...')

        plotter = self.PlotWidget(self)

        button = QPushButton('Refresh', self)
        button.setToolTip('This is an example button')
        button.move(50,400)
        #button.clicked.connect(plotter.genFigure())

        self.show()

        # statusThread = Thread(target=self.updateStatus, args=self)
        # statusThread.start()

    def updateStatus(self):
        server = MinecraftServer(loadSetting("MC_SERVER_IP"), loadSetting("SERVER_PORT_NUMBER"))
        status = None
        response = True
        label = "SERVER ONLINE"

        while (True):
            if (int(time.time() % CHECK_INTERVAL) == 0):
                try:
                    status = server.status()
                    response = True
                    label = "SERVER ONLINE"
                except Exception:
                    try:
                        requests.get("https://www.google.com/")
                        if response:
                            response = False
                            label = "!" + " SERVER OFFLINE " + "!"
                    except requests.ConnectionError:
                        label = "-" + " CONNECTIVITY FAILURE " + "-"
                        status = None

            self.statusBar().showMessage(label)

    class PlotWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setGeometry(0,20,0,0)
            self.button = QPushButton('Plot', self)
            self.hello = QPushButton('Hello World', self)
            self.browser = QtWebEngineWidgets.QWebEngineView(self)

            vlayout = QVBoxLayout(self)
            vlayout.addWidget(self.button, alignment=QtCore.Qt.AlignHCenter)
            vlayout.addWidget(self.hello, alignment=QtCore.Qt.AlignHCenter)
            vlayout.addWidget(self.browser)

            self.genFigure()

            # self.button.clicked.connect(self.genFigure)
            self.resize(700,340)

        def genFigure(self):
            daysAgo = datetime.now() - timedelta(3)

            # dates = []
            # users = []

            # for x in range(0,6):
            #     dates.append( str((weekAgo + timedelta(x)).date) )

            fig = go.Figure() # init the figure

            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(
                    range=[str(daysAgo), str(datetime.now())]
                ),
                paper_bgcolor="LightSteelBlue",
            )

            sessions = self.getSessions()
            seenAuthors = []
            for s in sessions:
                timeLabel = "Hours"
                times = [ sessions[s]['start_time'], sessions[s]['end_time'] ]
                timeDif = datetime.strptime(times[1], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(times[0], '%Y-%m-%d %H:%M:%S.%f')

                timeMarks = []
                
                # Add 10:00 PM to 12:00 AM labels to list to be put on hovertext
                # Remove first letter if it is a leading zero
                d = datetime.strptime(times[0], "%Y-%m-%d %H:%M:%S.%f")
                text = d.strftime("%I:%M %p")
                if (text[0] == "0"): text = text[1:]

                timeMarks.append(text)

                d = datetime.strptime(times[1], "%Y-%m-%d %H:%M:%S.%f")
                text = d.strftime("%I:%M %p")
                if (text[0] == "0"): text = text[1:]

                timeMarks.append(text)

                if (timeDif.seconds > 3600):
                    timeDif = round(timeDif.seconds / 3600, 1)
                else:
                    timeLabel = "Minutes"
                    timeDif = round(timeDif.seconds / 60, 1)

                fig.add_trace(go.Scatter(x=times, y=[sessions[s]['author'], sessions[s]['author']],
                                        marker_color=sessions[s]['color'],
                                        legendgroup=sessions[s]['author'],
                                        name=sessions[s]['author'],
                                        mode='lines',
                                        hovertemplate='{0}<br>{1} {2}<br>{3} to {4}<extra></extra>'.format(
                                                                            sessions[s]['author'],
                                                                            timeDif,
                                                                            timeLabel,
                                                                            timeMarks[0],
                                                                            timeMarks[1]
                                                                            ),
                                        orientation='h',
                                        showlegend=(sessions[s]['author'] not in seenAuthors) # show legend if this is the first time we've seen this author
                            ))

                seenAuthors.append(sessions[s]['author']) # Add author to seen authors

            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
    
        def getSessions(self):
            # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #     s.connect((HOST, PORT))
            #     data = b''
            #     while True:
            #         newData = s.recv(1024)
            #         data += newData
            #         if not newData:
            #             break
            # print("Received: {}".format(BytesToJSON(data)))
            # return BytesToJSON(data)
            return json.load(open('sessions.json', 'r'))


def BytesToJSON(bytes):
    data = bytes.decode('utf-8').replace("'", '"')
    return json.loads(data)

def saveSetting(setting, value):
    try:
        fileRead = open("sessions.json", "r")
        store = json.load(fileRead)
        fileRead.close()
    except Exception as e:
        store = {}

    with open("settings.json", "w") as file:
        store[setting] = value
        json.dump(store, file, indent=4)

def loadSetting(setting):
    try:
        fileRead = open("settings.json", "r")
        store = json.load(fileRead)
        fileRead.close()
    except Exception as e:
        return None
    return store[setting]




if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

    # genFigure()



# if __name__ == "__main__":
#     main()