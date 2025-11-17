import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.error("⚠️ Plotly ist nicht installiert. Bitte installieren Sie es mit: pip install plotly")
    st.stop()

# Seitenkonfiguration
st.set_page_config(
    page_title="EDUR PumpVision | Pump Monitoring System",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS im EDUR-Design (Petrol/Blau mit geschwungenen Elementen)
st.markdown("""
    <style>
    /* EDUR Farbschema */
    :root {
        --edur-petrol: #005C7F;
        --edur-light-blue: #A5D8E6;
        --edur-dark-blue: #003D54;
        --edur-accent: #7EC8E3;
    }
    
    /* Haupthintergrund */
    .main {
        background: linear-gradient(135deg, #f8fbfd 0%, #e8f4f8 100%);
    }
    
    /* Header mit EDUR-Welleneffekt */
    .edur-header {
        background: linear-gradient(135deg, var(--edur-petrol) 0%, var(--edur-dark-blue) 100%);
        color: white;
        padding: 25px;
        border-radius: 0 0 30px 30px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0, 92, 127, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .edur-header::after {
        content: '';
        position: absolute;
        bottom: -20px;
        left: 0;
        width: 100%;
        height: 40px;
        background: var(--edur-light-blue);
        opacity: 0.3;
        border-radius: 50% 50% 0 0 / 100% 100% 0 0;
    }
    
    .edur-logo-text {
        font-size: 2.5em;
        font-weight: bold;
        color: white;
        margin: 0;
        letter-spacing: 2px;
    }
    
    .edur-subtitle {
        font-size: 1.2em;
        color: var(--edur-light-blue);
        margin-top: 5px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--edur-petrol) 0%, var(--edur-dark-blue) 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid var(--edur-accent);
    }
    
    /* Metriken mit EDUR-Styling */
    .stMetric {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 92, 127, 0.15);
        border-top: 4px solid var(--edur-petrol);
    }
    
    /* Alarme im EDUR-Design */
    .alarm-high {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
        border-left: 5px solid #d32f2f;
        padding: 15px;
        margin: 8px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(211, 47, 47, 0.2);
    }
    
    .alarm-medium {
        background: linear-gradient(135deg, #fffbf0 0%, #fff4e0 100%);
        border-left: 5px solid #f57c00;
        padding: 15px;
        margin: 8px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(245, 124, 0, 0.2);
    }
    
    .alarm-low {
        background: linear-gradient(135deg, #f0f8ff 0%, #e3f2fd 100%);
        border-left: 5px solid var(--edur-petrol);
        padding: 15px;
        margin: 8px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 92, 127, 0.2);
    }
    
    /* Buttons im EDUR-Design */
    .stButton > button {
        background: linear-gradient(135deg, var(--edur-petrol) 0%, var(--edur-dark-blue) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 92, 127, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--edur-dark-blue) 0%, var(--edur-petrol) 100%);
        box-shadow: 0 6px 16px rgba(0, 92, 127, 0.4);
        transform: translateY(-2px);
    }
    
    /* Tabs im EDUR-Design */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 12px;
        padding: 5px;
        box-shadow: 0 2px 8px rgba(0, 92, 127, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: var(--edur-petrol);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--edur-petrol) 0%, var(--edur-dark-blue) 100%);
        color: white !important;
    }
    
    /* Welleneffekt für Abschnitte */
    .wave-divider {
        height: 30px;
        background: var(--edur-light-blue);
        opacity: 0.2;
        border-radius: 50% 50% 0 0 / 100% 100% 0 0;
        margin: 20px 0;
    }
    
    /* Footer im EDUR-Design */
    .edur-footer {
        background: linear-gradient(135deg, var(--edur-petrol) 0%, var(--edur-dark-blue) 100%);
        color: white;
        padding: 20px;
        border-radius: 30px 30px 0 0;
        margin-top: 40px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Simulierte Daten generieren
@st.cache_data
def generate_pump_data():
    pumps = []
    pump_types = ["Exzenterschneckenpumpe", "Kreiselpumpe", "Verdrängerpumpe"]
    locations = ["Halle A", "Halle B", "Halle C", "Außenbereich"]
    
    for i in range(1, 11):
        status_choice = np.random.choice(["OK", "Warnung", "Kritisch"], p=[0.7, 0.2, 0.1])
        pumps.append({
            "id": f"P-{i:03d}",
            "name": f"Pumpe {i}",
            "typ": np.random.choice(pump_types),
            "standort": np.random.choice(locations),
            "status": status_choice,
            "druck": np.random.uniform(1.5, 8.5),
            "druck_soll": 5.0,
            "temperatur": np.random.uniform(20, 85),
            "temp_max": 80,
            "vibration": np.random.uniform(0.5, 4.5),
            "vib_max": 4.0,
            "strom": np.random.uniform(10, 45),
            "durchfluss": np.random.uniform(5, 50),
            "betriebsstunden": np.random.uniform(1000, 15000),
            "naechste_wartung": np.random.randint(1, 90)
        })
    return pd.DataFrame(pumps)

@st.cache_data
def generate_alarm_data():
    alarms = []
    alarm_types = ["Druckabfall", "Überhitzung", "Erhöhte Vibration", "Stromspitze", "Durchfluss niedrig"]
    priorities = ["Hoch", "Mittel", "Niedrig"]
    
    for i in range(8):
        priority = np.random.choice(priorities, p=[0.3, 0.4, 0.3])
        alarms.append({
            "id": f"A-{i+1:03d}",
            "pumpe": f"P-{np.random.randint(1, 11):03d}",
            "typ": np.random.choice(alarm_types),
            "prioritaet": priority,
            "zeit": datetime.now() - timedelta(hours=np.random.randint(1, 48)),
            "status": np.random.choice(["Offen", "Quittiert", "Behoben"], p=[0.4, 0.3, 0.3]),
            "empfehlung": "Sofortige Inspektion erforderlich" if priority == "Hoch" else "Überwachung fortsetzen"
        })
    return pd.DataFrame(alarms)

@st.cache_data
def generate_historical_data(pump_id, days=7):
    dates = pd.date_range(end=datetime.now(), periods=days*24, freq='H')
    data = {
        'Zeit': dates,
        'Druck': np.random.uniform(4, 6, len(dates)) + np.sin(np.arange(len(dates))/12) * 0.5,
        'Temperatur': np.random.uniform(40, 60, len(dates)) + np.sin(np.arange(len(dates))/6) * 5,
        'Vibration': np.random.uniform(1, 3, len(dates)),
        'Strom': np.random.uniform(25, 35, len(dates))
    }
    return pd.DataFrame(data)

# Initialisierung
if 'pump_data' not in st.session_state:
    st.session_state.pump_data = generate_pump_data()
if 'alarm_data' not in st.session_state:
    st.session_state.alarm_data = generate_alarm_data()

# Sidebar Navigation mit EDUR-Branding
st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0; border-bottom: 2px solid rgba(255,255,255,0.2); margin-bottom: 20px;'>
        <h1 style='color: white; font-size: 2em; letter-spacing: 3px; margin: 0;'>EDUR</h1>
        <p style='color: #A5D8E6; font-size: 0.9em; margin: 5px 0 0 0;'>PumpVision®</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.title("🔧 Navigation")
page = st.sidebar.radio(
    "Bereich auswählen:",
    ["📊 Dashboard", "🔍 Pumpendetails", "⚠️ Alarmmanagement", "📈 Berichte & Analysen", "🛠️ Wartungsplanung"]
)

# Suchfunktion
st.sidebar.markdown("---")
st.sidebar.subheader("🔎 Schnellsuche")
search_term = st.sidebar.text_input("Pumpen-ID oder Standort")
pump_filter = st.sidebar.multiselect(
    "Pumpentyp filtern:",
    options=st.session_state.pump_data['typ'].unique()
)

# Daten filtern
filtered_data = st.session_state.pump_data.copy()
if search_term:
    filtered_data = filtered_data[
        filtered_data['id'].str.contains(search_term, case=False) |
        filtered_data['standort'].str.contains(search_term, case=False)
    ]
if pump_filter:
    filtered_data = filtered_data[filtered_data['typ'].isin(pump_filter)]

# ========== DASHBOARD ==========
if page == "📊 Dashboard":
    # EDUR Header
    st.markdown("""
        <div class="edur-header">
            <h1 class="edur-logo-text">EDUR PumpVision</h1>
            <p class="edur-subtitle">Intelligentes Pumpen-Monitoring System</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Übersicht auf einen Blick** • Letzte Aktualisierung: " + datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    
    # Top Metriken
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ok_count = len(filtered_data[filtered_data['status'] == 'OK'])
        st.metric("✅ Pumpen OK", ok_count, delta=None)
    
    with col2:
        warning_count = len(filtered_data[filtered_data['status'] == 'Warnung'])
        st.metric("⚠️ Warnungen", warning_count, delta=warning_count if warning_count > 0 else None)
    
    with col3:
        critical_count = len(filtered_data[filtered_data['status'] == 'Kritisch'])
        st.metric("❌ Kritisch", critical_count, delta=critical_count if critical_count > 0 else None, delta_color="inverse")
    
    with col4:
        total_hours = filtered_data['betriebsstunden'].sum()
        st.metric("⏱️ Gesamt-Betriebsstunden", f"{total_hours:,.0f} h")
    
    st.markdown("---")
    
    # Top 3 Alarme
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚨 Top 3 Alarmmeldungen")
        top_alarms = st.session_state.alarm_data[
            st.session_state.alarm_data['status'] == 'Offen'
        ].sort_values('prioritaet').head(3)
        
        if len(top_alarms) > 0:
            for _, alarm in top_alarms.iterrows():
                alarm_class = f"alarm-{alarm['prioritaet'].lower()}"
                st.markdown(f"""
                    <div class="{alarm_class}">
                        <strong>🔔 {alarm['typ']}</strong> - Pumpe {alarm['pumpe']}<br>
                        <small>Priorität: {alarm['prioritaet']} | {alarm['zeit'].strftime('%d.%m. %H:%M')}</small><br>
                        <small>💡 {alarm['empfehlung']}</small>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Keine offenen Alarme!")
    
    with col2:
        st.subheader("📊 24h Zusammenfassung")
        st.metric("Energieverbrauch", "1.247 kWh", delta="-3.2%")
        st.metric("Durchschn. Auslastung", "78%", delta="+5%")
        st.metric("Stillstandszeit", "2.3 h", delta="0.5 h", delta_color="inverse")
    
    st.markdown("---")
    
    # Pumpen-Übersicht
    st.subheader("🏭 Pumpen-Status Übersicht")
    
    # Status-Verteilung als Donut Chart
    status_counts = filtered_data['status'].value_counts()
    fig_status = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=.4,
        marker=dict(colors=['#4caf50', '#ff9800', '#f44336'])
    )])
    fig_status.update_layout(title="Status-Verteilung", height=300)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Pumpen-Tabelle
        display_cols = ['id', 'name', 'typ', 'standort', 'status', 'druck', 'temperatur']
        st.dataframe(
            filtered_data[display_cols].style.apply(
                lambda x: ['background-color: #c8e6c9' if v == 'OK' 
                          else 'background-color: #ffccbc' if v == 'Warnung'
                          else 'background-color: #ffcdd2' if v == 'Kritisch'
                          else '' for v in x],
                subset=['status']
            ),
            use_container_width=True,
            height=300
        )
    
    # Schnellzugriff-Buttons
    st.markdown("---")
    st.subheader("⚡ Schnellzugriff")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.button("🔧 Wartungsplan öffnen", use_container_width=True)
    with col2:
        st.button("📊 Berichte generieren", use_container_width=True)
    with col3:
        st.button("🛠️ Ersatzteile bestellen", use_container_width=True)
    with col4:
        st.button("📱 Mobile App Link", use_container_width=True)

# ========== PUMPENDETAILS ==========
elif page == "🔍 Pumpendetails":
    # EDUR Header
    st.markdown("""
        <div class="edur-header">
            <h1 class="edur-logo-text">EDUR PumpVision</h1>
            <p class="edur-subtitle">Detailansicht & Diagnose</p>
        </div>
    """, unsafe_allow_html=True)
    
    selected_pump = st.selectbox(
        "Pumpe auswählen:",
        options=filtered_data['id'].tolist(),
        format_func=lambda x: f"{x} - {filtered_data[filtered_data['id']==x]['name'].values[0]}"
    )
    
    pump_info = filtered_data[filtered_data['id'] == selected_pump].iloc[0]
    
    # Status-Header
    status_color = {"OK": "🟢", "Warnung": "🟡", "Kritisch": "🔴"}
    st.markdown(f"## {status_color[pump_info['status']]} {pump_info['name']} ({pump_info['id']})")
    st.caption(f"Typ: {pump_info['typ']} | Standort: {pump_info['standort']}")
    
    st.markdown("---")
    
    # A. Echtzeit-Daten
    st.subheader("📡 Echtzeit-Daten (Live-Monitoring)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta_druck = pump_info['druck'] - pump_info['druck_soll']
        st.metric(
            "Druck",
            f"{pump_info['druck']:.2f} Bar",
            delta=f"{delta_druck:+.2f} Bar",
            delta_color="normal" if abs(delta_druck) < 1 else "inverse"
        )
    
    with col2:
        temp_status = "normal" if pump_info['temperatur'] < pump_info['temp_max'] else "inverse"
        st.metric(
            "Temperatur",
            f"{pump_info['temperatur']:.1f} °C",
            delta=f"{pump_info['temp_max'] - pump_info['temperatur']:.1f}° bis Max",
            delta_color=temp_status
        )
    
    with col3:
        vib_status = "normal" if pump_info['vibration'] < pump_info['vib_max'] else "inverse"
        st.metric(
            "Vibration",
            f"{pump_info['vibration']:.2f} mm/s",
            delta="Im Normbereich" if vib_status == "normal" else "⚠️ Erhöht",
            delta_color=vib_status
        )
    
    with col4:
        st.metric("Stromaufnahme", f"{pump_info['strom']:.1f} A")
    
    with col5:
        st.metric("Durchfluss", f"{pump_info['durchfluss']:.1f} m³/h")
    
    # Historische Daten
    st.markdown("---")
    st.subheader("📈 Zeitverlauf (Letzte 7 Tage)")
    
    historical_data = generate_historical_data(selected_pump, days=7)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Druck", "🌡️ Temperatur", "📳 Vibration", "⚡ Stromaufnahme"])
    
    with tab1:
        fig_druck = px.line(historical_data, x='Zeit', y='Druck', title='Druckverlauf')
        fig_druck.add_hline(y=pump_info['druck_soll'], line_dash="dash", line_color="green", annotation_text="Sollwert")
        st.plotly_chart(fig_druck, use_container_width=True)
    
    with tab2:
        fig_temp = px.line(historical_data, x='Zeit', y='Temperatur', title='Temperaturverlauf')
        fig_temp.add_hline(y=pump_info['temp_max'], line_dash="dash", line_color="red", annotation_text="Maximum")
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with tab3:
        fig_vib = px.line(historical_data, x='Zeit', y='Vibration', title='Vibrationsverlauf')
        fig_vib.add_hline(y=pump_info['vib_max'], line_dash="dash", line_color="red", annotation_text="Maximum")
        st.plotly_chart(fig_vib, use_container_width=True)
    
    with tab4:
        fig_strom = px.line(historical_data, x='Zeit', y='Strom', title='Stromverbrauch')
        st.plotly_chart(fig_strom, use_container_width=True)
    
    # B. Alarmmanagement
    st.markdown("---")
    st.subheader("⚠️ Alarmmanagement")
    
    pump_alarms = st.session_state.alarm_data[st.session_state.alarm_data['pumpe'] == selected_pump]
    
    if len(pump_alarms) > 0:
        for _, alarm in pump_alarms.iterrows():
            with st.expander(f"🔔 {alarm['typ']} - {alarm['status']} ({alarm['prioritaet']})"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Zeit:** {alarm['zeit'].strftime('%d.%m.%Y %H:%M')}")
                    st.write(f"**Empfehlung:** {alarm['empfehlung']}")
                    if alarm['status'] == 'Offen':
                        kommentar = st.text_input("Kommentar hinzufügen:", key=f"kommentar_{alarm['id']}")
                        if st.button("Alarm quittieren", key=f"quitt_{alarm['id']}"):
                            st.success("✅ Alarm wurde quittiert!")
                with col2:
                    st.metric("Alarm-ID", alarm['id'])
                    st.metric("Priorität", alarm['prioritaet'])
    else:
        st.success("✅ Keine Alarme für diese Pumpe!")
    
    # C. Wartung & Dokumentation
    st.markdown("---")
    st.subheader("🔧 Wartung & Dokumentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"📅 **Nächste Wartung in:** {pump_info['naechste_wartung']} Tagen")
        st.write("**Fällige Aufgaben:**")
        st.checkbox("✓ Ölwechsel durchführen")
        st.checkbox("✓ Dichtungen prüfen")
        st.checkbox("✓ Vibrationsmessung")
        st.checkbox("✓ Drucktest")
    
    with col2:
        st.write("**📚 Dokumentenarchiv:**")
        st.download_button("📄 Betriebsanleitung (PDF)", data="", file_name="anleitung.pdf")
        st.download_button("📋 Wartungsprotokoll", data="", file_name="wartung.pdf")
        st.download_button("🔩 Ersatzteilkatalog", data="", file_name="ersatzteile.pdf")
        st.button("📷 Wartungsfotos anzeigen")
    
    # D. Handlungsempfehlungen
    st.markdown("---")
    st.subheader("💡 Handlungsempfehlungen")
    
    if pump_info['status'] == "Kritisch":
        st.error("🚨 **Sofortige Maßnahme erforderlich:** Pumpe zeigt kritische Werte!")
        st.write("👉 Empfohlene Aktion: Pumpe außer Betrieb nehmen und Service kontaktieren")
    elif pump_info['status'] == "Warnung":
        st.warning("⚠️ **Überwachung erhöhen:** Parameter außerhalb Normbereich")
        if pump_info['temperatur'] > pump_info['temp_max'] * 0.9:
            st.write("🌡️ Temperatur hoch → Kühlsystem prüfen")
        if pump_info['vibration'] > pump_info['vib_max'] * 0.9:
            st.write("📳 Vibration erhöht → Lager und Befestigung kontrollieren")
    else:
        st.success("✅ Pumpe läuft im Normalbetrieb - keine Maßnahmen erforderlich")
    
    st.button("🛒 Ersatzteile bestellen", use_container_width=True)

# ========== ALARMMANAGEMENT ==========
elif page == "⚠️ Alarmmanagement":
    # EDUR Header
    st.markdown("""
        <div class="edur-header">
            <h1 class="edur-logo-text">EDUR PumpVision</h1>
            <p class="edur-subtitle">Alarmmanagement & Monitoring</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect("Status:", ["Offen", "Quittiert", "Behoben"], default=["Offen"])
    with col2:
        priority_filter = st.multiselect("Priorität:", ["Hoch", "Mittel", "Niedrig"], default=["Hoch", "Mittel"])
    with col3:
        date_range = st.date_input("Zeitraum:", value=(datetime.now()-timedelta(days=7), datetime.now()))
    
    # Gefilterte Alarme
    filtered_alarms = st.session_state.alarm_data.copy()
    if status_filter:
        filtered_alarms = filtered_alarms[filtered_alarms['status'].isin(status_filter)]
    if priority_filter:
        filtered_alarms = filtered_alarms[filtered_alarms['prioritaet'].isin(priority_filter)]
    
    st.metric("Gefundene Alarme", len(filtered_alarms))
    
    # Alarm-Statistiken
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_priority = px.pie(filtered_alarms, names='prioritaet', title='Nach Priorität')
        st.plotly_chart(fig_priority, use_container_width=True)
    with col2:
        fig_status = px.pie(filtered_alarms, names='status', title='Nach Status')
        st.plotly_chart(fig_status, use_container_width=True)
    with col3:
        fig_type = px.bar(filtered_alarms['typ'].value_counts(), title='Nach Typ')
        st.plotly_chart(fig_type, use_container_width=True)
    
    # Alarm-Tabelle
    st.markdown("---")
    st.subheader("📋 Alarm-Liste")
    st.dataframe(
        filtered_alarms[['id', 'pumpe', 'typ', 'prioritaet', 'zeit', 'status', 'empfehlung']],
        use_container_width=True,
        height=400
    )

# ========== BERICHTE & ANALYSEN ==========
elif page == "📈 Berichte & Analysen":
    # EDUR Header
    st.markdown("""
        <div class="edur-header">
            <h1 class="edur-logo-text">EDUR PumpVision</h1>
            <p class="edur-subtitle">Berichte & Performance-Analysen</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["⚡ Energieverbrauch", "⏱️ Ausfallzeiten", "💰 Wartungskosten"])
    
    with tab1:
        st.subheader("Energieverbrauch-Analyse")
        
        # Simulierte Energiedaten
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
        energy_data = pd.DataFrame({
            'Datum': dates,
            'Verbrauch_kWh': np.random.uniform(800, 1500, len(dates)),
            'Kosten_EUR': np.random.uniform(120, 225, len(dates))
        })
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Durchschn. tägl. Verbrauch", "1.147 kWh", delta="-5.2%")
        with col2:
            st.metric("Monatliche Kosten", "34.410 €", delta="-156 €")
        with col3:
            st.metric("CO₂-Einsparung", "2.4 t", delta="+0.3 t")
        
        fig_energy = px.line(energy_data[-90:], x='Datum', y='Verbrauch_kWh', 
                            title='Energieverbrauch (Letzte 90 Tage)')
        st.plotly_chart(fig_energy, use_container_width=True)
        
        st.info("📊 Benchmark: Ihre Anlage verbraucht 8% weniger Energie als der Branchendurchschnitt")
    
    with tab2:
        st.subheader("Ausfallzeiten & Verfügbarkeit")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("MTBF (Durchschn.)", "847 h")
        with col2:
            st.metric("Verfügbarkeit", "98.7%", delta="+0.3%")
        with col3:
            st.metric("Ungeplante Stopps", "3", delta="1", delta_color="inverse")
        
        # Verfügbarkeit pro Pumpe
        availability_data = filtered_data[['id', 'name', 'betriebsstunden']].copy()
        availability_data['Verfügbarkeit_%'] = np.random.uniform(95, 99.5, len(availability_data))
        
        fig_avail = px.bar(availability_data, x='id', y='Verfügbarkeit_%', 
                          title='Verfügbarkeit nach Pumpe',
                          color='Verfügbarkeit_%',
                          color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_avail, use_container_width=True)
    
    with tab3:
        st.subheader("Wartungskosten-Analyse")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamtkosten (Jahr)", "47.850 €")
        with col2:
            st.metric("Kosten pro Pumpe", "4.785 €")
        with col3:
            st.metric("Präventiv vs. Reaktiv", "65% / 35%")
        
        cost_data = pd.DataFrame({
            'Monat': pd.date_range(start='2024-01-01', periods=12, freq='M'),
            'Präventive_Wartung': np.random.uniform(2000, 4000, 12),
            'Reaktive_Wartung': np.random.uniform(1000, 3000, 12)
        })
        
        fig_costs = go.Figure()
        fig_costs.add_trace(go.Bar(x=cost_data['Monat'], y=cost_data['Präventive_Wartung'], 
                                   name='Präventive Wartung'))
        fig_costs.add_trace(go.Bar(x=cost_data['Monat'], y=cost_data['Reaktive_Wartung'], 
                                   name='Reaktive Wartung'))
        fig_costs.update_layout(barmode='stack', title='Wartungskosten nach Monat')
        st.plotly_chart(fig_costs, use_container_width=True)
    
    # Export-Funktion
    st.markdown("---")
    st.subheader("📥 Bericht exportieren")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📄 Als PDF herunterladen", data="", file_name="bericht.pdf")
    with col2:
        st.download_button("📊 Als Excel herunterladen", data="", file_name="bericht.xlsx")

# ========== WARTUNGSPLANUNG ==========
elif page == "🛠️ Wartungsplanung":
    # EDUR Header
    st.markdown("""
        <div class="edur-header">
            <h1 class="edur-logo-text">EDUR PumpVision</h1>
            <p class="edur-subtitle">Wartungsplanung & Service</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Fällige Wartungen
    st.subheader("📅 Anstehende Wartungen")
    
    upcoming_maintenance = filtered_data[['id', 'name', 'typ', 'standort', 'naechste_wartung']].copy()
    upcoming_maintenance = upcoming_maintenance.sort_values('naechste_wartung')
    upcoming_maintenance['Status'] = upcoming_maintenance['naechste_wartung'].apply(
        lambda x: '🔴 Überfällig' if x < 0 else '🟡 Dringend' if x < 7 else '🟢 Geplant'
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        overdue = len(upcoming_maintenance[upcoming_maintenance['naechste_wartung'] < 0])
        st.metric("Überfällig", overdue, delta=overdue if overdue > 0 else None, delta_color="inverse")
    with col2:
        urgent = len(upcoming_maintenance[upcoming_maintenance['naechste_wartung'].between(0, 7)])
        st.metric("Diese Woche", urgent)
    with col3:
        planned = len(upcoming_maintenance[upcoming_maintenance['naechste_wartung'] > 7])
        st.metric("Geplant", planned)
    
    st.dataframe(
        upcoming_maintenance[['id', 'name', 'typ', 'standort', 'naechste_wartung', 'Status']],
        use_container_width=True,
        height=400
    )
    
    # Wartungskalender
    st.markdown("---")
    st.subheader("📆 Wartungskalender")
    
    calendar_data = []
    for _, pump in upcoming_maintenance.iterrows():
        next_date = datetime.now() + timedelta(days=int(pump['naechste_wartung']))
        calendar_data.append({
            'Pumpe': pump['id'],
            'Wartungsdatum': next_date,
            'Typ': 'Routinewartung'
        })
    
    calendar_df = pd.DataFrame(calendar_data)
    st.dataframe(calendar_df, use_container_width=True)
    
    st.button("📧 Wartungserinnerung versenden", use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
    <div class="edur-footer">
        <div style='display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;'>
            <div>
                <h2 style='margin: 0; letter-spacing: 3px;'>EDUR</h2>
                <p style='margin: 5px 0; color: #A5D8E6;'>PumpVision® v2.0</p>
            </div>
            <div>
                <p style='margin: 5px 0;'>📞 Support: +49 (0) 234 123456</p>
                <p style='margin: 5px 0;'>📧 service@.de</p>
            </div>
            <div>
                <p style='margin: 5px 0;'>🕐 Letzte Aktualisierung:</p>
                <p style='margin: 5px 0;'>{}</p>
            </div>
        </div>
        <p style='margin-top: 15px; font-size: 0.8em; opacity: 0.7;'>© 2024 EDUR-Pumpenfabrik Eduard Redlien GmbH & Co. KG</p>
    </div>
""".format(datetime.now().strftime("%d.%m.%Y %H:%M:%S")), unsafe_allow_html=True)

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-top: 20px;'>
        <p style='margin: 5px 0; font-size: 0.9em;'><strong>ℹ️ System-Info</strong></p>
        <p style='margin: 5px 0; font-size: 0.85em;'>• Echtzeit-Updates alle 30s</p>
        <p style='margin: 5px 0; font-size: 0.85em;'>• DSGVO-konform</p>
        <p style='margin: 5px 0; font-size: 0.85em;'>• TÜV-zertifiziert</p>
    </div>
""", unsafe_allow_html=True)

# Auto-Refresh Option
st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh aktivieren (30s)")
if auto_refresh:
    st.sidebar.success("Auto-Refresh aktiv")
    # In Production: st.rerun() mit time.sleep(30) in einem Loop
