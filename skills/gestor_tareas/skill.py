"""Skill: gestor_tareas.

Persiste las tareas en <data_dir>/tareas.json, en vez de en una lista en
memoria como en legacy/agente_monolitico.py (donde se perdian al cerrar
el programa).
"""
from __future__ import annotations

import json
from pathlib import Path


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, tasks: list[dict]) -> None:
    path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def run(message: str, context) -> str:
    tasks_path = context.data_dir / "tareas.json"
    tasks = _load(tasks_path)
    lowered = message.lower()

    if "completa" in lowered:
        digits = "".join(ch for ch in message if ch.isdigit())
        if not digits:
            return "Indica el numero de tarea a completar, por ejemplo: 'completa tarea 1'."
        index = int(digits) - 1
        if 0 <= index < len(tasks):
            tasks[index]["hecha"] = True
            _save(tasks_path, tasks)
            return f"Tarea {index + 1} marcada como completada: {tasks[index]['texto']}"
        return f"No existe la tarea numero {index + 1}."

    if "lista" in lowered or "muestra" in lowered:
        if not tasks:
            return "No tienes tareas registradas todavia."
        lineas = [
            f"{i + 1}. [{'x' if t['hecha'] else ' '}] {t['texto']}"
            for i, t in enumerate(tasks)
        ]
        return "Tus tareas:\n" + "\n".join(lineas)

    for prefix in ("agrega tarea", "nueva tarea", "agregar tarea"):
        if prefix in lowered:
            texto = message[lowered.index(prefix) + len(prefix):].strip(" :")
            if not texto:
                return "Dime que tarea quieres agregar."
            tasks.append({"texto": texto, "hecha": False})
            _save(tasks_path, tasks)
            return f"Tarea agregada: '{texto}' (#{len(tasks)})"

    return "No entendi la instruccion de tareas. Prueba con 'agrega tarea', 'lista tareas' o 'completa tarea N'."
