# -*- coding: utf-8 -*-
"""
Utilidades de parseo y formateo para la Calculadora de Punto Fijo (Web).
"""
import math
from typing import Any, Optional

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

# Símbolo principal
x = sp.symbols('x')

# Transformaciones para permitir multiplicación implícita y ^ como potencia
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# Nombres permitidos para el parser (seguridad básica)
PARSE_LOCALS = {
    "x": x,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "cot": sp.cot, "sec": sp.sec, "csc": sp.csc,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt, "Abs": sp.Abs,
    "pi": sp.pi, "E": sp.E,
}

def sanitize(s: str) -> str:
    """Normaliza funciones y símbolos comunes en español."""
    if s is None:
        return ""
    s = s.strip()
    s = s.replace("sen", "sin")
    s = s.replace("tg", "tan")
    s = s.replace("ctg", "cot")
    s = s.replace("ln", "log")
    s = s.replace("√", "sqrt")
    s = s.replace("π", "pi")
    s = s.replace("e^(", "exp(")  # caso simple
    return s

def parse_to_expr(text: str) -> sp.Expr:
    """Convierte texto a expresión SymPy segura, con multiplicación implícita."""
    text = sanitize(text)
    return parse_expr(text, transformations=TRANSFORMATIONS, local_dict=PARSE_LOCALS, evaluate=True)

def parse_fx(s: str) -> sp.Expr:
    """
    Convierte la entrada de f(x) a f(x) tal que f(x)=0 (permite 'lhs = rhs').
    Lanza ValueError si no depende de x o si el formato es inválido.
    """
    s = (s or "").strip()
    if not s:
        raise ValueError("Ingresa la ecuación f(x) = 0.")
    s = sanitize(s)
    if "=" in s:
        parts = s.split("=")
        if len(parts) != 2:
            raise ValueError("Usa solo un signo '=' en f(x).")
        lhs = parse_to_expr(parts[0])
        rhs = parse_to_expr(parts[1])
        expr = sp.simplify(lhs - rhs)
    else:
        expr = parse_to_expr(s)
    if x not in expr.free_symbols:
        raise ValueError("La expresión f(x) debe depender de x.")
    return sp.simplify(expr)

def parse_gx(s: str) -> sp.Expr:
    """
    Convierte entrada de g(x). Soporta 'x = ...' o '... = x'.
    Retorna la expresión g(x).
    """
    s = (s or "").strip()
    if not s:
        raise ValueError("g(x) vacío.")
    s = sanitize(s)
    if "=" in s:
        parts = s.split("=")
        if len(parts) != 2:
            raise ValueError("Usa solo un signo '=' en g(x).")
        left = parse_to_expr(parts[0])
        right = parse_to_expr(parts[1])
        if left == x:
            g = right
        elif right == x:
            g = left
        else:
            g = right
    else:
        g = parse_to_expr(s)
    return sp.simplify(g)

def to_complex(val: Any) -> Optional[complex]:
    """Intenta convertir un valor a número complejo de Python."""
    try:
        return complex(val)
    except Exception:
        try:
            return complex(sp.N(val))
        except Exception:
            return None

def is_finite_real(val: Any) -> bool:
    """True si val es un real finito."""
    try:
        vf = float(val)
        return math.isfinite(vf)
    except Exception:
        return False

def fmt_num(val: Any, sig: int = 12) -> str:
    """Formato amigable para números (también complejos)."""
    try:
        c = to_complex(val)
        if c is None or (isinstance(c, complex) and (math.isnan(c.real) or math.isnan(c.imag))):
            return "nan"
        if abs(c.imag) < 1e-12:
            return f"{float(c.real):.{sig}g}"
        sign = "+" if c.imag >= 0 else "-"
        return f"{float(c.real):.{sig}g}{sign}{abs(float(c.imag)):.{sig}g}i"
    except Exception:
        try:
            return f"{float(val):.{sig}g}"
        except Exception:
            return str(val)