import os
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pymongo import ReturnDocument
from config.dbfull import get_database
from routes.login import admin_required, get_current_active_user
from schemas.schemas import ActivityPramuka
from models.models import Activity, FileActivity
from bson import ObjectId
from config.dbfull import get_database
from pymongo.errors import DuplicateKeyError
from bson.errors import InvalidId

UPLOAD_DIR = "uploads"

activity = APIRouter(tags=["Activity"])

@activity.get('/')
async def find_all_activity(database=Depends(get_database)):
    activity_collection = database['activity']
    activity_cursor = activity_collection.find()
    activity_list = await activity_cursor.to_list(length=None)
    
    result = []

    for activity in activity_list:
        activity_data = Activity(**activity)

        # Mengambil file-file terkait dengan aktivitas berdasarkan ID aktivitas
        file_collection = database['file_activity']
        files_cursor = file_collection.find({"activity_id": str(activity['_id'])})
        files_list = await files_cursor.to_list(length=None)

        # Menambahkan file-file ke dalam aktivitas jika ada
        if files_list:
            files = []
            for file_data in files_list:
                # Konversi ObjectId ke string sebelum membuat objek FileActivity
                file_data['_id'] = str(file_data['_id'])
                files.append(FileActivity(**file_data))
            activity_data.file = files

        result.append(activity_data)

    return result

@activity.post('/activity')
async def create_activity(
    activity: Activity, 
    database=Depends(get_database),
    is_admin : bool =Depends(admin_required)
):
    activity_collection = database['activity']
    try:
        result = await activity_collection.insert_one(activity.dict())
        activity_id = str(result.inserted_id)
        return {"message": "Data added successfully!", "activity_id": activity_id}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Duplicate activity name")

@activity.post('/activity/{activity_id}/file')  # Menambahkan path parameter untuk activity_id
async def upload_file(
    activity_id: str,
    up_files: List[UploadFile] = File(...),
    database=Depends(get_database),
    is_admin: bool = Depends(admin_required)
):
    activity_collection = database['file_activity']
    activity_ids = []

    try:
        for up_file in up_files:
            if not up_file.filename.lower().endswith('.pdf'):
                return {"message": "Only PDF files are allowed"}
            contents = await up_file.read()

            # Membuat direktori jika belum ada
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            # Menyimpan file ke direktori upload dengan nama asli
            file_path = os.path.join(UPLOAD_DIR, up_file.filename)
            with open(file_path, "wb") as file_object:
                file_object.write(contents)

            # Simpan metadata file ke database
            file_data = {
                "activity_id": activity_id,
                "filename": up_file.filename,
                "file_path": file_path  # Menyimpan path lokal file
            }
            result = await activity_collection.insert_one(file_data)
            file_id = str(result.inserted_id)
            activity_ids.append(file_id)

        return {"message": "Data added successfully!", "file_ids": activity_ids}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid activity ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@activity.put('/{id}')
async def update_activity(id: str, activity: Activity,database=Depends(get_database),is_admin : bool =Depends(admin_required)):
    activity_collection = database['activity']
    activity_id = ObjectId(id)
    updated_activity = await activity_collection.find_one_and_update(
        {"_id": activity_id},
        {"$set": activity.dict()},
        return_document=ReturnDocument.AFTER
    )
    if updated_activity:
        return {"message": "Data updated successfully!", "activity_id": str(updated_activity["_id"])}
    else:
        raise HTTPException(status_code=404, detail="Data not found")

@activity.delete('/{id}',dependencies=[Depends(admin_required)])
async def delete_activity(id: str, database=Depends(get_database)):
    activity_collection = database['activity']
    activity_id = ObjectId(id)
    delete_result = await activity_collection.delete_one({"_id": activity_id})
    if delete_result.deleted_count == 1:
        return {"message": "Data deleted successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Data not found")