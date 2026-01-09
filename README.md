# Mermes — Network Traffic Generator

Mermes is a desktop application for generating network traffic using multiple protocols.  
The application provides a graphical interface for configuring traffic parameters, managing profiles means or and observing real-time load statistics.

The project is focused on combining asynchronous networking with a Qt-based GUI.

---

## Features

- Traffic generation using multiple protocols
- Supported protocols:
  - TCP
  - UDP
  - HTTP
  - TLS
  - WebSocket
- Multi-client simulation
- Real-time traffic chart
- Static and dynamic profiles
- User-defined profile storage

---

## Profiles

### Static Profiles
Static profiles use fixed parameters:
- Protocol
- Target / address
- Port
- Request rate
- Number of clients

### Dynamic Profiles
Dynamic profiles update parameters automatically:
- Randomized request rate
- Randomized client count
- Configurable update interval

This allows simulation of fluctuating network load.

---

## User Interface

The GUI allows:
- Selecting and managing profiles
- Configuring protocol and connection parameters
- Starting and stopping traffic generation
- Monitoring live traffic statistics via a chart

Profiles can be created, edited, and removed from within the application and are stored persistently.

---

## Technical Overview

- Language: Python 3
- GUI framework: PySide6 (Qt6)
- Concurrency model: QThread with a dedicated asyncio event loop
- Networking: Asynchronous protocol clients
- Visualization: Embedded real-time charts
- Packaging: PyInstaller

---

## Running the Application
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
---

## Building an Executable
```
pyinstaller --onefile --windowed main.py
```

---

## Intended Use
 - Network traffic simulation
 -  Testing client-side protocol behavior
 -  Studying asynchronous networking patterns
 -  GUI and asyncio integration experiments

---

## Disclaimer

**This software is intended for testing and educational purposes.
It should only be used on systems and networks where permission has been granted.**

---

## License
**MIT License**

---

**By Limbogeom**
