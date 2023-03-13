from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
#from config import connection_db


"""AGREGADO"""

conexion_db = "postgresql://postgres:admin@localhost:5432/flask_db"
#Conexion emprinet:
# postgresql://emprinet:emprinet@161.35.97.39:5432/evaluation

Base= declarative_base()

engine = create_engine(conexion_db )
db = SQLAlchemy()
Session =sessionmaker(bind=engine)
