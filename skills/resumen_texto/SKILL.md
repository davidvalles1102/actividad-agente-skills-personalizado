---
name: resumen_texto
description: Genera un resumen breve de un texto o archivo, usando el proveedor LLM del agente si esta disponible, o un resumen extractivo local en caso contrario.
triggers:
  - resume
  - resumen
  - resumeme
---

# Skill: Resumen de Texto

## Que hace
Produce un resumen corto de un texto. Si el agente tiene configurado un
proveedor de LLM real (Anthropic u OpenAI, con su respectiva API key), le
pide el resumen al modelo. Si no hay proveedor real disponible, aplica un
resumen extractivo simple (toma las primeras oraciones) sin depender de
ningun servicio externo.

## Cuando se activa
Cuando el mensaje incluye "resume", "resumen" o "resumeme".

## Formas de uso
- `resume: <texto a resumir>` -> resume el texto incluido en el mensaje.
- `resume archivo <nombre_archivo>` -> busca el archivo en `data/` y lo resume.

## Ejemplo de uso
```
Tu: resume archivo ejemplo_texto.txt
Ada [skill:resumen_texto]: Resumen (extractivo):
Los sistemas agenticos combinan modelos de lenguaje con herramientas externas...
```

## Notas de diseno
Esta es la unica skill que usa `AgentContext.provider` directamente,
mostrando como una skill puede apoyarse en el flujo LLM del agente en vez
de limitarse a logica determinista, sin acoplarse a un proveedor concreto
(Anthropic, OpenAI o Mock son intercambiables sin tocar este archivo).
