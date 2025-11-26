#!/bin/bash
# Script para lanzar el dashboard de Superinvestors
# Usa el entorno virtual de QuantFlow

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Lanzando Dashboard Superinvestors...${NC}\n"

# Detectar la ruta del proyecto QuantFlow (dos niveles arriba)
QUANTFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PYTHON="$QUANTFLOW_DIR/.venv/bin/python"
VENV_STREAMLIT="$QUANTFLOW_DIR/.venv/bin/streamlit"

# Verificar que existe el entorno virtual
if [ ! -f "$VENV_STREAMLIT" ]; then
    echo "❌ Error: No se encontró streamlit en el entorno virtual de QuantFlow"
    echo "   Ejecuta primero: cd $QUANTFLOW_DIR && ./setup_venv.sh"
    exit 1
fi

# Cambiar al directorio del dashboard
cd "$(dirname "${BASH_SOURCE[0]}")"

echo -e "${GREEN}✅ Usando Python: $VENV_PYTHON${NC}"
echo -e "${GREEN}✅ Directorio: $(pwd)${NC}\n"

# Lanzar Streamlit
$VENV_STREAMLIT run main.py
