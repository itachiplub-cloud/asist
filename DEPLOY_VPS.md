# VPS Deployment Guide

## Prerequisites
- Ubuntu 22.04+ or Debian 12+
- Docker & Docker Compose (recommended)
- Git

## Option 1: Docker Compose (Recommended)

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

### 2. Clone & Deploy

```bash
git clone https://github.com/itachiplub-cloud/asist.git
cd asist

# Configure
cp .env.example .env
nano .env  # Fill in your credentials

# Start all services
docker compose up -d

# View logs
docker compose logs -f bot

# Stop
docker compose down
```

### 3. Update

```bash
cd asist
git pull
docker compose build bot
docker compose up -d
```

## Option 2: Manual Setup (no Docker)

### 1. Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git mongodb redis-server

# Start services
sudo systemctl start mongodb redis-server
sudo systemctl enable mongodb redis-server
```

### 2. Clone & Setup

```bash
git clone https://github.com/itachiplub-cloud/asist.git
cd asist

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env  # Fill in your credentials
```

### 3. Run with systemd (auto-start)

```bash
sudo nano /etc/systemd/system/asist-bot.service
```

Paste:
```ini
[Unit]
Description=Telegram Assistant Bot
After=network.target mongodb.service redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/asist
ExecStart=/home/ubuntu/asist/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable asist-bot
sudo systemctl start asist-bot
sudo systemctl status asist-bot
```

### 4. Run API Server (optional)

Repeat the systemd steps for the API:

```ini
[Unit]
Description=Asist API Server
After=network.target mongodb.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/asist
ExecStart=/home/ubuntu/asist/venv/bin/uvicorn api.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Option 3: Heroku

### 1. Install Heroku CLI

```bash
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

### 2. Deploy

```bash
heroku create your-bot-name
heroku addons:create mongolab
heroku addons:create heroku-redis

heroku config:set API_ID=12345
heroku config:set API_HASH=your_hash
heroku config:set STRING_SESSION=your_session
heroku config:set OWNER_ID=123456789

git push heroku main

# Scale bot process
heroku ps:scale bot=1
```

## Useful Commands

```bash
# Check logs (Docker)
docker compose logs -f --tail 100 bot

# Check logs (systemd)
sudo journalctl -u asist-bot -f

# Backup
docker exec asist_mongo mongodump --out /data/backup

# Restart
docker compose restart bot
```
