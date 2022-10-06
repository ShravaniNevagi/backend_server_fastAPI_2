
import http
from typing import List
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel
import requests

app = FastAPI()
import json

class Info(BaseModel):
    port: str
    ipaddress: str
    token: str
    client_name: str
    

@app.get("/")
def root():
    return {"hello"}
  
import zipfile, io

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

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)