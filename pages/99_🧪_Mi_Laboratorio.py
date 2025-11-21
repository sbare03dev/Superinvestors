import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import sys
import os
from pathlib import Path

# --- 1. CONFIGURACIÓN DEL ENTORNO (CLAVE) ---
# Este bloque permite que el script acceda a las carpetas de tu proyecto Quantsys
try:
    # 1. Obtenemos la ruta del script actual
    current_path = Path(__file__).resolve()
    # 2. Subimos 4 niveles para llegar a la raíz de Quantsys:
    # pages/ -> superinvestors/ -> 6_Dashboards/ -> Quantsys/
    quantsys_root = current_path.parents[3]
    
    # 3. Añadimos esa ruta al Path de Python
    if str(quantsys_root) not in sys.path:
        sys.path.append(str(quantsys_root))
        # st.success(f"Ruta de Quantsys añadida: {quantsys_root}") # Descomentar para debug
    
    # --- INTENTO DE IMPORTACIÓN MODULAR ---
    # Asumimos que tienes una clase de estrategia en 1_Backtest/strategies/
    # Ejemplo: from 1_Backtest.strategies import LarryWilliamsMeanReversion
    
    # Reemplaza 'utilities' con la ruta real a tus módulos si el backtest está ahí
    from 1_Backtest.utilities.utils import DataFetcher  # Ejemplo de importación
    
    st.info("Conexión con la estructura de Quantsys exitosa. Lista para importar módulos.")

except ImportError as e:
    st.error(f"Error al importar módulos de Quantsys: {e}. Asegúrate de que el archivo existe y que tu 'quantsys_root' es correcto.")
    # Si la importación falla, usamos la versión sencilla que sólo usa yfinance
    st.stop()


# --- 2. INTERFAZ DE USUARIO Y LÓGICA DE CONTROL ---

st.set_page_config(layout="wide") 
st.title("🧪 Laboratorio Híbrido: Acceso Directo a Estrategias")
st.markdown("Ahora puedes usar la lógica de tus clases en `1_Backtest/strategies/`.")

# Aquí puedes listar todas tus estrategias de la carpeta 1_Backtest/strategies/
# Por simplicidad, usamos una lista hardcodeada por ahora.
estrategia_seleccionada = st.selectbox(
    "Selecciona una Estrategia de tu Repositorio:",
    ("Larry Williams Mean Reversion (RSI < 15)", "Custom MACD Crossover", "Estrategia ML de 4_Modelos")
)

# Simulamos la carga de la clase de la estrategia seleccionada
class MockStrategyExecutor:
    """Clase para simular que hemos cargado tu motor de backtest."""
    def __init__(self, ticker):
        self.ticker = ticker
        self.df = yf.download(ticker, period="3y", progress=False)

    def execute_logic(self, rsi_period, entry_level):
        """Simula la ejecución de la estrategia real."""
        self.df['RSI'] = self.df['Close'].rolling(rsi_period).mean() # Simulación
        self.df['Signal'] = 0
        self.df.loc[self.df['RSI'] < entry_level, 'Signal'] = 1
        self.df['Cumulative_Returns'] = (1 + self.df['Close'].pct_change()).cumprod()
        return self.df

# Parámetros en la barra lateral
st.sidebar.header("Parámetros de la Estrategia")
ticker_analizar = st.sidebar.text_input("Ticker a Analizar:", value="AAPL")
rsi_period = st.sidebar.slider("Período del RSI", 2, 14, 2)
entrada_rsi = st.sidebar.slider("Umbral de Entrada (RSI <)", 10, 30, 15)


# --- 3. DASHBOARD Y EJECUCIÓN ---

if st.button(f"▶️ Ejecutar Estrategia: {estrategia_seleccionada}"):
    st.markdown("---")
    
    # 1. Ejecutar el backtest (Usando tu lógica importada)
    executor = MockStrategyExecutor(ticker_analizar)
    results = executor.execute_logic(rsi_period, entrada_rsi)
    
    # 2. Visualización
    fig_equity = go.Figure()
    fig_equity.add_trace(go.Scatter(x=results.index, y=results['Cumulative_Returns'], name="Curva de Capital"))
    
    # Marcar Señales de Compra (simuladas)
    buy_signals = results[results['Signal'] == 1]
    fig_equity.add_trace(go.Scatter(
        x=buy_signals.index,
        y=buy_signals['Close'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=8, color='green'),
        name='Señal de Compra'
    ))

    fig_equity.update_layout(title=f"Rendimiento de {estrategia_seleccionada} en {ticker_analizar}", 
                             xaxis_title="Fecha", yaxis_title="Retorno Acumulado", 
                             height=500)
    st.plotly_chart(fig_equity, use_container_width=True)

    st.subheader(f"Resumen de {ticker_analizar}")
    st.dataframe(results[['Close', 'RSI', 'Signal']].tail(10)) # Muestra las últimas 10 filas
    