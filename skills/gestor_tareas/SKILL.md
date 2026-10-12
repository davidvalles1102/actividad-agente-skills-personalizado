---
name: gestor_tareas
description: Administra una lista de tareas pendientes (agregar, listar y completar), persistida en data/tareas.json.
triggers:
  - tarea
  - tareas
---

# Skill: Gestor de Tareas

## Que hace
Permite agregar, listar y marcar como completadas tareas guardadas en
`data/tareas.json`. Es la unica skill del proyecto con estado propio
entre conversaciones (a diferencia de la lista en memoria del proyecto
original, que se perdia al cerrar el programa).

## Cuando se activa
Cuando el mensaje contiene la palabra "tarea" o "tareas", combinada con
alguno de los comandos reconocidos.

## Comandos soportados
- `agrega tarea <texto>` / `nueva tarea <texto>` -> agrega una tarea.
- `lista tareas` / `muestra tareas` -> muestra todas las tareas con su estado.
- `completa tarea <n>` -> marca la tarea numero `n` como hecha.

## Ejemplo de uso
```
Tu: agrega tarea revisar el informe final
Ada [skill:gestor_tareas]: Tarea agregada: 'revisar el informe final' (#1)

Tu: lista tareas
Ada [skill:gestor_tareas]: Tus tareas:
1. [ ] revisar el informe final
```

## Notas de diseno
El estado se guarda en JSON plano (modulo estandar `json`) para evitar
dependencias externas y para que el archivo se pueda inspeccionar
facilmente durante la revision del proyecto.
