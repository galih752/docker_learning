from fastapi import Depends, dependencies
from pydantic import BaseModel, Field, EmailStr, constr, SecretStr
from enum import Enum
from typing import List, Optional
from config.dbfull import get_database
from bson import ObjectId
from datetime import datetime

#Users
class UserRegistration(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    hashed_password: str
    active: bool
    is_admin : bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

# Model untuk data token JWT
class TokenData(BaseModel):
    username: str

# Model untuk data pengguna
class User(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    active: bool
    
#Opinion
class myOpinion(BaseModel):
    id: str = Field(alias='_id')
    sender_name : str
    subject : str
    content : str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }
    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        super().__init__(**data)

class Admin(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    hashed_password: str
    active: bool
    is_admin : bool

#Schools
class School(BaseModel):
    school_name: str
    ambalan_name: str
    level: str
    gudep : str
    registration: bool
    
class UserInDB(BaseModel):
    full_name: str
    gudep_number:str
    username: str
    email: EmailStr
    hashed_password: str
    active: bool 
    is_admin: Optional[bool] = False
    school: List[School] = []
    opinions : List[myOpinion] = []
    
class FileActivity(BaseModel):
    id: str = Field(alias="_id")
    filename: str
    activity_id: str
    
#Activity
class Activity(BaseModel):
    id: str = Field(alias="_id")
    activity_name : str
    schedule_of_activities : str
    file : List[FileActivity] = []
    
    class Config:
        arbitrary_types_allowed = True
    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        super().__init__(**data)
        

#Data Potensi
class Dapot(BaseModel):
    gudep :str
    male_builder : int
    famale_builder : int
    male_member : int
    female_member : int
    bantara_member : int
    laksana_member : int
    garuda_member : int

#Dewan Kerja Ranting
class level(str,Enum):
    def __str__(self):
        return str(self.value)
    BANTARA = "Bantara"
    LAKSANA = "Laksana"
    GARUDA = "Garuda"
    
class DKR(BaseModel):
    name : str
    school_name : str
    level : level
    position : str
    period : str
    status : bool
    
# Comment
class Comments(BaseModel):
    id: str = Field(alias="_id")
    sender_name : str
    content: str
    id_news: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class News(BaseModel):
    id: Optional[str]
    category: Optional[str]
    title: Optional[str]
    thumbnail: Optional[str]
    content: Optional[str]
    images: List[str] = []
    writer : Optional[str]
    created_at: Optional[str] 
    updated_at: Optional[datetime] = None
    comments: List[Comments] = []

    @classmethod
    def get_comments_by_id_news(cls, news_id,database=Depends(get_database)):
        db_comment = database["comment"]
        db_news = database["news"]
        # Retrieve comments from MongoDB for the given news_id
        comments_docs = db_comment.find({"id_news": news_id})
        comments = [Comments(**doc) for doc in comments_docs]

        # Retrieve news data from MongoDB
        news_doc = db_news.find_one({"_id": ObjectId(news_id)})

        # Create a News object with the retrieved data and comments
        if news_doc:
            news = cls(
                id=str(news_doc['_id']),  # Convert _id to string and assign it to id
                title=news_doc['title'],
                description=news_doc['description'],
                content=news_doc['content'],
                category=news_doc['category'],
                thumbnail=news_doc.get('thumbnail'),
                comments=comments
            )
            return news
        else:
            return None

    