import socket
import time
import datetime
from threading import *
import os
from mcstatus import MinecraftServer
import requests
import socket
import json
from dotenv import load_dotenv
from faker import Factory

fake = Factory.create()
load_dotenv()

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 10230        # Port to listen on (non-privileged ports are > 1023)

CHECK_INTERVAL = 5
DOWN_DELAY = 60

class User:
    def __init__(self, name, session, color):
        self.name = name
        self.session = session
        self.color = color

class Session:
    def __init__(self, author, start_time):
        self.id = time.time()
        self.author = author
        self.color = author.color
        self.start_time = start_time
        self.end_time = None

activeSessions = []


def main():
    try:
        int(os.getenv("SERVER_PORT"))
    except Exception as e:
        print("ERROR: SERVER PORT NOT INTEGER")
        return
        
    server = MinecraftServer(os.getenv("SERVER_IP"), int(os.getenv("SERVER_PORT")))
    status = None
    ack = False
    response = True
    label = "SYSTEM ONLINE"

    downTime = 0
    previousUsers = []

    listenerThread = Thread(target=runListener, daemon=True)
    listenerThread.start()

    while (True):
        if (round(time.time(), 1) % CHECK_INTERVAL) == 0:
            try:
                status = server.status()
                response = True
                ack = False
                label = "SYSTEM ONLINE"
            except Exception:
                try:
                    requests.get("https://www.google.com/")
                    if response:
                        response = False
                        label = "!" + " SYSTEM OFFLINE " + "!"
                except requests.ConnectionError:
                    label = "-" + " CONNECTIVITY FAILURE " + "-"
                    status = None

        os.system("cls")
        print("{0} | Checking in: {1}s".format(label, int(CHECK_INTERVAL - time.time() % CHECK_INTERVAL)))
        if (response and status):
            print("\n{0} players online | {1} ms response time".format(status.players.online, status.latency))
            # GAINED A USER
            if (status.players.online > len(previousUsers)):

                # if user is not in previous users
                # add them to previous users with new session
                # add new session to activeSessions

                if (status.players.sample):
                    for player in status.players.sample:
                        found = False
                        for user in previousUsers:
                            if (player.name == user.name):
                                found = True
                                break
                        if not found:
                            print("NEW SESSION: " + player.name)
                            # Create session, create user, add user to session, add to arrays
                            newUser = User(player.name, None, getUserColor(player.name))
                            newSession = Session(newUser, datetime.datetime.now())
                            newUser.session = newSession


                            activeSessions.append(newSession)
                            previousUsers.append(newUser)

            # LOST A USER
            if (status.players.online < len(previousUsers)):

                # if previous user is not in current users
                # remove them from previous users
                # add end_time to user's session

                for user in previousUsers:
                    found = False
                    if (status.players.sample):
                        for player in status.players.sample:
                            if (player.name == user.name):
                                found = True
                                break
                    if not found:
                        print("CLOSED SESSION: " + player.name)
                        # End session, remove user from previous users, remove session from active activeSessions
                        user.session.end_time = datetime.datetime.now()
                        saveSession(user.session)
                        activeSessions.remove(user.session)
                        previousUsers.remove(user)
                        break
            
        time.sleep(0.99)


def saveSession(session):
    try:
        fileRead = open("sessions.json", "r")
        store = json.load(fileRead)
        fileRead.close()
    except Exception as e:
        store = {}

    with open("sessions.json", "w") as file:

        serializable_data = {
            'author': session.author.name,
            'color': session.color,
            'start_time': str(session.start_time),
            'end_time': str(session.end_time)
        }

        store[session.id] = serializable_data
        json.dump(store, file, indent=4)


def getUserColor(username):
    # Try to get user's hex color from sessions
    # If not found, return a random one
    try:
        fileRead = open("sessions.json", "r")
        store = json.load(fileRead)
        fileRead.close()
    except Exception as e:
        return fake.hex_color()

    for session in store:
        if (store[session]['author'] == username):
            return store[session]['color']
    return fake.hex_color()


def runListener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                store = bytes(str(getAllSessions()), "utf-8")
                conn.sendall(store)


def getAllSessions():
    fileRead = open("sessions.json", "r")
    sessions = json.load(fileRead)
    fileRead.close()

    for session in activeSessions:
        serializable_data = {
            'author': session.author.name,
            'start_time': str(session.start_time),
            'end_time': str(session.end_time)
        }
        sessions[session.id] = serializable_data

    return sessions

if __name__ == "__main__":
    main()