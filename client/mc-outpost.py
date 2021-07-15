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
import traceback

from PyQt5 import QtWidgets, QtWebEngineWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
import GenericInputDialog

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
        self.setFixedSize(700, 420)
        self.initUI()

        self.settingsChanged = False

        statusThread = Thread(target=self.updateStatus, daemon=True)
        statusThread.start()
        
    def initUI(self):
        self.setWindowTitle(self.title)

        self.setWindowIcon(QtGui.QIcon(resource_path("DATA/icon.ico")))

        # move to center screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        edit = QAction('Settings', self)
        edit.triggered.connect(self.settingsUI)
        mainBar = self.menuBar()
        mainBar.addAction(edit)

        self.playerLabel = QLabel(self)
        self.serverLabel = QLabel(self)
        self.playerLabel.move(20, 350)
        self.serverLabel.move(20, 370)
        self.playerLabel.setFixedWidth(660)
        self.serverLabel.setFixedWidth(660)

        self.statusBar().showMessage('Loading...')

        self.plotter = self.PlotWidget(self)

        self.show()

    def settingsUI(self):
        accepted, values = GenericInputDialog.show_dialog("Settings", [
            GenericInputDialog.TextLineInput('Server IP', loadSetting("SERVER_IP")),
            GenericInputDialog.TextLineInput('Server Port', str(loadSetting("SERVER_PORT"))),
            GenericInputDialog.TextLineInput('Server-Minutes Host IP', loadSetting("SERVER_MINUTES_IP")),
            GenericInputDialog.TextLineInput('Server-Minutes Port', str(loadSetting("SERVER_MINUTES_PORT")))])

        if (accepted):
            if not isInteger(values['Server Port']) or not isInteger(values['Server-Minutes Port']):
                self.errorUI('Port must be a number'); return

            saveSetting('SERVER_IP', values['Server IP'])
            saveSetting('SERVER_PORT', int(values['Server Port']))
            saveSetting('SERVER_MINUTES_IP', values['Server-Minutes Host IP'])
            saveSetting('SERVER_MINUTES_PORT', int(values['Server-Minutes Port']))
            self.settingsChanged = True
            self.plotter.genThread.genFigure()

    def errorUI(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.exec_()

    def updateStatus(self):
        server = MinecraftServer(loadSetting("SERVER_IP"), loadSetting("SERVER_PORT"))
        status = None
        response = True
        label = "Loading..."
        started = False

        while (True):
            if (int(time.time() % CHECK_INTERVAL) == 0):
                # Reconnect to the server if our settings changed
                if self.settingsChanged:
                    started = False
                    self.statusBar().showMessage('Reconnecting...')
                    self.settingsChanged = False
                    server = MinecraftServer(loadSetting("SERVER_IP"), loadSetting("SERVER_PORT"))

                try:
                    status = server.status()
                    response = True
                    label = "SERVER ONLINE"
                    if not started:
                        self.statusBar().showMessage('Connected')
                        started = True
                except Exception:
                    try:
                        requests.get("https://www.google.com/")
                        if response:
                            response = False
                            started = False
                            label = "SERVER OFFLINE"
                            self.statusBar().showMessage('Server Offline')
                    except requests.ConnectionError:
                        label = "CONNECTIVITY FAILURE"
                        started = False
                        status = None
                        self.statusBar().showMessage('Connectivity Failure')

                if status:
                    if status.players.sample:
                        playerNames = []
                        for player in status.players.sample:
                            playerNames.append(player.name)
                        self.playerLabel.setText("Players Online: " + ", ".join(playerNames))
                    else:
                        self.playerLabel.setText("No Players Online")

                    self.serverLabel.setText("Server Latency: {}ms".format(int(status.latency)))

    class PlotWidget(QWidget):

        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.setGeometry(0,20,0,0)
            self.browser = QtWebEngineWidgets.QWebEngineView()

            self.vlayout = QVBoxLayout(self)
            self.vlayout.addWidget(self.browser)

            self.resize(700,340)
            self.browser.setFixedSize(680,320)

            self.genThread = self.GenThread(self)
            self.genThread.htmlChanged.connect(self.browser.setHtml)
            self.genThread.labelChanged.connect(self.updateLabel)
            self.genThread.start()

        def updateLabel(self, text):
            print("Updating label to: {}".format(repr(text)))
            self.parent.statusBar().showMessage(text)

        class GenThread(QtCore.QThread):
            htmlChanged = QtCore.pyqtSignal(str)
            labelChanged = QtCore.pyqtSignal(str)

            previousSessions = {}

            # Once every 30s, run genFigure
            def run(self):
                self.genFigure()
                while (True):
                    if (round(time.time(), 1) % 300) == 0:
                        self.genFigure()


            def genFigure(self):
                print("Generating figure...")
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
                print("Updated layout...")

                sessions = self.getSessions()
                if not sessions:
                    self.labelChanged.emit("Unable to Get User Sessions")
                    return

                # If we have no new data, do not refresh the plotter
                if sessions == self.previousSessions:
                    print("No new session data to plot")
                    return
                else:
                    self.labelChanged.emit("New Session Data Plotted")
                    self.previousSessions = sessions

                print("Got sessions")

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

                html = fig.to_html(include_plotlyjs='cdn')
                print("Converted to HTML")
                self.htmlChanged.emit(html)
                print("Set HTML")
    
            def getSessions(self):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.connect((loadSetting("SERVER_MINUTES_IP"), loadSetting("SERVER_MINUTES_PORT")))
                    except Exception as e:
                        return None
                    data = b''
                    while True:
                        newData = s.recv(1024)
                        data += newData
                        if not newData:
                            break
                return BytesToJSON(data)


def BytesToJSON(bytes):
    data = bytes.decode('utf-8').replace("'", '"')
    return json.loads(data)

def saveSetting(setting, value):
    try:
        fileRead = open(resource_path("settings.json"), "r")
        store = json.load(fileRead)
        fileRead.close()
    except Exception as e:
        store = {}

    with open(resource_path("settings.json"), "w") as file:
        store[setting] = value
        json.dump(store, file, indent=4)

def loadSetting(setting):
    try:
        fileRead = open(resource_path("settings.json"), "r")
        store = json.load(fileRead)
        fileRead.close()
    except Exception as e:
        return None
    
    if not setting in store:
        return None

    return store[setting]





def isInteger(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())