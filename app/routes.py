# -*- coding: utf-8 -*-
"""
Rutas y controladores de la app web (Blueprint principal).
"""
from typing import List, Dict
from flask import Blueprint, render_template, request

import sympy as sp

from .parser_utils import parse_fx, parse_gx, fmt_num
from .fp_core import auto_g_from_f, compute_derivative_at, iterate_fixed_point

bp = Blueprint("main", __name__)

def build_message(kind: str, text: str) -> Dict[str, str]:
    return {"kind": kind, "text": text}

@bp.route("/", methods=["GET", "POST"])
def index():
    # Valores por defecto
    fx_text = ""
    gx_text = ""
    x0_text = "0.5"
    tol_text = "1e-6"
    max_it_text = "50"
    error_tipo = "Absoluto"

    messages: List[Dict[str, str]] = []
    rows = []
    summary = "—"
    g_used = "—"
    gprime_info = "—"

    if request.method == "POST":
        action = request.form.get("action", "")
        fx_text = (request.form.get("fx") or "").strip()
        gx_text = (request.form.get("gx") or "").strip()
        x0_text = (request.form.get("x0") or "0.5").strip()
        tol_text = (request.form.get("tol") or "1e-6").strip()
        max_it_text = (request.form.get("max_it") or "50").strip()
        error_tipo = (request.form.get("error_tipo") or "Absoluto").strip()

        if action == "clear":
            messages.append(build_message("info", "Formulario reiniciado."))
            fx_text, gx_text, x0_text, tol_text, max_it_text, error_tipo = "", "", "0.5", "1e-6", "50", "Absoluto"
            return render_template("index.html", **locals())

        # Parseo de entradas
        try:
            f_expr = parse_fx(fx_text)
        except Exception as e:
            messages.append(build_message("error", f"Error en f(x): {e}"))
            return render_template("index.html", **locals())

        try:
            x0 = float(x0_text)
        except Exception:
            messages.append(build_message("error", "x0 debe ser un número real."))
            return render_template("index.html", **locals())

        # Sugerir g(x)
        if action == "suggest":
            try:
                g_expr, info_msg = auto_g_from_f(f_expr, x0)
                gx_text = str(g_expr)
                g_used = sp.sstr(g_expr)
                gprime_val, _ = compute_derivative_at(g_expr, x0)
                gprime_info = "no disponible" if gprime_val is None else f"≈ {fmt_num(gprime_val)}"
                messages.append(build_message("info", info_msg))
                if gprime_val is not None and abs(gprime_val) >= 1.0:
                    messages.append(build_message(
                        "warning",
                        "Se detectó |g'(x0)| ≥ 1. El método podría no converger. Considera revisar g(x) o cambiar x0."
                    ))
            except Exception as e:
                messages.append(build_message("error", f"No fue posible sugerir g(x): {e}"))
            return render_template("index.html", **locals())

        # Calcular
        if action == "calculate":
            # g(x) del usuario o sugerida
            try:
                if gx_text:
                    g_expr = parse_gx(gx_text)
                    info_msg = "Usando g(x) proporcionada por el usuario."
                else:
                    g_expr, info_msg = auto_g_from_f(f_expr, x0)
                    gx_text = str(g_expr)
            except Exception as e:
                messages.append(build_message("error", f"Error en g(x): {e}"))
                return render_template("index.html", **locals())

            g_used = sp.sstr(g_expr)

            # Tolerancia e iteraciones
            try:
                tol = float(tol_text)
                if tol <= 0:
                    tol = None
            except Exception:
                tol = None

            try:
                max_it = int(max_it_text)
                if max_it <= 0:
                    raise ValueError
            except Exception:
                messages.append(build_message("error", "Iteraciones máximas debe ser un entero positivo."))
                return render_template("index.html", **locals())

            # g'(x0)
            gprime_val, _ = compute_derivative_at(g_expr, x0)
            gprime_info = "no disponible" if gprime_val is None else f"≈ {fmt_num(gprime_val)}"
            if gprime_val is not None and abs(gprime_val) >= 1.0:
                messages.append(build_message(
                    "warning",
                    "Se detectó |g'(x0)| ≥ 1. El método podría divergir o converger lentamente."
                ))

            # Iteración
            rows, xn, convergio = iterate_fixed_point(
                g_expr=g_expr,
                x0=x0,
                tol=tol,
                max_it=max_it,
                error_tipo=error_tipo,
            )

            summary = " | ".join([
                info_msg,
                f"Resultado aproximado: x* ≈ {fmt_num(xn)}",
                f"Iteraciones realizadas: {len(rows)}",
                f"Criterio: {'|x_(n+1)-x_n| < tol' if tol is not None else 'máx. iteraciones'}",
                f"Convergió: {'Sí' if convergio else 'No (criterio no satisfecho)'}",
            ])

            return render_template("index.html", **locals())

    # GET o estado inicial
    return render_template("index.html", **locals())