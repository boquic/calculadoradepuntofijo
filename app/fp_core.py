# -*- coding: utf-8 -*-
"""
Lógica del método de punto fijo: autodespeje, derivadas e iteración.
"""
import math
from typing import Optional, Tuple, List, Dict

import sympy as sp
from .parser_utils import x, fmt_num, to_complex

def auto_g_from_f(f_expr: sp.Expr, x0_val: float) -> Tuple[sp.Expr, str]:
    """
    Intenta sugerir g(x) automáticamente:
      1) f = A - x -> g = A
      2) f = x - A -> g = A
      3) g = x - λ f(x), con λ ≈ 1/f'(x0)
    """
    A = sp.Wild('A')
    # Patrón f = A - x
    m1 = f_expr.match(A - x)
    if m1 is not None:
        g = sp.simplify(m1[A])
        return g, "Detectado patrón: f(x) = A - x → g(x) = A"
    # Patrón f = x - A
    m2 = f_expr.match(x - A)
    if m2 is not None:
        g = sp.simplify(m2[A])
        return g, "Detectado patrón: f(x) = x - A → g(x) = A"

    # Estrategia λ: g(x) = x - λ f(x)
    try:
        fprime = sp.diff(f_expr, x)
        fp0 = float(fprime.subs(x, x0_val))
        lam = 1.0 / fp0 if abs(fp0) > 1e-14 and math.isfinite(fp0) else 1.0
    except Exception:
        lam = 1.0
    g = sp.simplify(x - sp.N(lam) * f_expr)
    return g, f"Usando g(x) = x - λ f(x), con λ ≈ {fmt_num(lam)} (basado en f'(x0))"

def lambdify_expr(expr: sp.Expr):
    """Crea función numérica a partir de una expresión SymPy."""
    try:
        f = sp.lambdify(x, expr, modules=["math", "sympy"])
        _ = f(0.1)  # prueba rápida
        return f
    except Exception:
        return sp.lambdify(x, expr, modules="sympy")

def compute_derivative_at(g_expr: sp.Expr, x0_val: float):
    """Calcula g'(x0) si es posible."""
    try:
        gprime = sp.diff(g_expr, x)
        val = gprime.subs(x, x0_val)
        valf = float(val)
        return valf, gprime
    except Exception:
        return None, None

def iterate_fixed_point(
    g_expr: sp.Expr,
    x0: float,
    tol: Optional[float],
    max_it: int,
    error_tipo: str = "Absoluto",
) -> Tuple[List[Dict[str, str]], float, bool]:
    """
    Ejecuta la iteración de punto fijo.
    Retorna:
      - rows: lista de dicts con n, xn, gxn, err (ya formateados)
      - xn_final: último valor
      - convergio: bool según criterio de tolerancia
    """
    g_fun = lambdify_expr(g_expr)
    rows: List[Dict[str, str]] = []
    xn = x0
    convergio = False

    for n in range(max_it):
        try:
            gxn = g_fun(xn)
        except Exception as e:
            rows.append({"n": n, "xn": fmt_num(xn), "gxn": "error", "err": f"eval: {e}"})
            break

        # Error (soporta reales/Complejos)
        try:
            cxn = to_complex(xn)
            cgxn = to_complex(gxn)
            if cxn is not None and cgxn is not None:
                if error_tipo == "Relativo":
                    denom = abs(cgxn) if abs(cgxn) > 1e-30 else 1.0
                    err_val = abs(cgxn - cxn) / denom
                else:
                    err_val = abs(cgxn - cxn)
            else:
                err_val = float('nan')
        except Exception:
            err_val = float('nan')

        rows.append({
            "n": n,
            "xn": fmt_num(xn),
            "gxn": fmt_num(gxn),
            "err": fmt_num(err_val),
        })

        if tol is not None and isinstance(err_val, (float, int)) and math.isfinite(err_val) and err_val < tol:
            convergio = True
            xn = gxn
            break

        xn = gxn

    return rows, xn, convergio