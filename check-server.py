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

from PyQt5 import QtWidgets, QtWebEngineWidgets, QtGui, QtCore

import plotly.graph_objects as go
import pandas as pd

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 10230        # The port used by the server

class App(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'MC Outpost'
        self.left = 1000
        self.top = 100
        self.setFixedSize(700, 480)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)

        # move to center screen
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.statusBar().showMessage('Message in statusbar.')

        plotter = self.PlotWidget(self)

        button = QtWidgets.QPushButton('Refresh', self)
        button.setToolTip('This is an example button')
        button.move(50,400)
        #button.clicked.connect(plotter.genFigure())

        self.show()

    class PlotWidget(QtWidgets.QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.button = QtWidgets.QPushButton('Plot', self)
            self.hello = QtWidgets.QPushButton('Hello World', self)
            self.browser = QtWebEngineWidgets.QWebEngineView(self)

            vlayout = QtWidgets.QVBoxLayout(self)
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




if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

    # genFigure()



# if __name__ == "__main__":
#     main()