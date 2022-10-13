
import json
from math import frexp
from typing import List
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

import models
import docker
import crud

from database import SessionLocal, engine


from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from fastapi import Request

models.Base.metadata.create_all(bind=engine)
import zipfile, io
from typing import Set, Union
import os

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

@app.get("/projects/{token}")
def read_projects_by_token(token:str, db: Session = Depends(get_db)):
    project = crud.get_projects_by_token(db=db,token=token)
    return project

@app.get("/experiments/{token}")
def read_experiments_by_token(token:str,db: Session = Depends(get_db)):
    experiment = crud.get_experiments_by_token(db=db, token=token)
    return experiment


class test2(BaseModel):
    number_of_epochs:int
    batch_size:int
    ipaddress:str
    port:str
    experiment_name:str
    run_name:str
    run_path:str
    experiment_path:str
    number_of_rounds: int
    number_of_clients:int


class test(BaseModel):
    token:str
    run_name:str
    runs_config : Union[test2, None] = None

@app.post("/start_client/")
async def start_client(info : test,db: Session = Depends(get_db)):
    details = test(**info.dict())
    runs_config_temp = details.runs_config
    token = details.token
    client_name = crud.get_client_name(db=db,token=token)
    

    exp_path = os.getcwd() + '/'+crud.get_exp_path(db=db,token=token)
    run_name= details.run_name
    dir = f'{exp_path}/runs/{run_name}'
    try:
        os.makedirs(dir)
    except:
        pass
    FILE = dir + '/runs_config.json'

    runs_config = {}
    for i in runs_config_temp:
        runs_config[i[0]]= i[1]
    runs_config['client_name']=client_name
    DATA = json.dumps(runs_config)
    with open(FILE, mode='w') as f:
        json.dump(runs_config,f)

    client = docker.from_env()
    container = client.containers.run(image = 'flower_tensorflow_client',network='host', environment = ['RUN_PATH=runs/'+run_name+'/'],volumes = {exp_path:{'bind':'/app/dir/','mode': 'rw'}},detach=True,auto_remove = True)
    




    # docker run --rm --network host -e RUN_PATH='runs/run1/' -v /home/sashreek/temp/experiment1:/app/dir/ client
    return 200




#data quality endpoint


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8080, reload=True)