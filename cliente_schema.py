# cliente_schema.py

class ClienteSchema:
    """Clase para manejar datos JSON de entrada de los controladores."""
    
    def __init__(self, data: dict):
        self.id = data.get('id', 0)
        self.nombres = data.get('nombres')
        self.correo = data.get('correo')
        self.passwordd = data.get('passwordd')
        
        self.codigo = data.get('codigo')