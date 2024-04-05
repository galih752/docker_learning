from fastapi import APIRouter, Depends, HTTPException, Request
from config.dbfull import get_database
from routes.login import admin_required, get_current_active_user
from schemas.schemas import SchoolPadalarang, SchoolsPadalarang
from models.models import School
from bson import ObjectId
import pymongo

sch = APIRouter(tags=["Schools"])

@sch.get('/')
async def find_all_schools(database=Depends(get_database)):
    db_school = database["schools"]
    school_cursor = db_school.find()
    school_list = await school_cursor.to_list(length=None)
    if not school_list:
        return []
    result = [SchoolPadalarang(school) for school in school_list]
    return result

@sch.post('/',dependencies=[Depends(admin_required)])
async def create_schools(school : School, database=Depends(get_database)):
    db_school = database["schools"]
    existing_item = await db_school.find_one({"school_name": school.school_name})
    if existing_item:
        return 'Data already exists.'
    else:
        await db_school.insert_one(dict(school))
        return HTTPException(status_code=200,detail="Data added successfully!",headers="Success!")

@sch.put('/{id}',dependencies=[Depends(admin_required)])
async def dapot_student(id, school: School,database=Depends(get_database),curent_user = Depends(get_current_active_user)):
    db_school = database["schools"]
    updated_school = await db_school.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": dict(school)},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return SchoolPadalarang(updated_school)

@sch.delete('/{id}',dependencies=[Depends(admin_required)])
async def delete_school(id, database=Depends(get_database)):
    db_school = database["schools"]
    school = await db_school.find_one_and_delete({"_id": ObjectId(id)})
    if school:
        return SchoolPadalarang(school)
    else:
        return {"message": "Data not found"}