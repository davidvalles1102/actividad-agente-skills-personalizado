"""Skill: calculadora.

Evalua expresiones aritmeticas de forma segura usando `ast`, en vez de
`eval()` sobre texto libre del usuario (ese era el riesgo de seguridad
en legacy/agente_monolitico.py).
"""
from __future__ import annotations

import ast
import operator
import re

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("expresion no permitida")


def _extract_expression(message: str) -> str:
    match = re.search(r"[-+/*%().\d\s]{2,}", message)
    if not match or not any(ch.isdigit() for ch in match.group(0)):
        raise ValueError("no se encontro una expresion numerica en el mensaje")
    return match.group(0).strip()


def run(message: str, context) -> str:
    try:
        expr = _extract_expression(message)
    except ValueError as exc:
        return f"No pude calcular eso: {exc}."

    try:
        tree = ast.parse(expr, mode="eval")
        resultado = _safe_eval(tree)
    except Exception as exc:
        return f"No pude calcular '{expr}': {exc}."

    return f"El resultado de {expr} es {resultado}."
