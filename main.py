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
    
    if cliente_data is None:
        return build_response(False, None, "Cliente no registrado"), 404

    return build_response(True, cliente_data, "Cliente encontrado"), 200

@app.route("/api/v1/cliente", methods=["POST"])
def set_cliente():
    data = ClienteSchema(request.get_json())
    service_result = service.set_cliente(data)

    if "error" in service_result:
        return build_response(False, None, service_result["error"])

    if "id" in service_result:
        message = "Cliente registrado correctamente"
        return build_response(True, service_result, message)

    return build_response(False, None, "No se pudo registrar el cliente"), 500

@app.route("/api/v1/cliente/codigo/", methods=["POST"])
def get_cliente_codigo():
    data = ClienteSchema(request.get_json())
    service_result = service.get_cliente_codigo(data.correo)

    success = "codigo" in service_result
    data_response = service_result if success else None
    message = "Código generado" if success else service_result.get("error", ["error"])

    return build_response(success, data_response, message)

@app.route("/api/v1/cliente/codigo/validar", methods=["POST"])
def validar_codigo():
    data = request.get_json()
    cliente_id = data.get('id')
    codigo = data.get('codigo')
    
    if not cliente_id or not codigo:
        return build_response(False, None, "Ingresa los datos completos")

    service_result = service.get_cliente_codigo_validar(cliente_id, codigo)
    success = "validacion" in service_result
    message = service_result.get("error") if "error" in service_result else f"Código válido. Minutos restantes: {service_result['minutos_restantes']}"
    
    return build_response(success, service_result if success else None, message)

if __name__ == "__main__":
    print("running server")
    app.run(host="0.0.0.0", port=3000)
