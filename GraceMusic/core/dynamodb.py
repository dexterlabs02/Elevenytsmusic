"""
DynamoDB implementation for Grace Music Bot
Handles database operations for users, chats, playlists, broadcasts, and analytics
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

try:
    import boto3
    from botocore.exceptions import ClientError
    DYNAMODB_AVAILABLE = True
except ImportError:
    DYNAMODB_AVAILABLE = False

logger = logging.getLogger("GraceMusic")


class DynamoDBClient:
    """DynamoDB client for Grace Music Bot"""

    def __init__(self, config):
        """
        Initialize DynamoDB client
        
        Args:
            config: Configuration object with AWS credentials
        """
        self.config = config
        
        if not DYNAMODB_AVAILABLE:
            logger.error("boto3 not installed. Install with: pip install boto3")
            self.dynamodb = None
            return

        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=config.AWS_REGION,
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
            )
            logger.info("✓ Connected to DynamoDB")
        except Exception as e:
            logger.error(f"❌ Failed to connect to DynamoDB: {e}")
            self.dynamodb = None

    async def initialize_tables(self) -> bool:
        """
        Create tables if they don't exist
        
        Returns:
            bool: True if successful
        """
        if not self.dynamodb:
            return False

        tables_config = {
            self.config.DYNAMODB_USERS_TABLE: {
                'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                'AttributeDefinitions': [{'AttributeName': 'user_id', 'AttributeType': 'N'}],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            self.config.DYNAMODB_CHATS_TABLE: {
                'KeySchema': [{'AttributeName': 'chat_id', 'KeyType': 'HASH'}],
                'AttributeDefinitions': [{'AttributeName': 'chat_id', 'AttributeType': 'N'}],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            self.config.DYNAMODB_BROADCAST_TABLE: {
                'KeySchema': [{'AttributeName': 'broadcast_id', 'KeyType': 'HASH'}],
                'AttributeDefinitions': [{'AttributeName': 'broadcast_id', 'AttributeType': 'S'}],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            self.config.DYNAMODB_ANALYTICS_TABLE: {
                'KeySchema': [
                    {'AttributeName': 'date', 'KeyType': 'HASH'},
                    {'AttributeName': 'event_type', 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'date', 'AttributeType': 'S'},
                    {'AttributeName': 'event_type', 'AttributeType': 'S'}
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            self.config.DYNAMODB_PLAYLIST_TABLE: {
                'KeySchema': [
                    {'AttributeName': 'chat_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'playlist_id', 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'chat_id', 'AttributeType': 'N'},
                    {'AttributeName': 'playlist_id', 'AttributeType': 'S'}
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            }
        }

        for table_name, config_dict in tables_config.items():
            try:
                table = self.dynamodb.create_table(
                    TableName=table_name,
                    **config_dict
                )
                table.wait_until_exists()
                logger.info(f"✓ Table '{table_name}' created/exists")
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceInUseException':
                    logger.error(f"❌ Error creating table {table_name}: {e}")
                    return False

        return True

    # ============ BROADCAST MEMORY OPERATIONS ============

    async def save_broadcast(self, broadcast_id: str, user_id: int, 
                            message_content: Dict[str, Any], 
                            target_chats: List[int], 
                            status: str = "pending") -> bool:
        """
        Save broadcast record to DynamoDB
        
        Args:
            broadcast_id: Unique broadcast identifier
            user_id: User who initiated broadcast
            message_content: Content to broadcast
            target_chats: List of chat IDs to broadcast to
            status: Broadcast status (pending, active, completed)
        
        Returns:
            bool: Success status
        """
        if not self.dynamodb:
            return False

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_BROADCAST_TABLE)
            table.put_item(
                Item={
                    'broadcast_id': broadcast_id,
                    'user_id': user_id,
                    'message_content': json.dumps(message_content),
                    'target_chats': target_chats,
                    'status': status,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'sent_count': 0,
                    'failed_count': 0
                }
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error saving broadcast: {e}")
            return False

    async def get_broadcast(self, broadcast_id: str) -> Optional[Dict]:
        """Get broadcast record"""
        if not self.dynamodb:
            return None

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_BROADCAST_TABLE)
            response = table.get_item(Key={'broadcast_id': broadcast_id})
            item = response.get('Item')
            
            if item and 'message_content' in item:
                item['message_content'] = json.loads(item['message_content'])
            
            return item
        except Exception as e:
            logger.error(f"❌ Error getting broadcast: {e}")
            return None

    async def update_broadcast_status(self, broadcast_id: str, 
                                     status: str, sent: int = 0, 
                                     failed: int = 0) -> bool:
        """Update broadcast status and counts"""
        if not self.dynamodb:
            return False

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_BROADCAST_TABLE)
            table.update_item(
                Key={'broadcast_id': broadcast_id},
                UpdateExpression='SET #status = :status, sent_count = :sent, failed_count = :failed, updated_at = :updated',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':sent': sent,
                    ':failed': failed,
                    ':updated': datetime.utcnow().isoformat()
                }
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error updating broadcast: {e}")
            return False

    async def list_broadcasts(self, status: Optional[str] = None, 
                             limit: int = 10) -> List[Dict]:
        """List recent broadcasts"""
        if not self.dynamodb:
            return []

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_BROADCAST_TABLE)
            
            if status:
                response = table.scan(
                    FilterExpression='#status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':status': status},
                    Limit=limit
                )
            else:
                response = table.scan(Limit=limit)
            
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"❌ Error listing broadcasts: {e}")
            return []

    # ============ ANALYTICS OPERATIONS ============

    async def log_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Log analytics event
        
        Args:
            event_type: Type of event (play, skip, join_chat, etc.)
            event_data: Event details
        
        Returns:
            bool: Success status
        """
        if not self.dynamodb:
            return False

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_ANALYTICS_TABLE)
            today = datetime.utcnow().strftime('%Y-%m-%d')
            
            table.put_item(
                Item={
                    'date': today,
                    'event_type': event_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    'event_data': json.dumps(event_data),
                    'count': 1
                }
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error logging event: {e}")
            return False

    async def get_analytics(self, event_type: str, 
                           days: int = 7) -> List[Dict]:
        """Get analytics for past N days"""
        if not self.dynamodb:
            return []

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_ANALYTICS_TABLE)
            responses = []
            
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
                response = table.get_item(
                    Key={
                        'date': date,
                        'event_type': event_type
                    }
                )
                if 'Item' in response:
                    item = response['Item']
                    if 'event_data' in item:
                        item['event_data'] = json.loads(item['event_data'])
                    responses.append(item)
            
            return responses
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return []

    async def get_stats(self) -> Dict[str, Any]:
        """Get overall bot statistics"""
        if not self.dynamodb:
            return {}

        try:
            stats = {}
            
            # Count users
            users_table = self.dynamodb.Table(self.config.DYNAMODB_USERS_TABLE)
            users_response = users_table.scan(Select='COUNT')
            stats['total_users'] = users_response.get('Count', 0)
            
            # Count chats
            chats_table = self.dynamodb.Table(self.config.DYNAMODB_CHATS_TABLE)
            chats_response = chats_table.scan(Select='COUNT')
            stats['total_chats'] = chats_response.get('Count', 0)
            
            # Get today's analytics
            analytics_table = self.dynamodb.Table(self.config.DYNAMODB_ANALYTICS_TABLE)
            today = datetime.utcnow().strftime('%Y-%m-%d')
            response = analytics_table.query(
                KeyConditionExpression='#date = :date',
                ExpressionAttributeNames={'#date': 'date'},
                ExpressionAttributeValues={':date': today}
            )
            stats['today_events'] = response.get('Count', 0)
            
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}

    # ============ USER OPERATIONS ============

    async def save_user(self, user_id: int, user_data: Dict) -> bool:
        """Save/update user in database"""
        if not self.dynamodb:
            return False

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_USERS_TABLE)
            user_data['user_id'] = user_id
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            table.put_item(Item=user_data)
            return True
        except Exception as e:
            logger.error(f"❌ Error saving user: {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        if not self.dynamodb:
            return None

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_USERS_TABLE)
            response = table.get_item(Key={'user_id': user_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None

    # ============ CHAT OPERATIONS ============

    async def save_chat(self, chat_id: int, chat_data: Dict) -> bool:
        """Save/update chat in database"""
        if not self.dynamodb:
            return False

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_CHATS_TABLE)
            chat_data['chat_id'] = chat_id
            chat_data['updated_at'] = datetime.utcnow().isoformat()
            
            table.put_item(Item=chat_data)
            return True
        except Exception as e:
            logger.error(f"❌ Error saving chat: {e}")
            return False

    async def get_chat(self, chat_id: int) -> Optional[Dict]:
        """Get chat data"""
        if not self.dynamodb:
            return None

        try:
            table = self.dynamodb.Table(self.config.DYNAMODB_CHATS_TABLE)
            response = table.get_item(Key={'chat_id': chat_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"❌ Error getting chat: {e}")
            return None
