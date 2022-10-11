
from typing import List
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

import models
import crud

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
  


@app.post("/register", status_code=status.HTTP_200_OK)
def client_details(info : Info,db: Session = Depends(get_db), ):
    details = Info(**info.dict())
    payload ={'port' : details.port, 'ipaddress':details.ipaddress, 'token': details.token, 'client_name':details.client_name }

    clientname = details.client_name
    endpoint = 'client_registration'
    token = details.token
    if token.count("+") != 3:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="invalid token type")
    
    t3,t4, ip, port = token.split('+')
    url = f'http://{ip}:{port}/{endpoint}'
    r = requests.post(url, json = payload, data = payload)
    
  
    if r.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(r.content))

        for name in z.namelist():
            n = name
        # print(n)
        folder, projectname, experimentname, file = n.split('/')
        # print(projectname)
        # print(experimentname)
        path = f'{folder}/{projectname}/{experimentname}'

        exp_path = db.query(models.Experiment).filter(
        models.Experiment.experiment_path == path).first()
        if exp_path:
        
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="already registered for this experiment")

        crud.db_entry( db=db,experimentname = experimentname,path=path, projectname = projectname,token =token, port = port,ip=ip, clientname= clientname)



        z.extractall()


        return 'file unzipped and client registered'

    return r.status_code

@app.post("/upload-data-file", status_code=status.HTTP_200_OK)
async def upload_data_file(token: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):

    for file in files:

        crud.save_file(db=db, token=token, uploaded_file=file)
    
    return {"Result": "OK", "filenames": [file.filename for file in files]}



@app.get("/projects")
def read_projects(db: Session = Depends(get_db)):
    projects = crud.get_projects(db)
    return projects

@app.get("/experiments/")
def read_experiments(db: Session = Depends(get_db)):
    experiment = crud.get_experiments(db)
    return experiment



#data quality endpoint


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)