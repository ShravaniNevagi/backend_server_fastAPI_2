
from sqlalchemy.orm import Session

import models

import os
from fastapi import File, UploadFile
import pathlib

def db_entry(db: Session, experimentname:str,projectname :str,token:str, port: str ,ip: str,path:str, clientname:str):
    db_entry_project = models.Project(project_name = projectname,token = token,port = port,ip = ip)
    db.add(db_entry_project)
    db.commit()
    db.refresh(db_entry_project)

    id = db_entry_project.project_id
    
    db_entry_exp = models.Experiment(project_id=id ,experiment_name = experimentname,token = token,experiment_path = path,clientname=clientname)
    db.add(db_entry_exp)
    db.commit()
    db.refresh(db_entry_exp)
    return

def save_file(db: Session, token: str, uploaded_file: File(...)):
    experiment = db.query(models.Experiment).filter(
        models.Experiment.token == token).first()
    experiment_name = experiment.experiment_name

    project_name = db.query(models.Project).filter(
        models.Project.token == experiment.token).first()
    project_name = project_name.project_name
    
    file_location = f"projects/{project_name}/{experiment_name}/{uploaded_file.filename}"
    file_extension = pathlib.Path(f'{file_location}').suffix
    with open(file_location, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    if file_extension == '.npz':
        os.rename(file_location, f'projects/{project_name}/{experiment_name}/data.npz')

    return "file uploaded"


def get_projects(db: Session):
    return db.query(models.Project).all()

def get_experiments(db: Session):
    return db.query(models.Experiment).all()

def get_projects_by_token(db: Session,token:str):
    return db.query(models.Project).filter(models.Project.token == token).all()

def get_experiments_by_token(db: Session,token:str):
    return db.query(models.Experiment).filter(models.Experiment.token == token).all()

def get_client_name(db: Session,token:str):
    client = db.query(models.Experiment).filter(models.Experiment.token == token).first()
    cllientname=client.clientname
    return cllientname

def get_exp_path(db: Session,token:str):
    client = db.query(models.Experiment).filter(models.Experiment.token == token).first()
    path=client.experiment_path
    return path