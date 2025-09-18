# Calculadora de Punto Fijo (Web, Flask)

App web para resolver `f(x)=0` por método de Punto Fijo.

## Características
- Entrada de `f(x)` y `g(x)` (opcional).
- Autodespeje asistido para sugerir `g(x)`.
- Iteración con tolerancia y/o iteraciones máximas.
- Tabla de resultados embebida.
- Teclado virtual para insertar funciones.
- Advertencias de convergencia (|g’(x0)|).

## Requisitos
- Python 3.8+
- `pip install -r requirements.txt`

## Ejecución
```bash
python run.py