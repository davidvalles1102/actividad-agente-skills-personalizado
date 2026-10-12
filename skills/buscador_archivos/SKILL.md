---
name: buscador_archivos
description: Busca archivos por nombre dentro de la carpeta data/ del proyecto.
triggers:
  - busca archivo
  - encuentra archivo
  - buscar archivo
---

# Skill: Buscador de Archivos

## Que hace
Recorre recursivamente la carpeta `data/` buscando archivos cuyo nombre
contenga el patron indicado por el usuario.

## Cuando se activa
Cuando el mensaje contiene "busca archivo", "encuentra archivo" o
"buscar archivo".

## Entrada
`busca archivo <patron>`, por ejemplo `"busca archivo tareas"`.

## Salida
Lista de rutas relativas a `data/` que coinciden, o un mensaje indicando
que no se encontraron coincidencias.

## Ejemplo de uso
```
Tu: busca archivo ejemplo
Rex [skill:buscador_archivos]: Archivos encontrados:
- ejemplo_texto.txt
```

## Notas de diseno
A diferencia del `os.walk(".")` del proyecto original (que recorria todo
el directorio de trabajo), esta skill limita la busqueda a `data/` de
forma explicita via `AgentContext.data_dir`.
