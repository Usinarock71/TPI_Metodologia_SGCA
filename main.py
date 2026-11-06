from fastapi import FastAPI, HTTPException
import datetime

app = FastAPI()

# BASE DE DATOS SIMULADA (Smell: Estado global, falta de persistencia real y Primitive Obsession)
db_solicitudes = []
contador_id = 1

# FUNCION 1: REGISTRAR SOLICITUD
# Smell detectado: Long Parameter List (lista de parometros inmensa)
# Smell detectado: Poor Naming (variables n, a, doc, corr, mat, tc, prio)
# Smell detectado: Long Method (hace validacion, creacion, guardado, log y notificacion todo junto)
@app.post("/registrar_solicitud")
def registrar(n: str, a: str, doc: str, corr: str, mat: str, tc: str, prio: int):
    global contador_id
    
    # Smell detectado: Duplicated code (validaciones manuales que se repetiran)
    if len(n) == 0 or len(a) == 0 or len(doc) == 0:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios")
    
    if tc not in ["Analitico", "Titulo", "Alumno Regular"]:
        raise HTTPException(status_code=400, detail="Tipo de certificado erroneo")

    # Smell detectado: Primitive Obsession (usar un diccionario suelto en vez de una Clase/Entidad)
    nueva_solicitud = {
        "id_sol": contador_id,
        "nombre_estudiante": n,
        "apellido_estudiante": a,
        "dni": doc,
        "email": corr,
        "matricula": mat,
        "tipo_certificado": tc,
        "prioridad": prio,
        "estado": "Pendiente",
        "responsable": None,
        "fecha": str(datetime.datetime.now())
    }
    
    db_solicitudes.append(nueva_solicitud)
    contador_id += 1
    
    # Smell detectado: Alto acoplamiento (logica de infraestructura harcodeada en la regla de negocio)
    print(f"Simulando conexion SMTP... Enviando email a {corr} desde smtp.universidad.edu.ar")
    
    return {"msg": "Solicitud creada exitosamente", "data": nueva_solicitud}


# FUNCION 2: CAMBIAR ESTADO
@app.put("/estado/{id_sol}")
def cambiar_estado(id_sol: int, nuevo_estado: str):
    # Smell detectado: Duplicated Code (busqueda iterativa manual que se repite en otros endpoints)
    encontrado = False
    for s in db_solicitudes:
        if s["id_sol"] == id_sol:
            encontrado = True
            # Lógica de negocio mezclada con el enrutamiento HTTP
            if s["estado"] == "Finalizado":
                raise HTTPException(status_code=400, detail="El tramite ya esta finalizado, no se puede cambiar")
            if nuevo_estado not in ["Pendiente", "En Proceso", "Finalizado", "Rechazado"]:
                raise HTTPException(status_code=400, detail="Estado invalido")
            
            s["estado"] = nuevo_estado
            print(f"Audit log: Estado de la solicitud {id_sol} paso a {nuevo_estado}")
            return {"msg": "Estado actualizado", "solicitud": s}
    
    if not encontrado:
        raise HTTPException(status_code=404, detail="Solicitud no existe en la base")


# FUNCION 3: ASIGNAR RESPONSABLE
@app.put("/responsable/{id_sol}")
def asignar_responsable(id_sol: int, resp: str):
    # Mas duplicacion de la logica de busqueda (Falta de cohesion)
    for s in db_solicitudes:
        if s["id_sol"] == id_sol:
            s["responsable"] = resp
            return {"msg": "Responsable asignado correctamente", "solicitud": s}
    raise HTTPException(status_code=404, detail="Solicitud no encontrada")


# FUNCION 4: GENERAR REPORTE
@app.get("/reportes")
def generar_reporte(filtro_estado: str = None):
    # Smell detectado: God Module (logica de filtrado, negocio y exportacion de archivos todo en el mismo lugar)
    resultado = []
    for s in db_solicitudes:
        if filtro_estado:
            if s["estado"] == filtro_estado:
                resultado.append(s)
        else:
            resultado.append(s)
    
    # Simulando exportacion acoplada que viola el Principio de Responsabilidad Unica (SRP)
    with open("reporte_temp.txt", "w") as file:
        file.write("REPORTE DE SOLICITUDES ACADEMICAS\n")
        for r in resultado:
            file.write(f"ID: {r['id_sol']} - Tipo: {r['tipo_certificado']} - Estado: {r['estado']}\n")
    
    return {"total_registros": len(resultado), "items": resultado}