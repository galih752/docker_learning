from fastapi import APIRouter, Request, Query, HTTPException, Depends, Form
from config.dbfull import get_database
from schemas.schemas import NewsComentItem, NewsComents
from models.models import Comments, User, UserInDB
from bson import ObjectId
from routes.login import get_current_active_user
from pymongo.errors import DuplicateKeyError
import pymongo
from datetime import datetime

comment = APIRouter(tags=["Comments"])

@comment.get('/all')
async def find_all_comment(database=Depends(get_database)):
    comment_collection = database["comment"]
    comment_cursor = comment_collection.find()
    result = []

    async for comment in comment_cursor:
        if "id_news" not in comment:
            continue

        # Mengambil informasi berita berdasarkan id_news
        news_collection = database["news"]
        news = await news_collection.find_one({"_id": ObjectId(comment["id_news"])})
        if not news:
            continue

        # Membuat objek NewsComentItem dengan tambahan informasi title
        comment_item = NewsComentItem(comment)
        comment_item["title"] = news.get("title", "")  # Sesuaikan dengan atribut berita yang sesuai

        result.append(comment_item)

    return result

@comment.get('/me')
async def find_all_comment(database=Depends(get_database), current_user=Depends(get_current_active_user)):
    comment_collection = database["comment"]
    comment_cursor = comment_collection.find({"sender_name": current_user.full_name})
    result = []

    async for comment in comment_cursor:
        if "id_news" not in comment:
            continue

        # Mengambil informasi berita berdasarkan id_news
        news_collection = database["news"]
        news = await news_collection.find_one({"_id": ObjectId(comment["id_news"])})
        if not news:
            continue

        # Membuat objek NewsComentItem dengan tambahan informasi title
        comment_item = NewsComentItem(comment)
        comment_item["title"] = news.get("title", "")  # Sesuaikan dengan atribut berita yang sesuai

        result.append(comment_item)

    return result

@comment.get('/by_news/{id_news}')
async def get_comment_by_id(id_news: str, current_user: UserInDB = Depends(get_current_active_user), database=Depends(get_database)):
    comment_collection = database["comment"]
    comment_cursor = comment_collection.find({"id_news": id_news, "sender_name": current_user.full_name})
    comment_list = await comment_cursor.to_list(length=None)

    if not comment_list:
        raise HTTPException(status_code=404, detail="Data not found")

    for comment in comment_list:
        comment["_id"] = str(comment["_id"])

    return comment_list

@comment.post('/')
async def create_coment(coment: Comments, current_user: UserInDB = Depends(get_current_active_user), database=Depends(get_database)):
    coment_collection = database['comment']
    coment_data = {
        "sender_name": current_user.full_name,
        "content": coment.content,
        "id_news": coment.id_news,
        "created_at": coment.created_at
    }
    inserted_coment = await coment_collection.insert_one(coment_data)
    coment_data['_id'] = str(inserted_coment.inserted_id)

    return HTTPException(status_code=200,detail=Comments(**coment_data))


@comment.put('/{id}')
async def update_coment(id, coment: Comments, current_user: UserInDB = Depends(get_current_active_user), database=Depends(get_database)):
    coment_collection = database['comment']
    obj_id = ObjectId(id)
    
    coment.sender_name = current_user.full_name
    updated_coment = await coment_collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": dict(coment)},
        return_document=True
    )
    if updated_coment:
        updated_coment['_id'] = str(updated_coment['_id'])
        return HTTPException(status_code=200,detail=Comments(**updated_coment), headers="Data added successfully!")
    else:
        raise HTTPException(status_code=404, detail="Opinion not found")

@comment.delete('/{id}')
async def delete_comment(id ,database =Depends(get_database),curent_user= Depends(get_current_active_user)):
    coment_db = database["comment"]
    opinion = await coment_db.find_one_and_delete({"_id": ObjectId(id)})
    if opinion:
        return NewsComentItem(opinion)
    else:
        return {"message": "Data not found"}
