from fastapi import FastAPI
from routes.schools import sch
from routes.data_potensi import dapot
from routes.dkr import dkr
from routes.news import news
from routes.activity import activity
from routes.login import login
from routes.opinion import opinion
from routes.comment import comment

app = FastAPI(
    title='Dira Abinawa',
    version='1.0.0'
)

# app.include_router(login,prefix='/token', tags=["Login"])
app.include_router(dkr,prefix='/dkr', tags=["Dewan Kerja Ranting"])
app.include_router(sch,prefix='/school', tags=["Schools"])
app.include_router(dapot, prefix='/dapot', tags=["Data Potensi"])
app.include_router(news, prefix='/news', tags=["News"])
app.include_router(comment, prefix='/coment', tags=["Comments"])
app.include_router(activity, prefix='/activity', tags=["Activity"])
app.include_router(opinion, prefix='/opinion', tags=["Opinion"])