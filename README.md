<p align="center">
  <img width="200" height="200" src="icon.png">
  <h1 align="center">MC Outpost</h1>
</p>
<p align="center">
  A Python server and client application that tracks player session times and server status
</p>
<p align="center">
  <br>
  <br>
  <br>
</p>

# About

MC Outpost provides a session graph and server status panel within the app.
This allows you to view player activity and the server's status on your custom Minecraft server right from the desktop application.

# Setup
### Prerequisites

- Python 3+ installed on server

### Instructions

- Download the repository via [CODE>Download Zip](https://github.com/Gmanicus/MC-Outpost/archive/refs/heads/main.zip) or `git clone https://github.com/Gmanicus/MC-Outpost.git`
- Place the `/server` directory on your server **OR** place `/server/server-minutes.py` on your server and create a `.env` file.
- Set `.env` configuration. SERVER_IP: The IP address that your server jar is running on | SERVER_PORT: The port number that your server jar is listening to
- Run `server-minutes.py`
- Run the MC-Outpost app on any machine
- Set your configuration via the **SETTINGS** button. SERVER_IP: The IP address that your server jar is running on | SERVER_PORT: The port number that your server jar is listening to
