import os, sys
# Inserta /app (raíz del backend en el contenedor) en sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)
