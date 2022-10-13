from sqlite3 import Timestamp
import string
from tokenize import String
from typing import List, Union
from xmlrpc.client import Boolean

from pydantic import BaseModel



class Experiment(BaseModel):
    experiment_no: int
    experiment_name: str
    project_id: int
    token: str
    clientname:str
    experiment_path:str
 

    class Config:
        orm_mode = True




class Project(BaseModel):
    project_id: int
    project_name: str
    token:str
    port:str
    ip:str
    experiments: List[Experiment] = []

    class Config:
        orm_mode = True

