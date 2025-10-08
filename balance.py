import streamlit as st
import pandas as pd
import datetime
from datetime import date
import json
import os

# Configuración de la página
st.set_page_config(
    page_title="Balance Diario",
    page_icon="💰",
    layout="wide"
)

# Archivo para guardar los datos
DATA_FILE = "balance_data.json"

def cargar_datos():
    """Cargar datos desde el archivo JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "ventas": [],
        "gastos": [],
        "tasas_cambio": []
    }

def guardar_datos(datos):
    """Guardar datos en el archivo JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def inicializar_session_state():
    """Inicializar variables de session state"""
    if 'datos' not in st.session_state:
        st.session_state.datos = cargar_datos()

# Clasificación de gastos
CLASIFICACION_GASTOS = [
    "Gastos administrativos",
    "Gastos Mantenimiento", 
    "Gastos Nómina",
    "Gastos Venta",
    "Gastos x Compras Materia Prima"
]

def main():
    st.title("💰 Balance Diario")
    st.markdown("Sistema para llevar el control de ventas y gastos diarios")
    
    inicializar_session_state()
    
    # Sidebar para navegación
    st.sidebar.title("Navegación")
    opcion = st.sidebar.radio(
        "Selecciona una opción:",
        ["🏠 Inicio", "💵 Registrar Ventas", "💳 Registrar Gastos", "📊 Ver Balance", "⚙️ Configurar Tasa"]
    )
    
    if opcion == "🏠 Inicio":
        mostrar_inicio()
    elif opcion == "💵 Registrar Ventas":
        registrar_ventas()
    elif opcion == "💳 Registrar Gastos":
        registrar_gastos()
    elif opcion == "📊 Ver Balance":
        ver_balance()
    elif opcion == "⚙️ Configurar Tasa":
        configurar_tasa()

def mostrar_inicio():
    """Pantalla de inicio con resumen"""
    st.header("Resumen del Día")
    
    hoy = date.today().isoformat()
    ventas_hoy = [v for v in st.session_state.datos['ventas'] if v['fecha'] == hoy]
    gastos_hoy = [g for g in st.session_state.datos['gastos'] if g['fecha'] == hoy]
    
    # Obtener la tasa más reciente
    tasa_actual = obtener_tasa_actual()
    
    if tasa_actual:
        st.success(f"💱 Tasa de cambio actual: {tasa_actual:,.2f} Bs/$")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_ventas_bs = sum(v['monto_bs'] for v in ventas_hoy)
        total_ventas_usd = total_ventas_bs / tasa_actual if tasa_actual else 0
        st.metric("💰 Ventas Hoy (Bs)", f"Bs. {total_ventas_bs:,.2f}")
        st.metric("💰 Ventas Hoy ($)", f"$ {total_ventas_usd:,.2f}")
    
    with col2:
        total_gastos_bs = sum(g['monto_bs'] for g in gastos_hoy)
        total_gastos_usd = total_gastos_bs / tasa_actual if tasa_actual else 0
        st.metric("💳 Gastos Hoy (Bs)", f"Bs. {total_gastos_bs:,.2f}")
        st.metric("💳 Gastos Hoy ($)", f"$ {total_gastos_usd:,.2f}")
    
    with col3:
        balance_bs = total_ventas_bs - total_gastos_bs
        balance_usd = total_ventas_usd - total_gastos_usd
        st.metric("⚖️ Balance Hoy (Bs)", f"Bs. {balance_bs:,.2f}")
        st.metric("⚖️ Balance Hoy ($)", f"$ {balance_usd:,.2f}")

def obtener_tasa_actual():
    """Obtener la tasa de cambio más reciente"""
    if st.session_state.datos['tasas_cambio']:
        return max(st.session_state.datos['tasas_cambio'], 
                  key=lambda x: x['fecha'])['tasa']
    return None

