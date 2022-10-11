from enum import unique
import string
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence
from sqlalchemy.orm import relationship

from database import Base



class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False, index=True)
    token = Column(String)
    port = Column(String)
    ip = Column(String)
    experiments = relationship(
        "Experiment", back_populates="project", cascade="delete, merge, save-update")


class Experiment(Base):
    __tablename__ = "experiments"

    experiment_no = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String, nullable=False, index=True)
    
    experiment_path = Column(String)

    token = Column(String)


    project_id = Column(Integer, ForeignKey(
        "projects.project_id"), nullable=False)

    clientname = Column(String)

    project = relationship("Project", back_populates="experiments")