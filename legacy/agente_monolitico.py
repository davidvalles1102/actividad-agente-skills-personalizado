"""
Proyecto base (semana anterior): agente conversacional simple.

Este script representa el punto de partida de la actividad "Refactorizacion
y Personalizacion de un Sistema Agentico mediante Skills Propias". Se deja
intacto a proposito para que el contraste con la version refactorizada
(carpetas core/, skills/, agents/ en la raiz del repositorio) sea evidente.

Problemas de diseno que tiene este archivo (documentados a proposito,
como evidencia del "antes"):
  1. Toda la logica vive en una sola funcion gigante (responder_mensaje):
     no hay separacion entre logica, configuracion y comportamiento.
  2. La "personalidad" del agente (nombre) esta hardcodeada junto con la
     logica de negocio; cambiar el tono o el idioma implica editar codigo.
  3. Cada capacidad (calculo, tareas, resumen, busqueda) esta escrita en
     linea dentro del if/elif: no se puede reutilizar, probar ni activar
     o desactivar de forma independiente.
  4. Las tareas viven en una lista global en memoria: se pierden al cerrar
     el programa.
  5. El calculo usa eval() directo sobre texto del usuario (riesgo de
     seguridad).
  6. Hay logica de formato de texto duplicada (construccion manual de
     strings con "+") en varias ramas.
  7. No existe ningun mecanismo para crear un segundo agente con otra
     personalidad o con un subconjunto distinto de capacidades.
  8. No hay pruebas automatizadas de ningun tipo.
"""

NOMBRE_AGENTE = "AgenteV1"
tareas_en_memoria = []


def calcular(mensaje):
    expresion = mensaje.lower().replace("calcula", "").strip()
    try:
        resultado = eval(expresion)  # inseguro: eval() sobre texto libre del usuario
    except Exception as error:
        return "No pude calcular eso: " + str(error)
    return "El resultado es " + str(resultado)


def responder_mensaje(mensaje):
    mensaje_lower = mensaje.lower()

    if "calcula" in mensaje_lower:
        return calcular(mensaje)

    if "agrega tarea" in mensaje_lower:
        texto = mensaje_lower.replace("agrega tarea", "").strip()
        tareas_en_memoria.append(texto)
        return "Tarea agregada: " + texto

    if "lista tareas" in mensaje_lower:
        if len(tareas_en_memoria) == 0:
            return "No hay tareas"
        texto_tareas = ""
        for i in range(len(tareas_en_memoria)):
            texto_tareas = texto_tareas + str(i + 1) + ". " + tareas_en_memoria[i] + "\n"
        return texto_tareas

    if "resume" in mensaje_lower:
        texto = mensaje.split(":")[-1] if ":" in mensaje else mensaje
        palabras = texto.split(" ")
        if len(palabras) <= 15:
            return "Resumen: " + texto
        resumen = " ".join(palabras[:15]) + "..."
        return "Resumen: " + resumen

    if "busca archivo" in mensaje_lower:
        import os
        patron = mensaje_lower.replace("busca archivo", "").strip()
        encontrados = []
        for raiz, carpetas, archivos in os.walk("."):
            for archivo in archivos:
                if patron in archivo.lower():
                    encontrados.append(os.path.join(raiz, archivo))
        if len(encontrados) == 0:
            return "No encontre archivos"
        texto_archivos = ""
        for a in encontrados:
            texto_archivos = texto_archivos + "- " + a + "\n"
        return texto_archivos

    return "No entendi el mensaje, " + NOMBRE_AGENTE + " solo sabe calcular, tareas, resumir y buscar archivos"


def main():
    print("Hola, soy " + NOMBRE_AGENTE)
    while True:
        mensaje = input("Tu: ")
        if mensaje.lower() == "salir":
            break
        respuesta = responder_mensaje(mensaje)
        print(NOMBRE_AGENTE + ": " + respuesta)


if __name__ == "__main__":
    main()
