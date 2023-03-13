from flask import Blueprint,jsonify,request
from flask_restx import Api, Resource, fields
from api.functions import *

#Blueprint
bp_api = Blueprint('Api', __name__, url_prefix='/Api')
#Api
api = Api(bp_api,version="1.0",title="Api",description="End Points")
ns_model = api.namespace('Methods', description='Metodos')


class VerificarDatos():
    #JSON
     Login = api.model('login',{
        "username":fields.String(description=u"username",required=True,),
        "password":fields.String(description=u"password",required=True,),
    })

@ns_model.route('/Login/')
#Descripcion...
@api.doc(description="Correo y contraseña")

class Login(Resource):
    @ns_model.expect(VerificarDatos.Login, validate= True)
    def post(self):
        auth = request.json
        print(auth)
        #user= {"username": "<username>", "password": "<password>"}
        #Datos que le paso...
        valida = valida_user(auth["username"], auth["password"])
        print(valida)
        if 'token' in valida: # Si el token esta en valida, quiere decir que se encontro un usuario + la contraseña es correcta...
            return jsonify(valida) #retorna EL TOKEN
        return jsonify({"Respuesta": "Login requerido!"})


@ns_model.route('/CreateUser/')
@api.doc(description="Correo y contraseña")
class CrearUsuario(Resource):
    @ns_model.expect(VerificarDatos.Login,validate=True)
    def post(self):
        usuario = request.json
        usuario_creado = crear_usuario(usuario["username"],usuario["password"])
        return jsonify(usuario_creado)