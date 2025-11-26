import streamlit as st
import pandas as pd
import numpy as np
import os
import glob

st.set_page_config(page_title="Quantified Strategies", page_icon="📈", layout="wide")

st.title("📈 Quantified Strategies Analysis")

# Configuración de rutas
RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), 
    "../..",  # Sube a 6_Dashboards/
    "../E_Analisis_Resultados/quantified_strategies/"  # Sube a QuantFlow/
)
RESULTS_DIR = os.path.abspath(RESULTS_DIR)

st.sidebar.header("Configuración")

if not os.path.exists(RESULTS_DIR):
    st.error(f"No se encontró el directorio de resultados: {RESULTS_DIR}")
    st.stop()

# Listar archivos de resultados
files = glob.glob(os.path.join(RESULTS_DIR, "*.csv"))
file_names = [os.path.basename(f) for f in files]

if not file_names:
    st.warning("No se encontraron resultados de backtest.")
    st.info("Ejecuta un backtest en QuantFlow y exporta los resultados a CSV.")
else:
    selected_file = st.sidebar.selectbox("Seleccionar Estrategia", file_names)
    
    if selected_file:
        file_path = os.path.join(RESULTS_DIR, selected_file)
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        
        st.subheader(f"📊 {selected_file.replace('.csv', '').replace('_', ' ').title()}")
        
        # === MÉTRICAS PRINCIPALES ===
        st.markdown("### 📈 Métricas de Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Retorno Total
        if 'Equity' in df.columns:
            total_return = (df['Equity'].iloc[-1] - 1) * 100
            col1.metric("Retorno Total", f"{total_return:.2f}%")
            
            # CAGR
            years = (df.index[-1] - df.index[0]).days / 365.25
            cagr = ((df['Equity'].iloc[-1] ** (1/years)) - 1) * 100
            col2.metric("CAGR", f"{cagr:.2f}%")
        
        # Sharpe Ratio
        if 'Strategy_Returns' in df.columns:
            returns = df['Strategy_Returns'].dropna()
            sharpe = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0
            col3.metric("Sharpe Ratio", f"{sharpe:.2f}")
        
        # Max Drawdown
        if 'Equity' in df.columns:
            cumulative = df['Equity']
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_dd = drawdown.min() * 100
            col4.metric("Max Drawdown", f"{max_dd:.2f}%")
        
        # === GRÁFICO DE EQUIDAD ===
        st.markdown("### 📉 Curva de Equidad")
        
        if 'Equity' in df.columns:
            # Crear Buy & Hold para comparación
            if 'Close' in df.columns:
                df['Buy_Hold'] = df['Close'] / df['Close'].iloc[0]
            
            chart_data = df[['Equity']].copy()
            if 'Buy_Hold' in df.columns:
                chart_data['Buy & Hold'] = df['Buy_Hold']
            
            st.line_chart(chart_data, height=400)
        
        # === ESTADÍSTICAS ADICIONALES ===
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Estadísticas de Trading")
            if 'Strategy_Returns' in df.columns:
                returns = df['Strategy_Returns'].dropna()
                winning_trades = (returns > 0).sum()
                total_trades = (returns != 0).sum()
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                stats = {
                    "Total Trades": int(total_trades),
                    "Win Rate": f"{win_rate:.2f}%",
                    "Avg Win": f"{returns[returns > 0].mean() * 100:.2f}%" if len(returns[returns > 0]) > 0 else "N/A",
                    "Avg Loss": f"{returns[returns < 0].mean() * 100:.2f}%" if len(returns[returns < 0]) > 0 else "N/A"
                }
                st.table(pd.DataFrame(stats.items(), columns=["Métrica", "Valor"]))
        
        with col2:
            st.markdown("### 📅 Información del Periodo")
            info = {
                "Inicio": df.index[0].strftime('%Y-%m-%d'),
                "Fin": df.index[-1].strftime('%Y-%m-%d'),
                "Días": len(df),
                "Años": f"{years:.2f}" if 'Equity' in df.columns else "N/A"
            }
            st.table(pd.DataFrame(info.items(), columns=["Campo", "Valor"]))
        
        # === DATOS COMPLETOS ===
        with st.expander("📋 Ver Datos Completos"):
            st.dataframe(df, height=400)
