from fastapi import APIRouter, Request, HTTPException, Query, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from models.models import News, Comments, UserInDB
from config.dbfull import get_database
import pytz
from schemas.schemas import NewsPramuka, NewPramuka
from routes.comment import get_comment_by_id
from bson import ObjectId
import pymongo
from pymongo import DESCENDING
from routes.login import get_current_active_user
from typing import Optional, List
from datetime import datetime

news = APIRouter(tags=["News"])

@news.get('/')
async def find_all_news(database=Depends(get_database)):
    news_db = database["news"]
    news_cursor = news_db.find().sort("created_at", pymongo.DESCENDING)
    news_list = await news_cursor.to_list(length=None)
    if not news_list:
        return []
    result_news = []

    for news_item in news_list:
        news_id = str(news_item["_id"])
        query = {"id_news": news_id}
        comment_db = database["comment"]
        comment_cursor = comment_db.find(query)
        comments_data = await comment_cursor.to_list(length=None)
        comments = [Comments(**{**comment, "_id": str(comment["_id"])}) for comment in comments_data]
        updated_at = news_item.get("updated_at")
        writer = news_item.get("writer", "Unknown")
        result_news.append(News(
            id=news_id,
            category=news_item["category"],
            title=news_item["title"],
            thumbnail=news_item["thumbnail"],
            content=news_item["content"],
            images = news_item["images"],
            writer=writer,
            created_at=news_item["created_at"],
            updated_at=updated_at,
            comments=comments
        ))

    return result_news
   
@news.post('/')
async def create_news(
    news: News,
    current_user: UserInDB = Depends(get_current_active_user),
    database=Depends(get_database)
):
    news_db = database["news"]
    existing_item = await news_db.find_one({"title": news.title})
    if existing_item:
        raise HTTPException(status_code=400, detail="Data already exists.")
    else:
        local_timezone = pytz.timezone('Asia/Jakarta')

        # Dapatkan waktu sekarang dalam zona waktu lokal
        now_local = datetime.now(local_timezone)

        # Konversi hari dalam bahasa Inggris ke dalam bahasa Indonesia
        days_in_indonesian = [
            'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'
        ]

        # Format tanggal dalam format yang diinginkan
        formatted_date = "{}, {} {}".format(
            days_in_indonesian[now_local.weekday()],
            now_local.day,
            now_local.strftime("%b %Y")
        )
        new_news_data = {
            "category": news.category,
            "title": news.title,
            "thumbnail": news.thumbnail,
            "content": news.content,
            "images": news.images,
            "writer": current_user.full_name,
            "created_at": formatted_date,
        }
        result = await news_db.insert_one(new_news_data)
        new_news_data["_id"] = str(result.inserted_id)
        return new_news_data
    
async def parse_comments(comment_cursor):
    comments = []
    async for comment in comment_cursor:
        comment_dict = comment.copy()
        comment_dict["_id"] = str(comment["_id"]) 
        comments.append(comment_dict)
    return comments

@news.put('/{id}')
async def update_news(
    id: str,
    title: str = Form(...),
    description: str = Form(...),
    content: str = Form(...),
    hashtag: str = Form(...),
    thumbnail: str = Form(...),
    current_user= Depends(get_current_active_user),
    database=Depends(get_database),
):
    news_db = database["news"]
    news_data = {
        "title": title,
        "description": description,
        "content": content,
        "hashtag": hashtag,
        "thumbnail": thumbnail,
        "updated_at": datetime.now()
    }
    if current_user.is_admin:
        updated_news = await news_db.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": news_data},
            return_document=pymongo.ReturnDocument.AFTER
        )
    else:
        existing_news = await news_db.find_one({"_id": ObjectId(id), "author": current_user.full_name})
        if not existing_news:
            raise HTTPException(status_code=403, detail="You are not allowed to edit this news.")
        updated_news = await news_db.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": news_data},
            return_document=pymongo.ReturnDocument.AFTER
        )
    if not updated_news:
        raise HTTPException(status_code=404, detail="News not found.")
    return HTTPException(status_code=200, detail=NewPramuka(updated_news), headers="Data added successfully!")

@news.delete('/{id}')
async def delete_news(
    id: str,
    curent_user: UserInDB = Depends(get_current_active_user),
    database=Depends(get_database)
):
    is_admin = curent_user.is_admin
    news_db = database["news"]
    news_data = await news_db.find_one({"_id":ObjectId(id)})
    if news_data:
        if is_admin or news_data["author"] == curent_user.full_name:
            await news_db.find_one_and_delete({"_id": ObjectId(id)})
            return {"message": "News deleted successfully"}
        else:
            return {"message": "You are not authorized to delete this news."}
    else:
        raise HTTPException(status_code=404, detail="Data not found")
