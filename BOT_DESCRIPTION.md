# 🎵 Grace Music Bot

**Advanced Telegram Music Streaming Bot** - High-quality audio streaming with professional features for groups and channels.

---

## 🎯 Overview

Grace Music is a premium music player bot for Telegram groups and channels. Stream music with zero lag, high-quality audio, and intuitive controls. Supports YouTube, playlists, live streams, and radio stations.

---

## ✨ Key Features

### 🎵 Music Playback
- **Crystal-clear opus audio** - Studio-quality streaming
- **YouTube support** - Songs, playlists, live streams
- **Queue management** - Up to 50+ songs (configurable)
- **Smart controls** - Play, pause, skip, stop, seek
- **Loop modes** - Off, single track, entire queue
- **Shuffle** - Randomize queue order
- **Force play** - Skip queue and play immediately

### 📻 Advanced Features
- **Radio stations** - 50+ pre-configured stations
- **Channel play** - Stream to linked channels
- **Video support** - Optional video playback (if enabled)
- **Streaming detection** - Supports YouTube live streams
- **Auto-queue** - Queue next songs automatically
- **Seek control** - Jump to specific timestamps
- **Inline player** - Visual controls with buttons

### 🔐 Admin Controls
- **Admin-only mode** - Restrict playing to admins
- **Authorized users** - Let non-admins control playback
- **Auto leave** - Bot leaves after inactivity
- **Broadcast** - Send messages to all groups
- **User blocking** - Prevent specific users
- **Chat blacklist** - Disable bot in specific chats
- **Global ban (G-ban)** - Ban users across all groups

### 📊 Technical Features
- **Zero-lag playback** - Optimized streaming
- **Automatic upscaling** - 10-second anticipation
- **Multi-assistant** - Load distribution across bots
- **Database analytics** - Track usage patterns
- **Health checks** - Automatic monitoring
- **Error recovery** - Graceful error handling
- **Replay function** - Replay current track

### 🌐 Localization
- **Multi-language** - Easy language extension
- **User preferences** - Per-group language settings
- **Professional translations** - Clean, readable text

---

## 📋 Commands

### Play Commands
```
/play [song/url]      - Play song from YouTube
/vplay [song/url]     - Play video (if enabled)
/playforce [song]     - Play immediately (skip queue)
/radio [station]      - Play radio station
/cplay [song]         - Play in linked channel
```

### Playback Control
```
/pause                 - Pause playback
/resume                - Resume playback
/skip                  - Skip to next track
/stop                  - Stop playback and leave
/seek [time]           - Seek to specific time
/seekback [time]       - Seek backward
/seekforward [time]    - Seek forward
```

### Queue Management
```
/queue                 - Show current queue
/shuffle               - Shuffle queue
/loop [mode]           - Set loop mode
  - disable            - Turn off loop
  - single             - Loop current track
  - queue              - Loop entire queue
```

### Admin Commands
```
/reload                - Reload admin cache
/auth [user]           - Add authorized user
/unauth [user]         - Remove authorized user
/authlist              - Show authorized users
/playmode              - Toggle admin-only mode
/channelplay [setup]   - Configure channel streaming
/maintenance [on/off]  - Toggle maintenance mode
```

### Information
```
/start                 - Start and welcome
/help                  - Show help menu
/ping                  - Bot status and latency
/stats                 - Bot statistics
/active                - Active calls count
/activevc              - List active voice chats
```

### Sudo Commands
```
/broadcast [message]   - Broadcast to all groups
/eval [code]           - Execute Python code
/logs                  - Get bot logs
/restart               - Restart bot
/update                - Update and restart
/leave                 - Leave current chat
/leaveall              - Leave inactive chats
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Telegram Bot Token
- Telegram API credentials (app_id, app_hash)
- MongoDB connection string (optional, local SQLite used as fallback)
- FFmpeg installed
- FFprobe installed

### Quick Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/elevenyts/Elevenytsmusic.git
   cd Elevenytsmusic
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp sample.env .env
   # Edit .env with your credentials
   ```

4. **Run Bot**
   ```bash
   python -m GraceMusic
   ```

---

## ⚙️ Configuration

### Required Environment Variables
```
API_ID=              # Telegram API ID
API_HASH=            # Telegram API Hash
BOT_TOKEN=           # Telegram Bot Token
SUDO_USERS=1234567   # Comma-separated sudo user IDs
```

### Optional Variables
```
MONGO_URL=           # MongoDB connection string
AWS_ACCESS_KEY=      # AWS access key (for DynamoDB)
AWS_SECRET_KEY=      # AWS secret key
LOGGER_ID=           # Logger channel ID for notifications
START_IMG=           # Bot image URL
QUEUE_LIMIT=50       # Maximum queue size
```

### Session Strings
```
SESSION_NAME=        # Pyrogram session for main bot
ASSISTANT_NAMES=     # Additional assistant session names
```

---

## 📊 Performance Specifications

| Metric | Value |
|--------|-------|
| **Database Connection** | ~0.3s (MongoDB) |
| **Bot Startup Time** | ~3-5 seconds |
| **Playback Latency** | <500ms |
| **Queue Limit** | 50 songs (configurable) |
| **Download Limit** | 200MB max |
| **Concurrent Streams** | Unlimited |
| **Active Calls Support** | 100+ simultaneously |

---

## 🛡️ Security Features

- **Rate limiting** - Prevents spam and abuse
- **User blacklisting** - Block specific users
- **Chat blacklisting** - Disable bot in specific groups
- **Global ban system** - Ban users across all groups
- **Admin verification** - Confirms admin permissions
- **Authorized users** - Non-admin playback control
- **Secure database** - Encrypted sessions
- **Error isolation** - Graceful error handling

---

## 🔧 Deployment

### Docker
```bash
docker build -t grace-music .
docker run -d \
  --name grace-music \
  -e API_ID=your_id \
  -e API_HASH=your_hash \
  -e BOT_TOKEN=your_token \
  grace-music
```

### AWS EC2
1. Launch Ubuntu 24.04 instance
2. Install Python 3.12, FFmpeg, MongoDB
3. Clone repository
4. Configure environment variables
5. Run with supervisor or systemd
6. Use port 8000 for health checks (Render-compatible)

### Render/Railway
Application already Render-ready with health check on port 8000.

### Local/VPS
Use systemd service or supervisor for process management.

---

## 📝 Logging

Bot logs are sent to configured logger channel for monitoring:
- New group joins
- User actions
- Errors and warnings
- System events
- Broadcasts

---

## 🤝 Support

- **Support Channel** (https://t.me/gracemusicin)
- **Community Chat** (https://t.me/gracemusicchat)
- **Issue Reports** - Use GitHub issues

---

## 📄 License

[Your License Type] - See LICENSE file for details

---

## 🙏 Credits

- **Pyrogram** - Telegram client library
- **PyTgCalls** - Voice chat integration
- **yt-dlp** - YouTube downloader
- **MongoDB** - Database backend
- **FFmpeg** - Audio processing

---

**Last Updated**: April 2026  
**Version**: 2.0.0  
**Status**: Production Ready ✅
