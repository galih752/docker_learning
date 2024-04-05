from fastapi import APIRouter, Request, Depends
from models.models import DKR
from config.dbfull import get_database
from routes.login import admin_required
from schemas.schemas import DewanKerja, DewansKerja
from bson import ObjectId
import pymongo

dkr = APIRouter(tags=["Dewan Kerja Ranting"])

@dkr.get('/')
async def find_all_dkr(database=Depends(get_database)):
    db_dkr = database["dkr"]
    dkr_cursor = db_dkr.find()
    dkr_list = await dkr_cursor.to_list(length=None)
    if not dkr_list:
        return []
    result = [DewanKerja(dkr) for dkr in dkr_list]
    return result

@dkr.post('/',dependencies=[Depends(admin_required)])
async def create_dkr(dkr : DKR, database=Depends(get_database)):
    db_dkr = database["dkr"]
    existing_item = await db_dkr.find_one({"name": dkr.name})
    if existing_item:
        return 'Data already exists.'
    else:
        await db_dkr.insert_one(dict(dkr))
        return dkr

@dkr.put('/{id}',dependencies=[Depends(admin_required)])
async def update_dkr(id, dkr: DKR, database=Depends(get_database)):
    db_dkr = database["dkr"]
    updated_dkr = await db_dkr.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": dict(dkr)},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return DewanKerja(updated_dkr)

@dkr.delete('/{id}',dependencies=[Depends(admin_required)])
async def delete_dkr(id, database=Depends(get_database)):
    db_dkr = database["dkr"]
    dkr = await db_dkr.find_one_and_delete({"_id": ObjectId(id)})
    if dkr:
        return DewanKerja(dkr)
    else:
        return {"message": "Data not found"}