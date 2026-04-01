#!/usr/bin/env python3
"""
Migration script to transfer data from MongoDB to DynamoDB
Usage: python migrate_to_dynamodb.py
"""

import asyncio
import logging
import sys
from pymongo import MongoClient
from config import Config
from GraceMusic.core.dynamodb import DynamoDBClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GraceMusic.Migration")


async def migrate_users(mongo_client, db):
    """Migrate users from MongoDB to DynamoDB"""
    logger.info("📦 Starting user migration...")
    
    try:
        mongo_db = mongo_client['gracemusicdb']
        users_collection = mongo_db['users']
        
        users = list(users_collection.find({}))
        logger.info(f"Found {len(users)} users in MongoDB")
        
        migrated = 0
        for user in users:
            user_id = user.get('_id')
            if not user_id:
                continue
                
            # Remove MongoDB _id field
            if '_id' in user:
                del user['_id']
            
            success = await db.save_user(user_id, user)
            if success:
                migrated += 1
        
        logger.info(f"✅ Migrated {migrated}/{len(users)} users")
        return migrated
    
    except Exception as e:
        logger.error(f"❌ Error migrating users: {e}")
        return 0


async def migrate_chats(mongo_client, db):
    """Migrate chats from MongoDB to DynamoDB"""
    logger.info("📦 Starting chat migration...")
    
    try:
        mongo_db = mongo_client['gracemusicdb']
        chats_collection = mongo_db['chats']
        
        chats = list(chats_collection.find({}))
        logger.info(f"Found {len(chats)} chats in MongoDB")
        
        migrated = 0
        for chat in chats:
            chat_id = chat.get('_id')
            if not chat_id:
                continue
            
            if '_id' in chat:
                del chat['_id']
            
            success = await db.save_chat(chat_id, chat)
            if success:
                migrated += 1
        
        logger.info(f"✅ Migrated {migrated}/{len(chats)} chats")
        return migrated
    
    except Exception as e:
        logger.error(f"❌ Error migrating chats: {e}")
        return 0


async def create_analytics_summary(mongo_client, db):
    """Create analytics summary from MongoDB data"""
    logger.info("📦 Creating analytics summary...")
    
    try:
        mongo_db = mongo_client['gracemusicdb']
        
        # Aggregate play counts by date
        if 'plays' in mongo_db.list_collection_names():
            plays_collection = mongo_db['plays']
            
            # Count total plays
            total_plays = plays_collection.count_documents({})
            
            await db.log_event("migration_complete", {
                "total_plays_migrated": total_plays,
                "migration_type": "mongodb_to_dynamodb"
            })
            
            logger.info(f"✅ Recorded {total_plays} plays in analytics")
            return total_plays
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Error creating analytics: {e}")
        return 0


async def main():
    """Main migration function"""
    logger.info("🚀 Starting MongoDB → DynamoDB Migration")
    logger.info("=" * 50)
    
    # Initialize configuration
    config = Config()
    
    # Verify MongoDB is configured
    if not config.MONGO_URL:
        logger.error("❌ MONGO_DB_URI not configured in .env")
        logger.info("📖 Please set MONGO_DB_URI before running migration")
        return False
    
    # Verify DynamoDB is configured
    if not config.USE_DYNAMODB:
        logger.error("❌ DynamoDB not enabled. Set USE_DYNAMODB=True in .env")
        return False
    
    # Connect to MongoDB
    logger.info("🔗 Connecting to MongoDB...")
    try:
        mongo_client = MongoClient(config.MONGO_URL)
        mongo_client.admin.command('ping')
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return False
    
    # Initialize DynamoDB
    logger.info("🔗 Initializing DynamoDB...")
    db = DynamoDBClient(config)
    
    if not db.dynamodb:
        logger.error("❌ Failed to initialize DynamoDB")
        return False
    
    # Create tables
    logger.info("📋 Creating DynamoDB tables...")
    if not await db.initialize_tables():
        logger.error("❌ Failed to create tables")
        return False
    
    # Perform migrations
    logger.info("=" * 50)
    logger.info("📦 MIGRATION IN PROGRESS")
    logger.info("=" * 50)
    
    users_migrated = await migrate_users(mongo_client, db)
    chats_migrated = await migrate_chats(mongo_client, db)
    analytics_created = await create_analytics_summary(mongo_client, db)
    
    # Print summary
    logger.info("=" * 50)
    logger.info("📊 MIGRATION SUMMARY")
    logger.info("=" * 50)
    logger.info(f"✅ Users migrated: {users_migrated}")
    logger.info(f"✅ Chats migrated: {chats_migrated}")
    logger.info(f"✅ Analytics recorded: {analytics_created}")
    logger.info("=" * 50)
    
    # Close connections
    mongo_client.close()
    
    logger.info("🎉 Migration completed successfully!")
    logger.info("\n💡 Next steps:")
    logger.info("1. Verify data in AWS DynamoDB Console")
    logger.info("2. Update your .env to use DynamoDB")
    logger.info("3. Restart the bot")
    logger.info("4. Monitor logs for any issues")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)
