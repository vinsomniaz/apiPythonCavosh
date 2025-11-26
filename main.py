from flask import Flask, request, jsonify
from flask_cors import CORS
from cliente_service import ClienteService
from cliente_schema import ClienteSchema
import os

app = Flask(__name__)
CORS(app) 
service = ClienteService()

def build_response(success, data, message):
    return jsonify({
        "success": success,
        "data": data,
        "message": message
    })

@app.route("/api/v1/cliente/login", methods=["POST"])
def get_cliente():
    data = ClienteSchema(request.get_json())
    cliente_data = service.get_cliente(data.correo, data.passwordd)
    
    success = cliente_data is not None
    message = "Cliente registrado" if success else "Cliente no registrado"
    
    return build_response(success, cliente_data, message)

@app.route("/api/v1/cliente", methods=["POST"])
def set_cliente():
    data = ClienteSchema(request.get_json())
    service_result = service.set_cliente(data)

    success = "id" in service_result or "update" in service_result
    data_response = service_result if "id" in service_result else None

    if "id" in service_result:
        message = "Cliente registrado"
    elif "update" in service_result:
        message = "Cliente actualizado"
    elif "error" in service_result:
        message = service_result["error"]
    else:
        message = "No se pudo registrar el cliente"

    return build_response(success, data_response, message)

@app.route("/api/v1/cliente/codigo/", methods=["POST"])
def get_cliente_codigo():
    data = ClienteSchema(request.get_json())
    service_result = service.get_cliente_codigo(data.correo)

    success = "codigo" in service_result
    data_response = service_result if success else None
    message = "Código generado" if success else service_result.get("error", "Error desconocido")

    return build_response(success, data_response, message)

@app.route("/api/v1/cliente/codigo/validar", methods=["POST"])
def validar_codigo():
    data = ClienteSchema(request.get_json())
    service_result = service.get_cliente_codigo_validar(data.correo, data.codigo)

    success = service_result is not None
    message = "Código validado correctamente" if success else "Código o correo incorrecto / expirado"
    
    return build_response(success, service_result, message)

if __name__ == "__main__":
    print("running server")
    app.run(host="0.0.0.0", port=3000)