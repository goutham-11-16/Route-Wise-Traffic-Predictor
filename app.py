"""
Interactive Web Application: Route-Wise Traffic Accident Risk Prediction System
Features:
- Real Driving Road Routing (OSRM Free API)
- Live Weather Auto-Detection & 24-Hour Forecast (Open-Meteo Free API)
- Intelligent Road Hazard & Blackspot Alerts
- Dynamic Safe Travel Time Recommendation
Course: 213CSE2301 - Predictive Analytics (Autonomy)
Course Coordinator: Dr. N. Subbulakshmi
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import altair as alt

from src.models import AccidentRiskModel
from src.router import (
    get_coordinates, haversine_distance_km, RouteRiskAnalyzer,
    search_locations, POPULAR_LOCATIONS
)
from src.live_services import fetch_live_weather, fetch_hourly_weather_forecast
from src.visualizer import build_interactive_route_map
from src.data_pipeline import get_time_category

st.set_page_config(
    page_title="Route Accident Risk & Safe Travel Recommender",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #4b5563;
        margin-bottom: 1.0rem;
    }
    .alert-critical {
        background-color: #fee2e2;
        border-left: 5px solid #dc2626;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
        color: #991b1b;
    }
    .alert-warning {
        background-color: #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
        color: #92400e;
    }
    .alert-info {
        background-color: #e0f2fe;
        border-left: 5px solid #0284c7;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
        color: #0369a1;
    }
    .weather-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.8rem;
        text-align: center;
    }
    .badge-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-med {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_ml_system():
    model = AccidentRiskModel(n_clusters=20, random_state=42)
    if os.path.exists('models/rf_model.pkl'):
        model.load_artifacts('models')
    else:
        from src.models import train_and_save
        model = train_and_save('data/cleaned_accidents_6469.csv', 'models')
    analyzer = RouteRiskAnalyzer(model)
    return model, analyzer


@st.cache_data(ttl=120)
def cached_search_locations(query: str):
    return search_locations(query, max_results=6)


@st.cache_data(ttl=300)
def cached_live_weather(lat: float, lon: float):
    return fetch_live_weather(lat, lon)


@st.cache_data
def load_accident_data():
    if os.path.exists('data/cleaned_accidents_6469.csv'):
        return pd.read_csv('data/cleaned_accidents_6469.csv')
    return pd.DataFrame()


model_engine, analyzer = load_ml_system()
df_accidents = load_accident_data()

# Sidebar: 100% Free API Info & Settings
with st.sidebar:
    st.image("https://img.icons8.com/color/96/traffic-light.png", width=64)
    st.markdown("### 🆓 Free API Stack (Zero Cost)")
    st.markdown("""
    This system runs on **100% free open community APIs** without requiring credit cards or paid keys:
    - 🗺️ **Routing:** [OSRM Project](http://project-osrm.org/) *(No API key, real road geometries)*
    - 🌤️ **Live Weather:** [Open-Meteo](https://open-meteo.com/) *(No key, real-time + 24h hourly forecast)*
    - 📍 **Geocoding:** OpenStreetMap / Nominatim & ArcGIS open endpoint
    - 🚨 **Alerts Engine:** Built-in blackspot proximity & hazard analyzer
    """)
    st.markdown("---")
    st.markdown("### ⚙️ Optional External API Keys")
    st.caption("You do NOT need keys to run the app. If you have custom keys, enter them here:")
    with st.expander("🔑 Optional API Keys"):
        custom_tomtom = st.text_input("TomTom API Key (Optional):", placeholder="Enter key for live traffic flow")
        custom_owm = st.text_input("OpenWeatherMap Key (Optional):", placeholder="Enter key for satellite radar")
        if custom_tomtom or custom_owm:
            st.success("Custom key configured!")

# Header
st.markdown('<div class="main-header">🚗 Route-Wise Traffic Accident Risk & Safe Travel Recommender</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    '<b>Course:</b> 213CSE2301 Predictive Analytics (Autonomy) | '
    '<b>Coordinator:</b> Dr. N. Subbulakshmi | '
    '<b>Department:</b> Computer Science & Engineering'
    '</div>',
    unsafe_allow_html=True
)

tabs = st.tabs([
    "🗺️ Real Route Risk & Safe Departure Recommender",
    "📊 Exploratory Data Analysis (Slides)",
    "🤖 Model Performance & Evaluation",
    "📁 Dataset Explorer & Architecture"
])

# ==============================================================================
# TAB 1: Route Risk Analyzer with Real Road Routing & Auto Live Weather
# ==============================================================================
with tabs[0]:
    st.subheader("Real-Road Risk Engine & Dynamic Safe Departure Recommender")
    st.write(
        "Search and select origin and destination. The system automatically fetches "
        "**real driving road paths (OSRM)**, **live weather conditions (Open-Meteo)**, "
        "and checks for **road hazard blackspots** to recommend the safest departure time."
    )

    col_input, col_map = st.columns([1, 1.55], gap="medium")

    with col_input:
        st.markdown("### 🔍 1. Search Locations")
        
        # Origin Search
        orig_query = st.text_input(
            "Type Origin Location:",
            value="Connaught Place Delhi",
            placeholder="e.g. Connaught Place, Noida, IGI Airport, Bangalore...",
            key="orig_query_input"
        )
        
        orig_matches = cached_search_locations(orig_query)
        if orig_matches:
            orig_options = [f"{m['name']} ({m['coords'][0]:.4f}, {m['coords'][1]:.4f})" for m in orig_matches]
            selected_orig_idx = st.selectbox(
                "📍 Select Confirmed Origin:",
                range(len(orig_options)),
                format_func=lambda i: orig_options[i],
                key="orig_select"
            )
            selected_orig = orig_matches[selected_orig_idx]
            origin_coords = selected_orig['coords']
            origin_name = selected_orig['name']
            st.success(f"✅ **Origin:** {origin_name}")
        else:
            c = get_coordinates(orig_query)
            if c:
                origin_coords = c
                origin_name = orig_query
                st.success(f"✅ **Origin Resolved:** {orig_query}")
            else:
                st.warning("⚠️ No exact matches found for Origin.")
                origin_coords = None
                origin_name = None

        # Destination Search
        dest_query = st.text_input(
            "Type Destination Location:",
            value="Noida Expressway",
            placeholder="e.g. India Gate, Cyber City Gurgaon, Noida Expressway, Mysore...",
            key="dest_query_input"
        )
        
        dest_matches = cached_search_locations(dest_query)
        if dest_matches:
            dest_options = [f"{m['name']} ({m['coords'][0]:.4f}, {m['coords'][1]:.4f})" for m in dest_matches]
            selected_dest_idx = st.selectbox(
                "🎯 Select Confirmed Destination:",
                range(len(dest_options)),
                format_func=lambda i: dest_options[i],
                key="dest_select"
            )
            selected_dest = dest_matches[selected_dest_idx]
            dest_coords = selected_dest['coords']
            dest_name = selected_dest['name']
            st.success(f"✅ **Destination:** {dest_name}")
        else:
            c = get_coordinates(dest_query)
            if c:
                dest_coords = c
                dest_name = dest_query
                st.success(f"✅ **Destination Resolved:** {dest_query}")
            else:
                st.warning("⚠️ No exact matches found for Destination.")
                dest_coords = None
                dest_name = None

        st.markdown("---")
        st.markdown("### ⏱️ 2. Planned Departure Time")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            hour_input = st.slider("Planned Departure Hour:", 0, 23, 21)
        with col_t2:
            time_category = get_time_category(hour_input)
            st.info(f"Departure Window: **{time_category} ({hour_input:02d}:00 hrs)**")

        # Automatic Live Weather Status Card
        if origin_coords:
            live_w = cached_live_weather(origin_coords[0], origin_coords[1])
            st.markdown(f"""
            <div class="weather-card">
                <b>{live_w['icon']} Live Route Weather Auto-Detected:</b><br>
                <b>Condition:</b> {live_w['condition']} ({live_w['description']})<br>
                <b>Temperature:</b> {live_w['temperature']}°C | <b>Wind:</b> {live_w['windspeed']} km/h<br>
                <span style="font-size: 11px; color: #0284c7;">⚡ Automatically pulled via Open-Meteo Free API</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            live_w = {"condition": "Clear", "temperature": 27.0, "windspeed": 5.0}

        # Optional Weather Simulation Override
        with st.expander("🛠️ Optional: Simulate Adverse Weather or Road Type"):
            override_weather = st.checkbox("Override Live Weather with Simulation", value=False)
            if override_weather:
                sim_weather = st.selectbox("Simulated Weather:", ['Clear', 'Rainy', 'Foggy', 'Cloudy'])
                live_w['condition'] = sim_weather
            road_input = st.selectbox("Road Classification:", ['Arterial', 'Highway', 'Residential', 'Intersection'], index=1)

        btn_analyze = st.button("🚀 Calculate Best Route & Recommend Safe Time", type="primary", use_container_width=True)

    with col_map:
        if origin_coords and dest_coords:
            if btn_analyze or 'last_analysis_data' not in st.session_state:
                with st.spinner("Fetching real road driving geometry (OSRM) and predicting segment risks..."):
                    road_type_val = road_input if 'road_input' in locals() else 'Arterial'
                    analysis = analyzer.analyze_route(
                        origin_coords, dest_coords, hour=hour_input, time_cat=time_category,
                        weather=live_w['condition'], road_type=road_type_val,
                        live_weather_info=live_w
                    )
                    rec = analyzer.recommend_safest_departure_time(
                        origin_coords, dest_coords, current_hour=hour_input, current_time_cat=time_category,
                        road_type=road_type_val
                    )
                    st.session_state['last_analysis_data'] = (origin_coords, dest_coords, origin_name, dest_name, analysis, rec, live_w)

            if 'last_analysis_data' in st.session_state:
                c_start, c_end, o_name, d_name, analysis, rec, w_info = st.session_state['last_analysis_data']

                # Real driving KPIs
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Driving Distance", f"{analysis['distance_km']} km")
                with m2:
                    st.metric("Estimated Duration", f"{analysis['estimated_minutes']} mins")
                with m3:
                    st.metric("Journey Risk Tier", analysis['journey_risk_tier'])
                with m4:
                    st.metric("Safest Window", rec['safest_time_category'], f"-{rec['risk_reduction_pct']}% Risk")

                # Live Road & Safety Hazard Alerts Banner
                alerts = analysis.get('alerts', [])
                if alerts:
                    st.markdown("#### ⚠️ Active Route Hazard Alerts")
                    for a in alerts:
                        css_class = "alert-critical" if a['severity'] == 'CRITICAL' else ("alert-warning" if a['severity'] in ['HIGH', 'WARNING'] else "alert-info")
                        st.markdown(f"""
                        <div class="{css_class}">
                            <b>{a['icon']} [{a['severity']}] {a['title']}</b><br>
                            <span>{a['message']}</span>
                        </div>
                        """, unsafe_allow_html=True)

                # Real Road Driving Map
                st.caption(f"🗺️ Map routing powered by: **{analysis.get('routing_source', 'OSRM')}**")
                route_map = build_interactive_route_map(
                    c_start, c_end, analysis, model_engine,
                    time_cat=time_category, weather=w_info['condition'],
                    origin_name=o_name, dest_name=d_name, live_weather=w_info
                )
                components.html(route_map._repr_html_(), height=460)
        else:
            st.info("👆 Please search and confirm both Origin and Destination on the left to display the route and risk evaluation.")

    # Safe Travel Time Recommendation & 24-Hour Risk Curve
    if 'last_analysis_data' in st.session_state and origin_coords and dest_coords:
        _, _, _, _, analysis, rec, _ = st.session_state['last_analysis_data']
        st.markdown("---")
        st.subheader("🕒 Dynamic Safe Travel Time Recommendation")
        
        rec_col1, rec_col2 = st.columns([1.2, 1.8])

        with rec_col1:
            st.markdown(f"""
            <div style="background-color: #ecfdf5; border: 2px solid #10b981; border-radius: 10px; padding: 16px;">
                <div style="color: #047857; font-size: 0.9rem; font-weight: bold;">🌟 OPTIMAL DEPARTURE TIME</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #065f46; margin: 4px 0;">{rec['safest_hour_label']} ({rec['safest_time_category']})</div>
                <div style="font-size: 1.05rem; color: #047857; font-weight: 600;">
                    🛡️ {rec['risk_reduction_pct']}% Risk Reduction
                </div>
                <p style="font-size: 0.88rem; color: #374151; margin-top: 8px;">
                    Rescheduling your trip from <b>{hour_input:02d}:00 ({time_category})</b> to 
                    <b>{rec['safest_hour_label']} ({rec['safest_time_category']})</b> minimizes exposure to high-fatality 
                    night-time freight traffic and favorable road visibility.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            # 4-Window cards
            w_cols = st.columns(2)
            for idx, w in enumerate(rec['all_time_evaluations']):
                col_target = w_cols[idx % 2]
                is_safe = w['time_category'] == rec['safest_time_category']
                b_class = "badge-low" if w['journey_risk_tier'] == 'LOW RISK' else ("badge-med" if w['journey_risk_tier'] == 'MODERATE RISK' else "badge-high")
                with col_target:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 8px; border: {'2px solid #10b981' if is_safe else '1px solid #e2e8f0'};">
                        <b>{w['weather_icon']} {w['time_category']}</b> ({w['nominal_hour']:02d}:00)<br>
                        <span class="{b_class}">{w['journey_risk_tier']}</span><br>
                        <span style="font-size: 0.8rem; color: #64748b;">Risk Index: {w['mean_risk_score']:.3f}</span>
                    </div>
                    """, unsafe_allow_html=True)

        with rec_col2:
            st.markdown("#### 📈 24-Hour Route Accident Risk Trajectory")
            st.caption("Hour-by-hour collision risk combining forecasted weather (Open-Meteo) and temporal accident distributions:")
            
            hourly_df = pd.DataFrame(rec['hourly_24_evaluations'])
            chart = alt.Chart(hourly_df).mark_line(point=True).encode(
                x=alt.X('hour:Q', title='Hour of Day (0-23)', scale=alt.Scale(domain=[0, 23])),
                y=alt.Y('mean_risk_score:Q', title='Composite Collision Risk Index (0 - 1.0)'),
                tooltip=['hour_label', 'time_category', 'weather', 'temperature', 'mean_risk_score', 'journey_risk_tier'],
                color=alt.value('#2563eb')
            ).properties(height=260)
            
            st.altair_chart(chart, use_container_width=True)


# ==============================================================================
# TAB 2: EDA & Reference Slides Visualizations
# ==============================================================================
with tabs[1]:
    st.subheader("Exploratory Data Analysis & Project Reference Charts")
    st.write("Visualizations generated directly from the 6,469 cleaned accident records matching the project slides.")

    eda_col1, eda_col2 = st.columns(2)

    with eda_col1:
        st.markdown("#### 1. Accident Distribution by Time Category (Slide 5)")
        if os.path.exists('static/accident_distribution_time.png'):
            st.image('static/accident_distribution_time.png', use_container_width=True)
        st.caption("Temporal pattern reveals peak volume in Afternoon (2,230) and Morning (1,910).")

        st.markdown("#### 3. Accident Frequency by Hour of Day (Slide 9)")
        if os.path.exists('static/hourly_frequency.png'):
            st.image('static/hourly_frequency.png', use_container_width=True)
        st.caption("24-hour histogram highlights bimodal commuting peaks at 06:00 and 13:00.")

        st.markdown("#### 5. Pearson Correlation Heatmap (Slide 9)")
        if os.path.exists('static/correlation_heatmap.png'):
            st.image('static/correlation_heatmap.png', use_container_width=True)
        st.caption("Extracted correlation matrix showing Hour, Time_Encoded, and Target_Encoded.")

    with eda_col2:
        st.markdown("#### 2. Severity Partitioned by Time Category (Slide 6)")
        if os.path.exists('static/accident_severity_time.png'):
            st.image('static/accident_severity_time.png', use_container_width=True)
        st.caption("High severity accidents concentrate heavily during Evening (950) and Night (538).")

        st.markdown("#### 4. Severity Classification Distribution (Slide 9)")
        if os.path.exists('static/severity_distribution.png'):
            st.image('static/severity_distribution.png', use_container_width=True)
        st.caption("Class breakdown: Medium (2,636 incidents), Low (2,280 incidents), High (1,553 incidents).")

        st.markdown("#### 6. Feature & Permutation Importance (Slide 8 & 9)")
        p_c1, p_c2 = st.columns(2)
        with p_c1:
            if os.path.exists('static/feature_importance.png'):
                st.image('static/feature_importance.png', use_container_width=True)
        with p_c2:
            if os.path.exists('static/permutation_importance.png'):
                st.image('static/permutation_importance.png', use_container_width=True)
        st.caption("Relative factor influence: Location Risk drives primary baseline, followed by Exact Hour and Time Category.")


# ==============================================================================
# TAB 3: Model Performance & Lab Classifier Comparison
# ==============================================================================
with tabs[2]:
    st.subheader("Machine Learning Performance & Model Comparisons")
    st.write(
        "Comparison of Random Forest against fundamental predictive models studied "
        "in the **Predictive Analytics (213CSE2301)** curriculum."
    )

    if os.path.exists('models/model_metadata.json'):
        with open('models/model_metadata.json') as f:
            meta = json.load(f)

        comp_df = pd.DataFrame(meta['model_comparisons']).T

        col_m1, col_m2 = st.columns([3, 2])

        with col_m1:
            st.markdown("#### Algorithm Performance Benchmark")
            st.dataframe(
                comp_df.style.highlight_max(subset=['Accuracy', 'Precision', 'Recall', 'F1_Score'], color='#dcfce7'),
                use_container_width=True
            )

            st.markdown("#### Key Model Findings")
            st.markdown("""
            - **Random Forest Ensemble**: Outperforms individual linear and tree classifiers with strong balance across classes.
            - **Handling Class Imbalance**: Balanced class weights applied to prevent bias against high-severity incidents.
            - **Cross-Validation / Stratified Test**: Evaluated on 1,294 unseen stratified test samples (20% holdout).
            """)

        with col_m2:
            st.markdown("#### Model Confusion Matrix (Slide 7)")
            if os.path.exists('static/confusion_matrix.png'):
                st.image('static/confusion_matrix.png', use_container_width=True)
            st.caption("Confusion matrix for High, Low, and Medium accident risk classification.")


# ==============================================================================
# TAB 4: Dataset & Architecture
# ==============================================================================
with tabs[3]:
    st.subheader("Dataset Ingestion & System Architecture")

    col_arch1, col_arch2 = st.columns([1, 1])

    with col_arch1:
        st.markdown("#### 📋 Data Ingestion & Preprocessing Pipeline")
        st.markdown("""
        1. **Raw Aggregation (24,000 Records)**:
           - Merged from 5 primary traffic & road incident repositories:
             - *NHAI Corridor Logs*
             - *Delhi Traffic Police Records*
             - *MoRTH Highway Incident DB*
             - *Urban Transport Telemetry*
             - *Open Incident Reports*
        2. **Quality Cleaning (6,469 Valid Records)**:
           - Filtered missing/corrupted GPS coordinates outside corridor boundaries.
           - Removed missing target records and duplicate timestamps.
           - Normalised timestamps into standardized operational categories (*Morning*, *Afternoon*, *Evening*, *Night*).
        """)

    with col_arch2:
        st.markdown("#### 👥 Course & Project Information")
        st.markdown("""
        - **Course Name**: Predictive Analytics (Autonomy)
        - **Course Code**: 213CSE2301
        - **Course Coordinator**: Dr. N. Subbulakshmi
        - **Department**: Department of Computer Science & Engineering
        - **Team Members**:
          1. **99240040465** - E Goutham Reddy
          2. **99240040477** - D Karimulla
          3. **99240040480** - G S N Abhiram
          4. **99240040466** - U Sasi Kumar
          5. **99240040467** - E Manideep
        """)

    st.markdown("---")
    st.markdown("#### 🔍 Filtered Cleaned Dataset Sample (6,469 Records)")
    if not df_accidents.empty:
        filter_time = st.multiselect("Filter by Time Category:", df_accidents['Time_Category'].unique(), default=list(df_accidents['Time_Category'].unique()))
        filter_sev = st.multiselect("Filter by Severity:", df_accidents['Severity'].unique(), default=list(df_accidents['Severity'].unique()))
        
        filtered_df = df_accidents[
            (df_accidents['Time_Category'].isin(filter_time)) &
            (df_accidents['Severity'].isin(filter_sev))
        ]
        st.dataframe(filtered_df.head(200), use_container_width=True)
