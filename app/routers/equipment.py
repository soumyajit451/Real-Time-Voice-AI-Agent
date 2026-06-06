import os
import tempfile
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from loguru import logger
from bson import ObjectId

from app.database import get_database
from app.models.equipment import Equipment
from app.models.document import Document
from app.config import settings


router = APIRouter()

@router.post("/", response_model=Equipment, status_code=status.HTTP_201_CREATED)
async def create_equipment(equipment: Equipment):
    
    """Create a new equipment"""
    db = get_database()
    
    # Check if equipment name already exists
    existing = await db.equipment.find_one({"name": equipment.name, "tenant_id": equipment.tenant_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Equipment with this name already exists"
        )
    
    # Add timestamps
    now = datetime.utcnow()
    equipment_dict = equipment.model_dump(exclude={"id"}, exclude_none=True)
    equipment_dict["created_at"] = now
    equipment_dict["updated_at"] = now
    
    # Insert into database
    result = await db.equipment.insert_one(equipment_dict)
    # Create response with _id as string
    response_dict = equipment.model_dump(exclude={"id"}, exclude_none=True)
    response_dict["_id"] = str(result.inserted_id)
    return Equipment(**response_dict)



