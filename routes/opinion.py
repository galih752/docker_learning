from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from config.dbfull import get_database
from routes.login import get_current_active_user
from schemas.schemas import OpinionPramuka, OpinionsPramuka
from models.models import UserInDB, myOpinion
from bson import ObjectId
import pymongo

opinion = APIRouter(tags=["Opinion"])

@opinion.get('/')
async def find_all_opinion(database=Depends(get_database)):
    opinion_collection = database['opinion']
    opinion_cursor = opinion_collection.find()
    opinion_list = await opinion_cursor.to_list(length=None)

    # Convert ObjectId to string for _id field
    result = [myOpinion(**opinion) for opinion in opinion_list]
    return HTTPException(status_code=200, detail=result)

@opinion.post('/')
async def create_opinion(opinion: myOpinion, current_user: UserInDB = Depends(get_current_active_user), database=Depends(get_database)):
    opinion_collection = database['opinion']
    existing_item = await opinion_collection.find_one({"subject": opinion.subject})
    if existing_item:
        raise HTTPException(status_code=400, detail="Data already exists.")
    else:
        opinion_data = {
            "sender_name": current_user.full_name,
            "subject": opinion.subject,
            "content": opinion.content,
        }
        inserted_opinion = await opinion_collection.insert_one(opinion_data)
        opinion_data['_id'] = inserted_opinion.inserted_id

        return HTTPException(status_code=200,detail=myOpinion(**opinion_data))

@opinion.put('/{id}')
async def update_opinion(id, opinion: myOpinion, current_user: UserInDB = Depends(get_current_active_user), database=Depends(get_database)):
    opinion_collection = database['opinion']
    obj_id = ObjectId(id)
    
    existing_opinion = await opinion_collection.find_one({"_id": obj_id})
    
    if not existing_opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")
    
    if current_user.is_admin or existing_opinion['sender_name'] == current_user.full_name:
        updated_opinion_data = opinion.dict(exclude={"sender_name"})  # Exclude sender_name from the update
        updated_opinion_data["updated_at"] = datetime.now()
        updated_opinion = await opinion_collection.find_one_and_update(
            {"_id": obj_id},
            {"$set": updated_opinion_data},
            return_document=True
        )
        
        if updated_opinion:
            updated_opinion['_id'] = str(updated_opinion['_id'])
            return myOpinion(**updated_opinion)
        else:
            raise HTTPException(status_code=500, detail="Failed to update opinion")
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to update this opinion.")

@opinion.delete('/{id}')
async def delete_opinion(id: str, current_user: UserInDB = Depends(get_current_active_user), database=Depends(get_database)):
    opinion_collection = database['opinion']
    obj_id = ObjectId(id)
    
    existing_opinion = await opinion_collection.find_one({"_id": obj_id})
    
    if not existing_opinion:
        raise HTTPException(status_code=404, detail="Opinion not found")
    
    if current_user.is_admin or existing_opinion['sender_name'] == current_user.full_name:
        deleted_opinion = await opinion_collection.find_one_and_delete({"_id": obj_id})
        
        if deleted_opinion:
            deleted_opinion['_id'] = str(deleted_opinion['_id'])
            return myOpinion(**deleted_opinion)
        else:
            raise HTTPException(status_code=500, detail="Failed to delete opinion")
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this opinion.")
