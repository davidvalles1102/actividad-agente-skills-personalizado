---
name: calculadora
description: Resuelve expresiones matematicas basicas (+, -, *, /, %, potencias) de forma segura, sin usar eval() sobre texto libre.
triggers:
  - calcula
  - cuanto es
  - resultado de
  - suma
  - resta
  - multiplica
  - divide
---

# Skill: Calculadora

## Que hace
Evalua expresiones aritmeticas simples contenidas en el mensaje del
usuario usando el modulo `ast` de Python, permitiendo unicamente un
conjunto explicito de operadores numericos (sin `eval()` directo sobre
texto arbitrario, a diferencia de `legacy/agente_monolitico.py`).

## Cuando se activa
Cuando el mensaje del usuario contiene alguno de los `triggers` definidos
arriba (por ejemplo "calcula", "cuanto es", o palabras como "suma"/"resta").

## Entrada
Un mensaje de texto que incluya una expresion numerica, por ejemplo:
`"calcula 12 * (4 + 1)"`.

## Salida
Una linea de texto con el resultado, por ejemplo:
`"El resultado de 12 * (4 + 1) es 60."`

## Ejemplo de uso
```
Tu: calcula 10 / 2 + 3
Ada [skill:calculadora]: El resultado de 10 / 2 + 3 es 8.0.
```

## Notas de diseno
Se usa `ast.parse` + un mapeo explicito de operadores permitidos en vez de
`eval()` para evitar ejecucion de codigo arbitrario, que es precisamente
el riesgo de seguridad presente en la version monolitica original.
