from flask import Flask, jsonify,request, render_template
from sqlalchemy import  text
from db import Session, engine, conexion_db, db

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import cached_property
from api.controllers import bp_api
import json
import jwt
import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "Th1s1ss3cr3t"

#configuracion base de datos:

app.config['SQLALCHEMY_DATABASE_URI'] =conexion_db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)






migrate = Migrate(app, db)

session = Session()
app.register_blueprint(bp_api)
from models import *


@app.route('/', methods= ['GET'])
def hola():
    return render_template('index.html')


#Decorador pára añadir seguridad a los endpoints
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None
        #Si esta dentro del headers que le enviamos en la peticion...
        if 'access-tokens' in request.headers:
            token = request.headers['access-tokens']
        #Si no esta el token...
        if not token:
            return jsonify({'message': 'No has enviado el token'})

        #Intente decodificarlo para evaluar si aun sigue activo el token... ya que dentro de la funcion
        # login_user defini que dure 30 minutos y luego expire...
        try:
            decoded_token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print("Datos del decordador:")
            print(decoded_token_data)# Imprime esto: {'public_id': 'willyelenohash', 'exp': 1678647387}
            print(type(decoded_token_data)) #Imprime esto: <class 'dict'>
            print(decoded_token_data['public_id']) #Imprime esto: willyelenohash
            
        except Exception as e:
            print(e)
            #Si el token es invalido o ha expirado...
            return jsonify({'message': 'El token no es valido...'})
            #Añadir el public_id del usuario autenticado a los argumentos de la función decorada
        

        return f(decoded_token_data['public_id'], *args, **kwargs) #Retorno 'willyelenohash'
    return decorator


@app.route('/login', methods =['POST'])
def login_user(): 
    #Recibo los parámetros de username y password que envio
    auth = request.authorization   

    #Validamos...
    #Si no envío nada..., si no esta username o el password--- entonces le decimos que no podemos verificar.
    if not auth or not auth.username or not auth.password:      
            return jsonify({"Respuesta":"could not verify"})
    #En caso contrario...
    with engine.connect() as con:
        #Traigo el usuario...
        user = con.execute(text(f"select * from usuario where username = '{auth.username}'")).one()
        print("usuarioooooooooooooooooooooooo:")
        print(user)
         
    #Luego el hash del usuario que tenemos, lo valido con la contraseña que enviamos al de insonmia
    if check_password_hash(user[2], auth.password): 
        #Guardamos el username en la nueva llave del diccionario 'public_id' 
            token = jwt.encode({'public_id': user[1], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])  
            #Devolvemos un toki el usuario ya esta registrado en la base de datos...
            if isinstance(token, bytes):
                token = token.decode('Utf-8')
            return jsonify({'token' : token})
            
            #return jsonify({'token' : token.decode('Utf-8')}) 
            
    else:

        return jsonify({"Respuesta":"Contraseña incorrecta"})

@app.route("/logout", methods=["GET"])
def logout():
    # r.delete(session["username"])
    session.clear()
    return jsonify({"respuesta":" password no puede estar vacio"})

@app.route('/create_user', methods =['GET','POST'])
def create_user():
    datos= json.loads(request.data)
    if 'username' not in datos: #si la llave username no se encuentra dentro de la variable 'datos'...
        return jsonify({"respuesta":"No estas enviando el username!"})
    if 'password' not in datos: #si la llave username no se encuentra dentro de la variable 'datos'...
        return jsonify({"respuesta":"No estas enviando el password!"})
    if len (datos["username"]) == 0: #Si la longitud de la clave username es igual a cero, le indicamos que no puede estar vacio
        return jsonify({"respuesta":" username no puede estar vacio"})
    if len (datos["password"]) == 0:
        return jsonify({"respuesta":" password no puede estar vacio"})

    #print(datos)
    #print(type(datos))
    with engine.connect() as con:
        hash_password = generate_password_hash(datos['password'],method = "sha256")
        nuevo_usuario = Usuario(username =datos['username'], password = hash_password)
        session.add(nuevo_usuario)
        session.commit()
        try:
            session.commit()
        except:
            return jsonify({"Respuesta": "Uusario ya esta creado en la base de datos!"})

    return jsonify({"respuesta": "Usuario creado correctamente!"})

