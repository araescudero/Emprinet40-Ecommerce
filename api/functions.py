from werkzeug.security import generate_password_hash,check_password_hash
import datetime
from sqlalchemy import  text
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import jwt
from db import engine
from .query import *



llave = "Th1s1ss3cr3t" 

def valida_user(username,password):
    with engine.connect() as con:
        try:
            user = con.execute(text(f"select * from usuario where username='{username}'")).one()
        except:
            user = None 
    if user : #Si el user no es none...
        #Valide la contraseña
        if check_password_hash(user[2], password):  
            #Si es correcta la contraseña, genera el token
            token = jwt.encode({'public_id': user[1], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, llave)  
            if isinstance(token, bytes):
                token = token.decode('Utf-8')
            
            return {'token' : token}
    return {"respuesta": "Contraseña incorrecta!"}


def crear_usuario(username,password):
    hash_password = generate_password_hash(password,method="sha256")
    
    try:
        engine.execute(text(insertar_usuario(username,hash_password)))
    except:
        return {"Respuesta":"No se creo el user"}
    return {"respuesta":"Usuario creado correctamente!"}