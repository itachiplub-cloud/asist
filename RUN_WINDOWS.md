# Windows Terminal Setup Guide

## Prerequisites
- Python 3.12+ ([download](https://python.org/downloads))
- MongoDB ([download](https://www.mongodb.com/try/download/community))
- Git ([download](https://git-scm.com/download/win))

## 1. Install MongoDB (Windows)

### Option A: MongoDB Community Server
1. Download and run the MSI installer
2. Choose "Complete" setup
3. Install MongoDB Compass (GUI) when prompted
4. MongoDB will run as a Windows service automatically

### Option B: MongoDB Atlas (cloud, no install)
1. Create free cluster at https://cloud.mongodb.com
2. Get your connection string (MONGO_URI)

## 2. Clone & Setup

```powershell
# Clone the repo
git clone https://github.com/itachiplub-cloud/asist.git
cd asist

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Get Your Telegram Credentials

### Get API_ID and API_HASH
1. Go to https://my.telegram.org/apps
2. Login with your phone number
3. Create an application
4. Copy `api_id` and `api_hash`

### Generate String Session
```powershell
# Run the session generator
python -c "
from pyrogram import Client
with Client('session_gen', api_id=YOUR_API_ID, api_hash='YOUR_API_HASH') as app:
    print('STRING_SESSION:', app.export_session_string())
"
```
- Enter your phone number and the verification code
- Copy the printed `STRING_SESSION`

## 4. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```powershell
copy .env.example .env
```

Edit `.env` with Notepad or VS Code:
```ini
API_ID=12345
API_HASH=your_api_hash
STRING_SESSION=your_string_session
OWNER_ID=your_telegram_id
MONGO_URI=mongodb://localhost:27017
```

## 5. Run the Bot

```powershell
# Make sure your venv is activated
.\venv\Scripts\activate

# Run the bot
python bot.py

# Run the API server (optional, second terminal)
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

## 6. Run as a Windows Service (optional)

### Using NSSM (Non-Sucking Service Manager)
1. Download NSSM from https://nssm.cc/download
2. Extract `nssm.exe` to your project folder
3. Run as Administrator:

```powershell
# Install as service
.\nssm.exe install AsistBot

# In the GUI that opens:
#   Path: C:\path\to\asist\venv\Scripts\python.exe
#   Arguments: bot.py
#   Startup directory: C:\path\to\asist
#
# Click "Install service"
```

### Using Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When the computer starts"
4. Action: Start a program
5. Program: `C:\path\to\asist\venv\Scripts\python.exe`
6. Arguments: `bot.py`
7. Start in: `C:\path\to\asist`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `pymongo` connection error | Start MongoDB: `net start MongoDB` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `FloodWait` errors | Increase `COOLDOWN_MIN` in `.env` |
| Session expired | Regenerate string session and update `.env` |

## Quick Start (Paste-friendly)

```powershell
git clone https://github.com/itachiplub-cloud/asist.git
cd asist
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your credentials
python bot.py
```
