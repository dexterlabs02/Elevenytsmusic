# 🗄️ DynamoDB Setup Guide for Grace Music Bot

## Overview
This guide explains how to set up AWS DynamoDB as the database for Grace Music Bot, including broadcasting memory and analytics tracking.

---

## 📋 Table of Contents
1. [AWS Account Setup](#aws-account-setup)
2. [IAM User Creation](#iam-user-creation)
3. [DynamoDB Configuration](#dynamodb-configuration)
4. [Environment Variables](#environment-variables)
5. [Migration from MongoDB](#migration-from-mongodb)
6. [Testing](#testing)
7. [Cost Optimization](#cost-optimization)

---

## 1. AWS Account Setup

### Step 1: Create AWS Account
1. Go to https://aws.amazon.com/
2. Click "Create AWS Account"
3. Provide email, password, and account name
4. Add payment method
5. Verify phone number

### Step 2: Log In to AWS Console
1. Visit https://console.aws.amazon.com
2. Sign in with your AWS account

---

## 2. IAM User Creation (Recommended)

**⚠️ IMPORTANT:** Never use your AWS root account credentials in applications. Create an IAM user instead.

### Step 1: Create IAM User
1. Go to **IAM** service
2. Click **Users** in sidebar → **Create user**
3. Set username: `grace-music-bot`
4. Click **Next**

### Step 2: Set Permissions
1. Select **Attach policies directly**
2. Search for and select: **AmazonDynamoDBFullAccess**
   - This gives full DynamoDB access
   - For production, consider using a more restrictive policy

### Step 3: Create Access Keys
1. Click on the created user
2. Go to **Security credentials** tab
3. Click **Create access key**
4. Select **Application running outside AWS** (for local/cloud deployment)
5. Click **Next → Create access key**

### Step 4: Save Credentials
1. Copy:
   - **Access Key ID** → `AWS_ACCESS_KEY_ID`
   - **Secret Access Key** → `AWS_SECRET_ACCESS_KEY`
2. ⚠️ **SAVE THESE SECURELY** - You won't see the secret key again!
3. Click **Done**

---

## 3. DynamoDB Configuration

### Step 1: Verify AWS Region
The recommended region is **us-east-1** (N. Virginia) - most free tier benefits.

For other regions:
- `us-east-1` - North Virginia (Recommended)
- `us-west-2` - Oregon
- `eu-west-1` - Ireland
- `ap-southeast-1` - Singapore

---

## 4. Environment Variables

### Create/Update `.env` file from `sample.env`:

```bash
cp sample.env .env
```

### Configure DynamoDB in `.env`:

```env
# ============ AWS DYNAMODB ============
USE_DYNAMODB=True
AWS_ACCESS_KEY_ID=your_iam_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_iam_secret_access_key_here
AWS_REGION=us-east-1

# DynamoDB Table Names (auto-created on first run)
DYNAMODB_USERS_TABLE=grace_music_users
DYNAMODB_CHATS_TABLE=grace_music_chats
DYNAMODB_BROADCAST_TABLE=grace_music_broadcasts
DYNAMODB_ANALYTICS_TABLE=grace_music_analytics
DYNAMODB_PLAYLIST_TABLE=grace_music_playlists

# Feature Flags
ENABLE_ANALYTICS=True
ENABLE_BROADCAST_DB=True
```

### Install Required Package:
```bash
pip install boto3
# Or include in requirements.txt
echo "boto3>=1.26.0" >> requirements.txt
```

### Disable MongoDB (Optional):
If you only want to use DynamoDB, leave `MONGO_DB_URI` empty or set `USE_DYNAMODB=True`.

---

## 5. DynamoDB Table Structure

### Tables Automatically Created:

#### 1. **grace_music_users**
```
Primary Key: user_id (Number)
Stores: User settings, preferences, blacklist status
```

#### 2. **grace_music_chats**
```
Primary Key: chat_id (Number)
Stores: Chat settings, admin list, language preference
```

#### 3. **grace_music_broadcasts**
```
Primary Key: broadcast_id (String)
Stores: Broadcast records, delivery status, message content
Attributes:
  - user_id: Who sent the broadcast
  - target_chats: List of chat IDs
  - status: pending/active/completed
  - sent_count: Successfully sent count
  - failed_count: Failed delivery count
  - created_at: Timestamp
```

#### 4. **grace_music_analytics**
```
Primary Keys: date (String - YYYY-MM-DD), event_type (String)
Stores: Event tracking, statistics
Event Types:
  - play_music
  - skip_track
  - join_chat
  - user_joined
  - broadcast_sent
```

#### 5. **grace_music_playlists**
```
Primary Keys: chat_id (Number), playlist_id (String)
Stores: Saved playlists and custom queues
```

---

## 6. Migration from MongoDB

### Option 1: Keep Both Databases (Recommended Initially)
The code can support both MongoDB and DynamoDB simultaneously:

```env
# Keep MongoDB
MONGO_DB_URI=mongodb+srv://user:pass@cluster.mongodb.net/gracemusicdb

# Add DynamoDB
USE_DYNAMODB=True
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

### Option 2: Migrate Data

#### Step 1: Backup MongoDB
```bash
mongodump --uri="mongodb+srv://username:password@cluster" --out=backup
```

#### Step 2: Export to JSON
```python
import pymongo
import json

client = pymongo.MongoClient("mongodb+srv://...")
db = client['gracemusicdb']

for collection_name in db.list_collection_names():
    collection = db[collection_name]
    docs = list(collection.find({}))
    with open(f'{collection_name}.json', 'w') as f:
        json.dump(docs, f, default=str)
```

#### Step 3: Import to DynamoDB
Use the provided migration script `scripts/migrate_to_dynamodb.py` (see below).

---

## 7. Testing

### Step 1: Verify Configuration
```python
from GraceMusic.core.dynamodb import DynamoDBClient
from config import Config

config = Config()
db = DynamoDBClient(config)

# Check connection
if db.dynamodb:
    print("✅ Connected to DynamoDB")
else:
    print("❌ Failed to connect")
```

### Step 2: Test Tables
```python
import asyncio

async def test():
    # Initialize tables
    success = await db.initialize_tables()
    print(f"Tables initialized: {success}")
    
    # Test broadcast
    await db.save_broadcast(
        broadcast_id="test_1",
        user_id=12345,
        message_content={"text": "Test"},
        target_chats=[67890],
        status="pending"
    )
    
    # Get stats
    stats = await db.get_stats()
    print(f"Statistics: {stats}")

asyncio.run(test())
```

### Step 3: Check DynamoDB Console
1. AWS Console → DynamoDB
2. Click **Tables**
3. Verify `grace_music_*` tables exist
4. Click table → **View items** to see stored data

---

## 8. Broadcasting Memory Features

### Save Broadcast Record
```python
await db.save_broadcast(
    broadcast_id="bcast_001",
    user_id=YOUR_USER_ID,
    message_content={
        "text": "Important announcement",
        "format_entities": [...]
    },
    target_chats=[CHAT_ID1, CHAT_ID2, ...],
    status="pending"
)
```

### Track Broadcast Status
```python
# Update during broadcast
await db.update_broadcast_status(
    broadcast_id="bcast_001",
    status="active",
    sent=50,
    failed=2
)

# After completion
await db.update_broadcast_status(
    broadcast_id="bcast_001",
    status="completed",
    sent=100,
    failed=0
)
```

### Query Broadcasts
```python
# Get specific broadcast
broadcast = await db.get_broadcast("bcast_001")

# List all completed broadcasts
broadcasts = await db.list_broadcasts(status="completed", limit=10)
```

---

## 9. Analytics Tracking

### Log Events
```python
# When music is played
await db.log_event("play_music", {
    "chat_id": 12345,
    "user_id": 67890,
    "title": "Song Title",
    "duration": 180
})

# When user joins
await db.log_event("user_joined", {
    "user_id": 67890,
    "username": "username",
    "timestamp": datetime.utcnow().isoformat()
})

# When broadcast is sent
await db.log_event("broadcast_sent", {
    "broadcast_id": "bcast_001",
    "total_sent": 100,
    "failed": 0
})
```

### Query Analytics
```python
# Get last 7 days of "play_music" events
events = await db.get_analytics("play_music", days=7)

# Get overall statistics
stats = await db.get_stats()
print(f"Total Users: {stats['total_users']}")
print(f"Total Chats: {stats['total_chats']}")
print(f"Today's Events: {stats['today_events']}")
```

---

## 10. Cost Optimization

### DynamoDB Pricing Model
- **On-Demand**: Pay per read/write request
  - Good for variable traffic
  - Slightly more expensive per request
  
- **Provisioned**: Set fixed capacity
  - Good for predictable traffic
  - Cheaper at scale
  - Free tier: 25 read units, 25 write units

### Optimize Costs
1. **Use TTL (Time to Live)** for temporary data
2. **Archive old analytics** to S3 Glacier
3. **Use Provisioned capacity** for production
4. **Set up CloudWatch alarms** for unusual activity

### Free Tier (First 12 months)
- 25 read capacity units
- 25 write capacity units
- 25 GB storage
- Sufficient for small to medium bots

---

## 11. Troubleshooting

### Connection Issues
```
Error: ❌ Failed to connect to DynamoDB
Solution:
1. Verify AWS credentials in .env
2. Check AWS IAM user has DynamoDBFullAccess
3. Verify AWS_REGION is correct
4. Check internet connection
```

### Table Creation Fails
```
Error: ResourceInUseException
Solution: Table already exists (this is normal, will be reused)
```

### Permission Denied
```
Error: User: arn:aws:iam::... is not authorized
Solution:
1. Check IAM user has AmazonDynamoDBFullAccess
2. Verify credentials are correct (no extra spaces)
3. Re-generate access keys if needed
```

### Slow Performance
```
Solution:
1. Switch to Provisioned capacity
2. Increase read/write units
3. Add GSI (Global Secondary Index) for common queries
4. Enable DAX (DynamoDB Accelerator)
```

---

## 12. Production Deployment

### AWS Lambda (Serverless)
```yaml
# Deploy as Lambda function
Runtime: Python 3.11
Memory: 512 MB
Timeout: 300 seconds
Environment Variables: Copy from .env
```

### EC2 Instance
```bash
# Create security group allowing outbound to DynamoDB
aws ec2 authorize-security-group-egress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

### ECS/Kubernetes
```yaml
env:
  - name: AWS_ACCESS_KEY_ID
    valueFrom:
      secretKeyRef:
        name: aws-credentials
        key: access-key
  - name: AWS_SECRET_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: aws-credentials
        key: secret-key
```

---

## 📚 Additional Resources

- **AWS DynamoDB Docs**: https://docs.aws.amazon.com/dynamodb/
- **boto3 Documentation**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
- **IAM User Guide**: https://docs.aws.amazon.com/iam/latest/userguide/
- **AWS Pricing Calculator**: https://calculator.aws/

---

## 🆘 Need Help?

- Check logs: `docker logs grace-music-bot`
- AWS Console: https://console.aws.amazon.com
- DynamoDB Monitoring: CloudWatch Dashboard
- Support: Check GitHub Issues or Documentation

---

**Last Updated**: April 2024
