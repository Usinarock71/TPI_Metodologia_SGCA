from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime

app = FastAPI()

# ==========================================
# REFACTORING 1: Introduce Parameter Object (y Primitive Obsession fix)
# Crear clases (Modelos DTO) para estructurar los datos en lugar de variables sueltas.
# ==========================================
class SolicitudDTO(BaseModel):
    nombre_estudiante: str
    apellido_estudiante: str
    dni: str
    email: str
    matricula: str
    tipo_certificado: str
    prioridad: int

class Solicitud(BaseModel):
    id_sol: int
    estudiante_completo: str
    email: str
    tipo_certificado: str
    estado: str
    responsable: str | None = None
    fecha: str

# ==========================================
# REFACTORING 2: Move Method / Separación de Responsabilidades (SRP)
# Mover la lógica de la "Base de Datos" a su propia clase Repositorio.
# ==========================================
class RepositorioSolicitudes:
    def __init__(self):
        self.db = []
        self.contador_id = 1
    
    # REFACTORING 3: Extract Method (Centralizamos la búsqueda duplicada)
    def buscar_por_id(self, id_sol: int):
        for s in self.db:
            if s.id_sol == id_sol:
                return s
        return None

    def guardar(self, solicitud_dto: SolicitudDTO) -> Solicitud:
        nueva = Solicitud(
            id_sol=self.contador_id,
            estudiante_completo=f"{solicitud_dto.nombre_estudiante} {solicitud_dto.apellido_estudiante}",
            email=solicitud_dto.email,
            tipo_certificado=solicitud_dto.tipo_certificado,
            estado="Pendiente",
            fecha=str(datetime.datetime.now())
        )
        self.db.append(nueva)
        self.contador_id += 1
        return nueva

# Instanciar el repositorio (Simulación de Inyección de Dependencias)
repo = RepositorioSolicitudes()

# ==========================================
# REFACTORING 4: Extract Method (Desacoplamiento de infraestructura)
# Extraer la simulación de envío de correos fuera de los endpoints.
# ==========================================
def notificar_estudiante(email: str, mensaje: str):
    print(f"Audit Log: Enviando email a {email} -> {mensaje}")

# ==========================================
# CONTROLADORES HTTP
# ==========================================

@app.post("/registrar_solicitud")
def registrar(solicitud: SolicitudDTO):
    if solicitud.tipo_certificado not in ["Analitico", "Titulo", "Alumno Regular"]:
        raise HTTPException(status_code=400, detail="Tipo de certificado invalido")
    
    nueva_solicitud = repo.guardar(solicitud)
    notificar_estudiante(solicitud.email, "Tu solicitud fue registrada exitosamente")
    
    return {"msg": "Solicitud creada exitosamente", "data": nueva_solicitud}

@app.put("/estado/{id_sol}")
def cambiar_estado(id_sol: int, nuevo_estado: str):
    solicitud = repo.buscar_por_id(id_sol)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    if solicitud.estado == "Finalizado":
        raise HTTPException(status_code=400, detail="El tramite ya esta finalizado, no admite cambios")
    if nuevo_estado not in ["Pendiente", "En Proceso", "Finalizado", "Rechazado"]:
        raise HTTPException(status_code=400, detail="Estado invalido")
        
    solicitud.estado = nuevo_estado
    return {"msg": "Estado actualizado", "solicitud": solicitud}

@app.put("/responsable/{id_sol}")
def asignar_responsable(id_sol: int, resp: str):
    solicitud = repo.buscar_por_id(id_sol)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
    solicitud.responsable = resp
    return {"msg": "Responsable asignado correctamente", "solicitud": solicitud}

@app.get("/reportes")
def generar_reporte(filtro_estado: str = None):
    if filtro_estado:
        resultado = [s for s in repo.db if s.estado == filtro_estado]
    else:
        resultado = repo.db
        
    return {"total_registros": len(resultado), "items": resultado}