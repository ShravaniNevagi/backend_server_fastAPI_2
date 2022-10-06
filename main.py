
from typing import List
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

import models

from database import SessionLocal, engine


from fastapi import File, UploadFile
from fastapi.responses import FileResponse


models.Base.metadata.create_all(bind=engine)
import zipfile, io


app = FastAPI()


origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Info(BaseModel):
    port: str
    ipaddress: str
    token: str
    client_name: str
    

@app.get("/")
def root():
    return {"hello"}
  


@app.post("/register")
def client_details(info : Info):
    details = Info(**info.dict())
    payload ={'port' : details.port, 'ipaddress':details.ipaddress, 'token': details.token, 'client_name':details.client_name }

    endpoint = 'client_registration'
    token = details.token
    if token.count("+") != 2:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="invalid token type")
    
    t, ip, port = token.split('+')
    url = f'http://{ip}:{port}/{endpoint}'
    r = requests.post(url, json = payload, data = payload)
    
  
    if r.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(r.content))


        z.extractall()


        return 'file unzipped and client registered'

    return r.status_code

#create 2 tables in a new db projects and experiments
#project - id, name, token, ip port from token
#experiment - name, project id, token, path to exp
#get projects
#get experiments
#upload data file

#zip model.h5 and loader.py
#data.npz

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)