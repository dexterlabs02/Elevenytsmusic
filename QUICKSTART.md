# ⚡ Grace Music Bot - Quick Start Guide

## 🎯 Fastest Way to Get Started

### 1️⃣ Prerequisites
- Python 3.10+
- FFmpeg
- Bot token from [@BotFather](https://t.me/BotFather)
- Telegram credentials

### 2️⃣ Clone & Setup

```bash
# Clone repository
git clone https://github.com/gracemusic/GraceMusic.git
cd GraceMusic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure Environment

```bash
# Copy sample configuration
cp sample.env .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

**Essential .env variables:**
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
OWNER_ID=your_user_id
LOGGER_ID=-1001234567890

# Choose Database (MongoDB or DynamoDB)

# ⚙️ Option A: MongoDB
MONGO_DB_URI=mongodb+srv://user:pass@cluster.mongodb.net/gracemusicdb

# ⚙️ Option B: DynamoDB (AWS)
USE_DYNAMODB=True
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Userbot Session
STRING_SESSION=your_session_string
```

### 4️⃣ Get Credentials

#### Telegram API Credentials
1. Visit https://my.telegram.org
2. Login with your account
3. Go to **API Development**
4. Create new application
5. Copy **API ID** and **API Hash**

#### Bot Token
1. Message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow instructions
4. Copy bot token

#### Your User ID
1. Message [@userinfobot](https://t.me/userinfobot)
2. It will show your ID

#### Log Channel ID
```bash
# Create a private channel, then:
# Send a message to the channel
# Forward it to @messageIDbot
# It shows: in_reply_to_message_id: xxxxx
# Your channel ID is: -100xxxxx
```

#### Userbot Session String
1. Message [@StringFatherBot](https://t.me/StringFatherBot)
2. Login with your account when prompted
3. Copy the session string

### 5️⃣ Start the Bot

```bash
# Install FFmpeg (if not already installed)
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS
# Windows: Download from https://ffmpeg.org/download.html

# Run the bot
python -m GraceMusic

# Or start in background
nohup python -m GraceMusic > bot.log &
```

### 6️⃣ Verify It's Running
- Bot should be online on Telegram
- Send `/start` to the bot
- It should respond

---

## 📊 Database Setup

### MongoDB (Easiest)
1. Go to https://cloud.mongodb.com
2. Create free account
3. Create cluster
4. Get connection string
5. Add to `.env` as `MONGO_DB_URI`

### DynamoDB (AWS)
Complete guide: See [DYNAMODB_SETUP.md](DYNAMODB_SETUP.md)

Quick setup:
1. Create AWS account
2. Create IAM user with DynamoDB access
3. Get access keys
4. Add to `.env`:
   ```env
   USE_DYNAMODB=True
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_REGION=us-east-1
   ```
5. Run bot (tables auto-create)

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  gracemusic:
    build: .
    container_name: grace-music-bot
    environment:
      - API_ID=${API_ID}
      - API_HASH=${API_HASH}
      - BOT_TOKEN=${BOT_TOKEN}
      - OWNER_ID=${OWNER_ID}
      - LOGGER_ID=${LOGGER_ID}
      - MONGO_DB_URI=${MONGO_DB_URI}
      - STRING_SESSION=${STRING_SESSION}
    volumes:
      - ./cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - gracemusic

networks:
  gracemusic:
    driver: bridge
EOF

# Deploy
docker-compose up -d

# View logs
docker-compose logs -f gracemusic
```

### Using Docker

```bash
# Build image
docker build -t gracemusic .

# Run container
docker run -d \
  --name gracemusic \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_token \
  -e OWNER_ID=your_id \
  -e MONGO_DB_URI=your_mongo_uri \
  gracemusic

# View logs
docker logs -f gracemusic
```

---

## 🔧 Troubleshooting

### Bot offline / won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list | grep pyrogram

# View detailed logs
python -m GraceMusic 2>&1 | tee bot.log
```

### Missing credentials error
```
Error: Missing required environment variables
Solution: Check all required variables in .env are set
```

### Database connection failed
```
# MongoDB
- Verify connection string format
- Check IP whitelist in MongoDB Atlas
- Ensure network access is allowed

# DynamoDB
- Verify AWS credentials
- Check IAM permissions (need DynamoDBFullAccess)
- Verify region is correct
```

### Bot commands not working
```bash
# Restart bot
pkill -f "python -m GraceMusic"
python -m GraceMusic

# Check logs
tail -f bot.log
```

---

## 📡 Deployment Options

### Local Machine
- Simplest for testing
- Requires constant connection
- Use `nohup` or `screen` for background

### Cloud VPS (Recommended)
- AWS EC2
- Linode
- DigitalOcean
- Hetzner

```bash
# SSH into server
ssh user@server_ip

# Follow setup steps above
```

### Docker/Kubernetes
- Scalable
- Easy management
- Use docker-compose.yml provided

### Heroku / Railway / Render
- Free tier available
- Automatic deployments
- Limited resources

---

## 📚 Useful Commands

```bash
# View bot processes
ps aux | grep GraceMusic

# Kill bot gracefully
pkill -f "python -m GraceMusic"

# View real-time logs
tail -f bot.log

# Generate new session string
python -c "from pyrogram import Client; Client('sessions')"

# Check database connection
python -c "from config import Config; c = Config(); print(c.MONGO_URL[:20]+'...' if c.MONGO_URL else 'Not set')"
```

---

## 🆘 Need Help?

- **Documentation**: See README.md and docs folder
- **Issues**: GitHub Issues
- **Telegram Support**: [@gracemusicchat](https://t.me/gracemusicchat)
- **Database Help**: 
  - MongoDB: https://docs.mongodb.com
  - DynamoDB: https://docs.aws.amazon.com/dynamodb/

---

## 🚀 Next Steps

1. ✅ Deploy bot
2. ✅ Test basic commands (`/start`, `/ping`, `/help`)
3. ✅ Join test group and play music
4. ✅ Configure admin features
5. ✅ Set up analytics/broadcasting (see docs)
6. ✅ Monitor logs and performance

---

## 📝 Notes

- **Credentials Security**: Never share .env file or credentials
- **Backups**: Regularly backup database
- **Updates**: Keep dependencies updated (`pip install --upgrade -r requirements.txt`)
- **Logs**: Monitor bot.log for errors
- **Support**: Join [@gracemusicchat](https://t.me/gracemusicchat) for help

---

**Last Updated**: April 2024
**Grace Music Bot v2.0**
