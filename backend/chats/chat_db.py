from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import redis
import json
import logging
from redis.exceptions import RedisError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection
try:
    r = redis.Redis(host='redis', port=6379, db=0)
    r.ping()  # Test connection to Redis
except RedisError as re:
    logger.error(f"Failed to connect to Redis: {str(re)}")
    raise HTTPException(status_code=500, detail="Redis connection error")

# Define a router
router = APIRouter()

# Define a model for the message
class Message(BaseModel):
    role: str
    content: str

# Define a model for the conversation
class Conversation(BaseModel):
    user_id: str
    conversation: List[Message]

# Endpoint to save a conversation
@router.post("/save-conversation/")
async def save_conversation(conversation: Conversation):
    try:
        # Convert the Pydantic models to dictionaries
        conversation_dict = conversation.dict()
        
        # Retrieve the existing conversation from Redis
        existing_conversation_data = r.get(f"conversation_{conversation_dict['user_id']}")
        
        if existing_conversation_data:
            existing_conversation = json.loads(existing_conversation_data)
            # Append new messages to the existing conversation
            existing_conversation["conversation"] = conversation_dict["conversation"]
        else:
            # If no existing conversation, create a new one
            existing_conversation = conversation_dict
        
        # Save the updated conversation back to Redis
        r.set(f"conversation_{conversation_dict['user_id']}", json.dumps(existing_conversation))
        return {"status": "Conversation saved successfully"}
    
    except RedisError as re:
        logger.error(f"Redis error while saving conversation: {str(re)}")
        raise HTTPException(status_code=500, detail="Redis error while saving conversation")
    except (json.JSONDecodeError, TypeError) as je:
        logger.error(f"JSON serialization error: {str(je)}")
        raise HTTPException(status_code=500, detail="Error serializing conversation data")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving conversation")

# Endpoint to get the conversation
@router.get("/get-conversation/{user_id}")
async def get_conversation(user_id: str):
    try:
        conversation_data = r.get(f"conversation_{user_id}")
        if not conversation_data:
            # Create a new conversation with a welcome message if not found
            welcome_message = {
                "role": "assistant",
                "content": "Hello, I am Metal Yapi AI assistant. How can I help you?"
            }
            new_conversation = {
                "user_id": user_id,
                "conversation": [welcome_message]
            }
            # Save the new conversation to Redis
            r.set(f"conversation_{user_id}", json.dumps(new_conversation))
            return new_conversation
        
        # Deserialize the conversation from Redis
        conversation = json.loads(conversation_data)
        return conversation
    
    except RedisError as re:
        logger.error(f"Redis error while retrieving conversation: {str(re)}")
        raise HTTPException(status_code=500, detail="Redis error while retrieving conversation")
    except (json.JSONDecodeError, TypeError) as je:
        logger.error(f"JSON parsing error: {str(je)}")
        raise HTTPException(status_code=500, detail="Error parsing conversation data")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving conversation")
