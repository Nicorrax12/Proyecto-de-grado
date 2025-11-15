class Carrera:
    def __init__(self, id, nombre, descripcion, icono, color, activo=1):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.icono = icono
        self.color = color
        self.activo = activo
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'color': self.color,
            'activo': self.activo
        }