def registrar_ventas():
    """Registrar nuevas ventas"""
    st.header("💵 Registrar Ventas")
    
    # Obtener tasa actual
    tasa_actual = obtener_tasa_actual()
    if tasa_actual:
        st.info(f"Tasa de cambio actual: {tasa_actual:,.2f} Bs/$")
    else:
        st.warning("⚠️ No hay tasa de cambio configurada. Ve a 'Configurar Tasa' primero.")
    
    with st.form("form_ventas"):
        fecha = st.date_input("Fecha", value=datetime.date.today())
        
        col1, col2 = st.columns(2)
        
        with col1:
            punto_venta = st.number_input("Punto de venta (Bs)", min_value=0.0, value=0.0, step=100.0)
            dolar_cash = st.number_input("$ Cash (Bs)", min_value=0.0, value=0.0, step=100.0)
        
        with col2:
            venta_externa = st.number_input("Venta externa (Bs)", min_value=0.0, value=0.0, step=100.0)
            bs_cash = st.number_input("Bs. Cash (Bs)", min_value=0.0, value=0.0, step=100.0)
        
        descripcion = st.text_input("Descripción (opcional)")
        
        submitted = st.form_submit_button("💾 Guardar Venta")
        
        if submitted:
            if tasa_actual is None:
                st.error("Debes configurar una tasa de cambio primero")
                return
                
            total_bs = punto_venta + dolar_cash + venta_externa + bs_cash
            total_usd = total_bs / tasa_actual
            
            nueva_venta = {
                'fecha': fecha.isoformat(),
                'punto_venta_bs': punto_venta,
                'dolar_cash_bs': dolar_cash,
                'venta_externa_bs': venta_externa,
                'bs_cash_bs': bs_cash,
                'total_bs': total_bs,
                'total_usd': total_usd,
                'descripcion': descripcion,
                'tasa_cambio': tasa_actual
            }
            
            st.session_state.datos['ventas'].append(nueva_venta)
            guardar_datos(st.session_state.datos)
            
            st.success(f"✅ Venta registrada exitosamente! Total: Bs. {total_bs:,.2f} (${total_usd:,.2f})")
            
            # Mostrar resumen
            st.subheader("Resumen de la Venta")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**En Bolívares:**")
                st.write(f"Punto de venta: Bs. {punto_venta:,.2f}")
                st.write(f"$ Cash: Bs. {dolar_cash:,.2f}")
                st.write(f"Venta externa: Bs. {venta_externa:,.2f}")
                st.write(f"Bs. Cash: Bs. {bs_cash:,.2f}")
                st.write(f"**Total: Bs. {total_bs:,.2f}**")
            
            with col2:
                st.write("**En Dólares:**")
                st.write(f"Punto de venta: $ {punto_venta/tasa_actual:,.2f}")
                st.write(f"$ Cash: $ {dolar_cash/tasa_actual:,.2f}")
                st.write(f"Venta externa: $ {venta_externa/tasa_actual:,.2f}")
                st.write(f"Bs. Cash: $ {bs_cash/tasa_actual:,.2f}")
                st.write(f"**Total: $ {total_usd:,.2f}**")

def registrar_gastos():
    """Registrar nuevos gastos"""
    st.header("💳 Registrar Gastos")
    
    tasa_actual = obtener_tasa_actual()
    if tasa_actual:
        st.info(f"Tasa de cambio actual: {tasa_actual:,.2f} Bs/$")
    else:
        st.warning("⚠️ No hay tasa de cambio configurada. Ve a 'Configurar Tasa' primero.")
    
    with st.form("form_gastos"):
        fecha = st.date_input("Fecha", value=datetime.date.today())
        clasificacion = st.selectbox("Clasificación del Gasto", CLASIFICACION_GASTOS)
        descripcion = st.text_input("Descripción del Gasto")
        monto_bs = st.number_input("Monto en Bolívares", min_value=0.0, value=0.0, step=10.0)
        
        submitted = st.form_submit_button("💾 Guardar Gasto")
        
        if submitted:
            if tasa_actual is None:
                st.error("Debes configurar una tasa de cambio primero")
                return
                
            monto_usd = monto_bs / tasa_actual
            
            nuevo_gasto = {
                'fecha': fecha.isoformat(),
                'clasificacion': clasificacion,
                'descripcion': descripcion,
                'monto_bs': monto_bs,
                'monto_usd': monto_usd,
                'tasa_cambio': tasa_actual
            }
            
            st.session_state.datos['gastos'].append(nuevo_gasto)
            guardar_datos(st.session_state.datos)
            
            st.success(f"✅ Gasto registrado exitosamente! Monto: Bs. {monto_bs:,.2f} (${monto_usd:,.2f})")

