# 🚀 AWS Deployment Guide - Grace Music Bot

**Complete step-by-step guide for deploying Grace Music on AWS EC2**

---

## 📋 Table of Contents
1. [EC2 Instance Setup](#ec2-instance-setup)
2. [Security Configuration](#security-configuration)
3. [Environment Setup](#environment-setup)
4. [Installation Steps](#installation-steps)
5. [Service Configuration](#service-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Scaling & Optimization](#scaling--optimization)

---

## EC2 Instance Setup

### Step 1: Launch EC2 Instance

**AWS Console Steps:**

1. Go to EC2 Dashboard → Instances
2. Click "Launch Instances"
3. **Name**: `grace-music-bot`
4. **AMI**: Ubuntu 24.04 LTS (Free tier eligible)
5. **Instance Type**: `t3.small` (recommended)
   - 2 vCPU
   - 2 GB RAM
   - EBS optimized
6. **Key Pair**: Create new or use existing
7. **Storage**: 20 GB (General Purpose SSD)

### Step 2: Allocate Elastic IP (Optional but Recommended)

```bash
# In AWS Console:
1. EC2 Dashboard → Elastic IPs
2. Click "Allocate Elastic IP address"
3. Associate with your instance
4. Copy IP for your DNS records
```

### Step 3: Connect to Instance

```bash
# SSH Connection
ssh -i your-key.pem ubuntu@your-elastic-ip

# Verify connection
whoami  # Should show: ubuntu
pwd     # Should show: /home/ubuntu
```

---

## Security Configuration

### Step 1: Update Security Group

**AWS Console:**
```
1. Go to Security Groups
2. Select your instance's security group
3. Edit Inbound Rules:
   - SSH (port 22): Restrict to your IP
   - HTTP (port 8000): Allow 0.0.0.0/0
   - HTTPS (port 443): Optional
```

### Step 2: Harden SSH (On EC2)

```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update System
sudo apt update && sudo apt upgrade -y

# Configure SSH
sudo nano /etc/ssh/sshd_config
# Change: PermitRootLogin no
# Change: PasswordAuthentication no
# Save and exit

sudo systemctl restart ssh
```

### Step 3: Configure Firewall

```bash
# Enable UFW
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 8000/tcp # Health check
sudo ufw allow 443/tcp  # HTTPS (optional)
```

---

## Environment Setup

### Step 1: Install System Dependencies

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    ffmpeg \
    ffprobe \
    git \
    curl \
    wget \
    nano \
    build-essential \
    libssl-dev

# Verify installations
python3.12 --version
ffmpeg -version
git --version
```

### Step 2: Install MongoDB (Local or use Atlas)

**Option A: Local MongoDB**
```bash
# Install MongoDB
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
mongo --version
```

**Option B: MongoDB Atlas (Cloud)**
```bash
# Use your MongoDB Atlas connection string in .env
# Format: mongodb+srv://username:password@cluster.mongodb.net/database
```

### Step 3: Create Application Directory

```bash
# Create app directory
mkdir -p ~/grace-music-bot
cd ~/grace-music-bot

# Create Python virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify venv
which python  # Should show: ~/grace-music-bot/venv/bin/python
python --version
```

---

## Installation Steps

### Step 1: Clone Repository

```bash
# Clone repo
git clone https://github.com/elevenyts/Elevenytsmusic.git .

# Verify directory
ls -la  # Should show: GraceMusic/, requirements.txt, .env, etc.
```

### Step 2: Install Python Dependencies

```bash
# Activate venv if not already
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Verify key packages
python -c "import pyrogram; print('✓ Pyrogram OK')"
python -c "import pytgcalls; print('✓ PyTgCalls OK')"
python -c "import pymongo; print('✓ PyMongo OK')"
```

### Step 3: Configure Environment Variables

```bash
# Create .env file
nano .env

# Add these variables:
```

```bash
# Telegram API Credentials
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Database
MONGO_URL=mongodb://localhost:27017/gracemusic
# Or for Atlas: mongodb+srv://username:password@cluster.mongodb.net/database

# Logging
LOGGER_ID=your_logger_channel_id

# Users
SUDO_USERS=your_telegram_id

# Images
START_IMG=https://files.catbox.moe/ieoh4h.png
DEFAULT_THUMB=https://files.catbox.moe/ieoh4h.png
RADIO_IMG=https://files.catbox.moe/ieoh4h.png

# Configuration
QUEUE_LIMIT=50
AUTO_LEAVE_TIMER=900

# AWS (Optional)
AWS_ACCESS_KEY=
AWS_SECRET_KEY=

# Support Links
SUPPORT_CHANNEL=https://t.me/gracemusicin
SUPPORT_CHAT=https://t.me/gracemusicchat
```

**Save**: Ctrl+O, Enter, Ctrl+X

### Step 4: Generate Session Strings

```bash
# Create session generation script
python << 'EOF'
from pyrogram import Client

# Main bot session
client = Client(
    "grace_music",
    api_id=123456,  # Your API_ID
    api_hash="your_api_hash",
    bot_token="your_bot_token"
)

print("Session string generated!")
EOF

# Copy the session string to .env as SESSION_NAME
```

### Step 5: Test Run

```bash
# Activate venv
source venv/bin/activate

# Run bot
python -m GraceMusic

# Expected output:
# [INFO] - GraceMusic: 🎉 Bot started successfully!
# [INFO] - GraceMusic: 🔌 Loaded 34 plugin modules.
# [INFO] - GraceMusic: 👑 Loaded 1 sudo users.

# Press Ctrl+C to stop
```

---

## Service Configuration

### Step 1: Create systemd Service File

```bash
# Create service file
sudo nano /etc/systemd/system/grace-music.service
```

**Paste this content:**

```ini
[Unit]
Description=Grace Music Bot - Telegram Music Streaming Bot
After=network.target mongod.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/grace-music-bot
Environment="PATH=/home/ubuntu/grace-music-bot/venv/bin"
EnvironmentFile=/home/ubuntu/grace-music-bot/.env
ExecStart=/home/ubuntu/grace-music-bot/venv/bin/python -m GraceMusic

# Restart policy
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

**Save**: Ctrl+O, Enter, Ctrl+X

### Step 2: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service on boot
sudo systemctl enable grace-music

# Start service
sudo systemctl start grace-music

# Check status
sudo systemctl status grace-music

# View logs
journalctl -u grace-music -f  # Real-time logs
journalctl -u grace-music -n 100  # Last 100 lines
```

### Step 3: Verify Service

```bash
# Check if bot is running
systemctl is-active grace-music

# Check health endpoint
curl http://localhost:8000

# Should show: {"status": "ok"} or similar

# Check bot startup logs
journalctl -u grace-music --since "5 minutes ago"
```

---

## Monitoring & Maintenance

### Step 1: Monitor Bot Status

```bash
# Real-time monitoring
watch -n 5 'systemctl status grace-music'

# CPU and memory usage
ps aux | grep "[p]ython -m GraceMusic"

# Open files and connections
lsof -p $(pgrep -f "python -m GraceMusic")

# Network connections
netstat -an | grep ESTABLISHED | wc -l
```

### Step 2: Backup Configuration

```bash
# Backup .env file
cp .env .env.backup
sudo chown ubuntu:ubuntu .env.backup
chmod 600 .env.backup

# Backup database
mongodump --out ~/mongodb_backup/$(date +%Y%m%d)

# Or for Atlas, use their backup features
```

### Step 3: Manage Logs

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/grace-music
```

```
/var/log/grace-music.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
}
```

### Step 4: Troubleshooting Commands

```bash
# View recent errors
journalctl -u grace-music -p err

# Check database connection
python << 'EOF'
import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")
print("Database connection: OK")
EOF

# Test Telegram connection
python << 'EOF'
import requests
r = requests.get("https://api.telegram.org/botTOKEN/getMe")
print("Telegram connection: OK") if r.status_code == 200 else print(f"Error: {r.status_code}")
EOF

# Restart service
sudo systemctl restart grace-music

# Stop service
sudo systemctl stop grace-music

# View more logs
sudo journalctl -u grace-music -n 500 --no-pager > logs.txt
```

---

## Scaling & Optimization

### Step 1: Enable Auto-Scaling (Optional)

```bash
# Create CloudWatch alarm
aws cloudwatch put-metric-alarm \
    --alarm-name grace-music-cpu \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold

# Create launch template
aws ec2 create-launch-template \
    --launch-template-name grace-music-template \
    --version-description "Grace Music Bot v1.0"
```

### Step 2: Database Optimization

```bash
# Create indexes for faster queries
mongo << 'EOF'
use gracemusic
db.chats.createIndex({ "chat_id": 1 })
db.users.createIndex({ "user_id": 1 })
db.calls.createIndex({ "chat_id": 1 })
EOF

# Monitor database size
du -sh ~/mongodb_backup/
```

### Step 3: Performance Tuning

```bash
# Increase file descriptors
sudo nano /etc/security/limits.conf
# Add: ubuntu soft nofile 65536
# Add: ubuntu hard nofile 65536

# Apply changes
sudo systemctl reboot

# Verify after reboot
ulimit -n  # Should show: 65536
```

---

## Post-Deployment Validation

```bash
# 1. Verify bot responds
curl -X GET http://localhost:8000

# 2. Check all plugins loaded
journalctl -u grace-music | grep "Loaded"

# 3. Test music command
# Send /play rickroll to test group - verify it plays

# 4. Verify auto-delete works
# Send /pause - wait 3 minutes - verify message deleted

# 5. Check health metrics
python << 'EOF'
import requests
r = requests.get("http://localhost:8000/health")
print(f"Status: {r.json()}")
EOF

# 6. Backup and document
echo "Deployment Date: $(date)" > DEPLOYMENT.log
echo "Instance ID: $(ec2-metadata --instance-id)" >> DEPLOYMENT.log
echo "IPv4 Address: $(ec2-metadata --public-ipv4)" >> DEPLOYMENT.log
```

---

## 📞 AWS Support Commands

```bash
# Get instance metadata
ec2-metadata --all

# Get public IP
ec2-metadata --public-ipv4
# or
curl https://checkip.amazonaws.com

# Get instance details
aws ec2 describe-instances --instance-ids <instance-id>

# Monitor costs (AWS CLI)
aws ce get-cost-and-usage \
    --time-period Start=2026-01-01,End=2026-04-01 \
    --granularity MONTHLY \
    --metrics BlendedCost
```

---

## ✅ Final Deployment Checklist

- [ ] EC2 instance launched and running
- [ ] Security groups configured
- [ ] SSH access verified
- [ ] System dependencies installed
- [ ] Python 3.12 environment ready
- [ ] MongoDB running (or Atlas configured)
- [ ] Repository cloned
- [ ] .env file configured with all credentials
- [ ] Session strings generated
- [ ] Requirements installed
- [ ] Local test run successful
- [ ] systemd service file created
- [ ] Service enabled and running
- [ ] Health check endpoint responding
- [ ] Bot logs showing no errors
- [ ] Test group added and music playing
- [ ] Auto-delete working (wait 3 minutes to verify)
- [ ] Backup procedures documented
- [ ] Support contacts saved

---

## 🎉 Deployment Complete!

Your Grace Music bot is now running on AWS EC2 and ready for production use.

**Next Steps:**
1. Invite bot to your group
2. Send `/start` command
3. Add the bot to Telegram groups
4. Test all features
5. Monitor logs regularly
6. Set up automated backups
7. Configure CloudWatch alarms (optional)

**Support**: https://t.me/gracemusicchat

---

**Last Updated**: April 2026  
**AWS Deployment Guide v2.0**  
**Status**: Production Ready ✅
