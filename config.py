from os import getenv
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file (create one from sample.env)
load_dotenv()


class Config:
    """
    Configuration class for managing bot settings.

    All settings are loaded from environment variables with sensible defaults where applicable.
    Required variables are validated on initialization through the check() method.
    """

    def __init__(self):
        """Initialize configuration by loading all environment variables."""

        # ============ TELEGRAM API CREDENTIALS ============
        # Get these from https://my.telegram.org
        # Telegram API ID (numeric)
        self.API_ID: int = int(getenv("API_ID", "0"))
        # Telegram API Hash (hexadecimal)
        self.API_HASH: str = getenv("API_HASH", "")

        # ============ BOT CONFIGURATION ============
        # Bot token from @BotFather
        self.BOT_TOKEN: str = getenv("BOT_TOKEN", "")
        # Group/channel ID for logs (must be negative)
        self.LOGGER_ID: int = int(getenv("LOGGER_ID", "0"))
        # Your user ID (get from @userinfobot)
        self.OWNER_ID: int = int(getenv("OWNER_ID", "0"))

        # ============ DATABASE CONFIGURATION ============
        # MongoDB connection URL (mongodb+srv://...)
        self.MONGO_URL: str = getenv("MONGO_DB_URI", "")

        # DynamoDB Configuration (AWS)
        self.USE_DYNAMODB: bool = self._str_to_bool(getenv("USE_DYNAMODB", "False"))
        self.AWS_ACCESS_KEY_ID: str = getenv("AWS_ACCESS_KEY_ID", "")
        self.AWS_SECRET_ACCESS_KEY: str = getenv("AWS_SECRET_ACCESS_KEY", "")
        self.AWS_REGION: str = getenv("AWS_REGION", "us-east-1")
        
        # DynamoDB Table Names
        self.DYNAMODB_USERS_TABLE: str = getenv("DYNAMODB_USERS_TABLE", "grace_music_users")
        self.DYNAMODB_CHATS_TABLE: str = getenv("DYNAMODB_CHATS_TABLE", "grace_music_chats")
        self.DYNAMODB_BROADCAST_TABLE: str = getenv("DYNAMODB_BROADCAST_TABLE", "grace_music_broadcasts")
        self.DYNAMODB_ANALYTICS_TABLE: str = getenv("DYNAMODB_ANALYTICS_TABLE", "grace_music_analytics")
        self.DYNAMODB_PLAYLIST_TABLE: str = getenv("DYNAMODB_PLAYLIST_TABLE", "grace_music_playlists")

        # Feature Flags for Database
        self.ENABLE_ANALYTICS: bool = self._str_to_bool(getenv("ENABLE_ANALYTICS", "True"))
        self.ENABLE_BROADCAST_DB: bool = self._str_to_bool(getenv("ENABLE_BROADCAST_DB", "True"))

        # ============ MUSIC BOT LIMITS ============
        # Convert minutes to seconds for duration limit
        # Max song duration (default: 300 min)
        self.DURATION_LIMIT: int = int(getenv("DURATION_LIMIT", "300")) * 60
        # Max songs in queue (default: 30)
        self.QUEUE_LIMIT: int = int(getenv("QUEUE_LIMIT", "30"))
        # Max songs from playlist (default: 20)
        self.PLAYLIST_LIMIT: int = int(getenv("PLAYLIST_LIMIT", "20"))

        # ============ ASSISTANT/USERBOT SESSIONS ============
        # Pyrogram session strings - get from @StringFatherBot
        # You can have up to 3 assistants for handling multiple groups
        # Primary assistant (required)
        self.SESSION1: str = getenv("STRING_SESSION", "")
        # Secondary assistant (optional)
        self.SESSION2: str = getenv("STRING_SESSION2", "")
        # Tertiary assistant (optional)
        self.SESSION3: str = getenv("STRING_SESSION3", "")

        # ============ SUPPORT LINKS ============
        self.SUPPORT_CHANNEL: str = getenv(
            "SUPPORT_CHANNEL", "https://t.me/gracemusic")
        self.SUPPORT_CHAT: str = getenv("SUPPORT_CHAT", "https://t.me/gracemusicchat")

        # ============ EXCLUDED CHATS ============
        # Parse comma-separated chat IDs that assistants should never leave
        self.EXCLUDED_CHATS: List[int] = self._parse_excluded_chats()

        # ============ FEATURE FLAGS ============
        # Auto-end stream when queue is empty
        self.AUTO_END: bool = self._str_to_bool(getenv("AUTO_END", "False"))
        # Auto-leave inactive chats
        self.AUTO_LEAVE: bool = self._str_to_bool(getenv("AUTO_LEAVE", "False"))
        # Enable/disable thumbnail generation (set False to use default thumb)
        self.THUMB_GEN: bool = self._str_to_bool(getenv("THUMB_GEN", "True"))

        # ============ API CONFIGURATION ============
        # YouTube API URL for downloading (replaces cookies)
        self.YOUTUBE_API_URL: str = getenv("YOUTUBE_API_URL", "https://shrutibots.site")

        # ============ IMAGE URLS ============
        # URLs for various bot images
        self.DEFAULT_THUMB: str = getenv(
            "DEFAULT_THUMB",
            "https://files.catbox.moe/43u332.jpg"  # Default thumbnail
        )
        self.PING_IMG: str = getenv(
            "PING_IMG", "https://files.catbox.moe/43u332.jpg")    # Ping command image
        self.START_IMG: str = getenv(
            "START_IMG", "https://files.catbox.moe/43u332.jpg")  # Start command image
        self.RADIO_IMG: str = getenv(
            "RADIO_IMG", "https://files.catbox.moe/43u332.jpg")    # Radio command image

        # ============ MODERATION ============
        # List of usernames to exclude from admin mentions
        self.EXCLUDED_USERNAMES: List[str] = getenv("EXCLUDED_USERNAMES", "").split()

    def _parse_excluded_chats(self) -> List[int]:
        """
        Parse excluded chat IDs from comma-separated string.

        Returns:
            List[int]: List of chat IDs to exclude from auto-leave.
        """
        excluded = getenv("EXCLUDED_CHATS", "")
        if not excluded:
            return []

        chat_ids = []
        for chat_id in excluded.split(","):
            chat_id = chat_id.strip()
            if chat_id.lstrip('-').isdigit():
                chat_ids.append(int(chat_id))
        return chat_ids

    @staticmethod
    def _str_to_bool(value: str) -> bool:
        """
        Convert string to boolean value.

        Args:
            value: String representation of boolean.

        Returns:
            bool: Converted boolean value.
        """
        return value.lower() in ("true", "1", "yes", "y", "on")

    def check(self) -> None:
        """
        Validate that all required environment variables are set.

        Raises:
            SystemExit: If any required variables are missing.
        """
        required_vars = {
            "API_ID": self.API_ID,
            "API_HASH": self.API_HASH,
            "BOT_TOKEN": self.BOT_TOKEN,
            "LOGGER_ID": self.LOGGER_ID,
            "OWNER_ID": self.OWNER_ID,
            "STRING_SESSION": self.SESSION1,
        }

        # Database requirement: Either MongoDB or DynamoDB must be configured
        if not self.MONGO_URL and not self.USE_DYNAMODB:
            required_vars["DATABASE"] = None  # Will be marked as missing

        # DynamoDB-specific requirements
        if self.USE_DYNAMODB:
            dynamodb_vars = {
                "AWS_ACCESS_KEY_ID": self.AWS_ACCESS_KEY_ID,
                "AWS_SECRET_ACCESS_KEY": self.AWS_SECRET_ACCESS_KEY,
            }
            required_vars.update(dynamodb_vars)

        missing = [
            name for name, value in required_vars.items()
            if not value or (isinstance(value, int) and value == 0)
        ]

        if missing:
            raise SystemExit(
                f"❌ Missing required environment variables: {', '.join(missing)}\n"
                f"Please check your .env file and ensure all required variables are set.\n"
                f"📖 See sample.env for reference configuration."
            )