def ver_balance():
    """Mostrar balance completo"""
    st.header("📊 Balance General")
    
    tasa_actual = obtener_tasa_actual()
    if tasa_actual:
        st.info(f"💱 Tasa de cambio actual: {tasa_actual:,.2f} Bs/$")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha inicio", value=datetime.date.today() - datetime.timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Fecha fin", value=datetime.date.today())
    
    # Convertir a string para comparación
    fecha_inicio_str = fecha_inicio.isoformat()
    fecha_fin_str = fecha_fin.isoformat()
    
    # Filtrar datos
    ventas_filtradas = [v for v in st.session_state.datos['ventas'] 
                       if fecha_inicio_str <= v['fecha'] <= fecha_fin_str]
    gastos_filtrados = [g for g in st.session_state.datos['gastos'] 
                       if fecha_inicio_str <= g['fecha'] <= fecha_fin_str]
    
    # Métricas principales
    total_ventas_bs = sum(v['total_bs'] for v in ventas_filtradas)
    total_ventas_usd = sum(v['total_usd'] for v in ventas_filtradas)
    total_gastos_bs = sum(g['monto_bs'] for g in gastos_filtrados)
    total_gastos_usd = sum(g['monto_usd'] for g in gastos_filtrados)
    balance_bs = total_ventas_bs - total_gastos_bs
    balance_usd = total_ventas_usd - total_gastos_usd
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total Ventas (Bs)", f"Bs. {total_ventas_bs:,.2f}")
        st.metric("💰 Total Ventas ($)", f"$ {total_ventas_usd:,.2f}")
    with col2:
        st.metric("💳 Total Gastos (Bs)", f"Bs. {total_gastos_bs:,.2f}")
        st.metric("💳 Total Gastos ($)", f"$ {total_gastos_usd:,.2f}")
    with col3:
        st.metric("⚖️ Balance Total (Bs)", f"Bs. {balance_bs:,.2f}")
        st.metric("⚖️ Balance Total ($)", f"$ {balance_usd:,.2f}")
    
    # Tabs para detalles
    tab1, tab2, tab3 = st.tabs(["📈 Detalle Ventas", "📉 Detalle Gastos", "📋 Resumen por Clasificación"])
    
    with tab1:
        if ventas_filtradas:
            df_ventas = pd.DataFrame(ventas_filtradas)
            st.subheader("Detalle de Ventas")
            st.dataframe(df_ventas, use_container_width=True)
        else:
            st.info("No hay ventas registradas en el período seleccionado")
    
    with tab2:
        if gastos_filtrados:
            df_gastos = pd.DataFrame(gastos_filtrados)
            st.subheader("Detalle de Gastos")
            st.dataframe(df_gastos, use_container_width=True)
        else:
            st.info("No hay gastos registrados en el período seleccionado")
    
    with tab3:
        if gastos_filtrados:
            df_gastos_clasif = pd.DataFrame(gastos_filtrados)
            resumen_clasif = df_gastos_clasif.groupby('clasificacion').agg({
                'monto_bs': 'sum',
                'monto_usd': 'sum'
            }).reset_index()
            
            st.subheader("Gastos por Clasificación")
            st.dataframe(resumen_clasif, use_container_width=True)
            
            # Gráfico de gastos por clasificación
            st.subheader("Distribución de Gastos")
            chart_data = resumen_clasif.set_index('clasificacion')['monto_usd']
            st.bar_chart(chart_data)
        else:
            st.info("No hay gastos para mostrar el resumen por clasificación")

def configurar_tasa():
    """Configurar tasa de cambio"""
    st.header("⚙️ Configurar Tasa de Cambio")
    
    tasa_actual = obtener_tasa_actual()
    if tasa_actual:
        st.success(f"Tasa de cambio actual: **{tasa_actual:,.2f} Bs/$**")
    
    with st.form("form_tasa"):
        nueva_tasa = st.number_input(
            "Nueva Tasa de Cambio (Bs/$)",
            min_value=1.0,
            value=tasa_actual if tasa_actual else 1.0,
            step=0.1
        )
        fecha_tasa = st.date_input("Fecha de la tasa", value=datetime.date.today())
        
        submitted = st.form_submit_button("💾 Guardar Tasa")
        
        if submitted:
            nueva_tasa_info = {
                'fecha': fecha_tasa.isoformat(),
                'tasa': nueva_tasa
            }
            
            st.session_state.datos['tasas_cambio'].append(nueva_tasa_info)
            guardar_datos(st.session_state.datos)
            
            st.success(f"✅ Tasa de cambio guardada: {nueva_tasa:,.2f} Bs/$")
    
    # Historial de tasas
    if st.session_state.datos['tasas_cambio']:
        st.subheader("Historial de Tasas")
        df_tasas = pd.DataFrame(st.session_state.datos['tasas_cambio'])
        df_tasas['fecha'] = pd.to_datetime(df_tasas['fecha'])
        df_tasas = df_tasas.sort_values('fecha', ascending=False)
        st.dataframe(df_tasas, use_container_width=True)

if __name__ == "__main__":
    main()
