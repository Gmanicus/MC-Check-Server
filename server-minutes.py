import socket
import time
import datetime
import multiprocessing
import os
from mcstatus import MinecraftServer
import requests
import json
from dotenv import load_dotenv

load_dotenv()

CHECK_INTERVAL = 5
DOWN_DELAY = 60

def main():
    server = MinecraftServer(os.getenv("MC_CHECKSERVER_IP"), 10240)
    status = None
    ack = False
    response = True
    label = "SYSTEM ONLINE"

    downTime = 0
    previousUsers = []
    sessions = []

    while (True):
        if (int(time.time() % CHECK_INTERVAL) == 0):
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
                        downTime = time.time()
                        label = "!" + " SYSTEM OFFLINE " + "!"
                except requests.ConnectionError:
                    label = "-" + " CONNECTIVITY FAILURE " + "-"
                    status = None

        # os.system("cls")
        # print("{0} | Checking in: {1}s".format(label, int(CHECK_INTERVAL - time.time() % CHECK_INTERVAL)))
        if (response and status):
            # print("\n{0} players online | {1} ms response time".format(status.players.online, status.latency))
            # GAINED A USER
            if (status.players.online > len(previousUsers)):

                # if user is not in previous users
                # add them to previous users with new session
                # add new session to sessions

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
                            newSession = Session(None, datetime.datetime.now())
                            newUser = User(player.name, newSession)
                            newSession.author = newUser

                            sessions.append(newSession)
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
                        # End session, remove user from previous users
                        user.session.end_time = datetime.datetime.now()
                        saveSession(user.session)
                        previousUsers.remove(user)
                        break
            
            # if (status.players.sample):
            #     for player in status.players.sample:
            #         print("> {}".format(player.name))
        time.sleep(1)

def saveSession(session):
        #if (DEBUG): return
    try:
        fileRead = open("sessions.json", "r")
        store = json.load(fileRead)
    except Exception as e:
        store = {}

    with open("sessions.json", "w") as file:

        serializable_data = {
            'author': session.author.name,
            'start_time': str(session.start_time),
            'end_time': str(session.end_time)
        }

        store[session.id] = serializable_data
        json.dump(store, file, indent=4)

class User:
    def __init__(self, name, session):
        self.name = name
        self.session = session

class Session:
    def __init__(self, author, start_time):
        self.id = time.time()
        self.author = author
        self.start_time = start_time
        self.end_time = None

if __name__ == "__main__":
    main()