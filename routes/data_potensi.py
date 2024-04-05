from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from models.models import Dapot, School, UserInDB
from config.dbfull import get_database
from routes.login import get_current_active_user, get_current_user, non_admin_required
from schemas.schemas import DataPotensi, DatasPotensi
from bson import ObjectId
from pymongo.collection import Collection
import pymongo

dapot = APIRouter(tags=["Data Potensi"])

@dapot.get('/')
async def get_schools_with_potentials(database: Collection = Depends(get_database)):
    # Retrieve all schools
    db_school = database["schools"]
    schools = await db_school.find().to_list(length=None)

    # Retrieve all dapot data
    db_dapot = database["dapot"]
    all_dapot = await db_dapot.find().to_list(length=None)

    # Create a dictionary to store dapot data based on gudep

    # Prepare the result list
    result = []

    # Iterate through schools and check if dapot data exists
    for school in schools:
        gudep = school["gudep"]
        dapot_data = next((dapot for dapot in all_dapot if dapot.get("gudep") == gudep), None)

        if dapot_data is not None:
            # If dapot data exists, use the existing data
            result.append({
                "school_name": school["school_name"],
                "ambalan_name": school["ambalan_name"],
                "level": school["level"],
                "gudep": gudep,
                "registration": school["registration"],
                "dapot_data": {
                    "male_builder": dapot_data.get("male_builder", 0),
                    "female_builder": dapot_data.get("female_builder", 0),
                    "male_member": dapot_data.get("male_member", 0),
                    "female_member": dapot_data.get("female_member", 0),
                    "bantara_member": dapot_data.get("bantara_member", 0),
                    "laksana_member": dapot_data.get("laksana_member", 0),
                    "garuda_member": dapot_data.get("garuda_member", 0),
                }
            })
        else:
            # If no dapot data exists, use default values (0)
            result.append({
                "school_name": school["school_name"],
                "ambalan_name": school["ambalan_name"],
                "level": school["level"],
                "gudep": gudep,
                "registration": school["registration"],
                "dapot_data": {
                    "male_builder": 0,
                    "female_builder": 0,
                    "male_member": 0,
                    "female_member": 0,
                    "bantara_member": 0,
                    "laksana_member": 0,
                    "garuda_member": 0,
                }
            })

    return result

@dapot.post('/')
async def create_dapot(dapot: Dapot, database: Collection = Depends(get_database),current_user: UserInDB = Depends(get_current_user)):
    print(database)  # Print or use a debugger to inspect the content
    db_dapot = database["dapot"]
    await db_dapot.insert_one(dapot.dict())
    existing_item = await db_dapot.find_one({"gudep": dapot.gudep})
    if existing_item:
        raise HTTPException(status_code=400, detail="Data already exists.")

@dapot.put('/{id}')
async def dapot_student(id, dapot: Dapot,database=Depends(get_database),curent_user = Depends(get_current_active_user)):
    db_dapot = database["dapot"]
    updated_dapot = await db_dapot.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": dict(dapot)},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return DataPotensi(updated_dapot)

@dapot.delete('/{id}')
async def delete_dapot(id,database=Depends(get_database),curent_user = Depends(get_current_active_user)):
    db_dapot = database["dapot"]
    dapot = await db_dapot.find_one_and_delete({"_id": ObjectId(id)})
    if dapot:
        return DataPotensi(dapot)
    else:
        return {"message": "Data Potensi not found"}    