@app.route('/obtener_producto_usuario', methods= ['GET'])
@token_required
def obtener_producto_usuario(decoded_token_data):
    datos = json.loads(request.data)
    print("Datos desde obtener_PRODUCTO")
    print(datos) #Imprime esto: {'username': 'willyelenohash'}
    if 'username' not in datos:
        return jsonify({"respuesta": "Username no enviado"})
    with engine.connect() as con:
        #Query para obtener el usuariuo + la ejecutamos + guardamos la respuesta de la query
        obtener_usuario = f"select * from usuario where username = '{datos['username']}'"
        respuesta = con.execute(text(obtener_usuario)).one()
        print(respuesta) #Imprime esto: (19, 'willyelenohash', 'sha256$v0ZVikKg5oNnde2Y$b076e8131c7a9662e7a89382f7f34b33433cd459b86c74f2785f80f86b3878d1')
        #Hacemos la Query para obtener la venta de la respuesta que a la primer query
        obtener_productos = f"select descripcion_productos from productos where username_id = '{respuesta[0]}'"
        respuesta_productos = con.execute(text(obtener_productos))
        print("productos")
        print(respuesta_productos) #Imprime esto: <sqlalchemy.engine.cursor.CursorResult object at 0x00000252A1887340>
        #Usamos compresion de lista, para aguardar todas las ventas de ese usuario en una lista
        respuesta_productos = [i[0] for i in respuesta_productos]
        print(respuesta_productos)

        for i in respuesta_productos: #me imprime los datos completos de la persona que hizo la venta
           print(i)
        return jsonify({"Productos_del_usuario": {"usuario":datos['username'], "productos": respuesta_productos}})

#Obtener TODOS los productos
@app.route('/obtener_productos_general', methods =['GET'])
def obtener_productos_general():
    with engine.connect() as con:
        #Traigo todo lo que este en la tabla productos
        obtener_productos = f"select * from productos "
        respuesta_productos = con.execute(text(obtener_productos))
        lista = list()
        for i in respuesta_productos:
            lista.append({"ID_PRODUCTO": i[0],"NOMBRE_PRODUCTO": i[3],"VALOR_PRODUCTO": i[2]})
    return jsonify({"Respuesta":lista})

#Modificar un producto
@app.route('/modificar_producto', methods =['PUT'])
def modificar_producto():
    #with engine.connect() as con:
        data = json.loads(request.data)
        if 'id' not in data:
            return jsonify({"Respuesta":"El id no esta en el body validar datos!"})
        if 'precio' not in data:
            return jsonify({"Respuesta":"El precio no esta en el body validar datos!"})
        if 'descripcion' not in data:
            return jsonify({"Respuesta":"La descripcion no esta en el body validar datos!"})
        producto = Productos.query.get(data["id"])
        producto.precio = data["precio"]
        producto.descripcion_productos = data["descripcion"]
        db.session.commit()
        return jsonify({"Respuesta": "Producto Actualizado!"})


#Crear un Producto
@app.route('/crear_producto',methods =['POST'])
def crear_producto():
    data = json.loads(request.data)
    if 'id_username' not in data:
        return jsonify({"Respuesta":"El id_username no esta en el body validar datos!"})
    if 'precio' not in data:
        return jsonify({"Respuesta":"El precio no esta en el body validar datos!"})
    if 'descripcion' not in data:
        return jsonify({"Respuesta":"La descripcion no esta en el body validar datos!"})
    nuevo_producto = Productos(username_id = data["id_username"], precio= data["precio"], descripcion_productos=data["descripcion"])
    db.session.add(nuevo_producto)
    db.session.commit()
    return jsonify({"Respuesta": "Producto Creado"})

#Eliminar Producto
@app.route('/eliminar_producto', methods =['DELETE'])
def eliminar_producto():
    #with engine.connect() as con:
        data = json.loads(request.data)
        if 'id' not in data:
            return jsonify({"Respuesta":"El id no esta en el body validar datos!"})
        
        producto = Productos.query.get(data["id"])
        db.session.delete(producto)
        db.session.commit()
        return jsonify({"Respuesta": "Producto Eliminado!"})



if __name__ == "__main__":
    app.run(debug=True)