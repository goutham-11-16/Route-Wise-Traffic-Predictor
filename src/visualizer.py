"""
Geospatial Map Visualization Engine using Folium
Renders real road driving paths, accident blackspot clusters, and live hazard alert zones.
Course: 213CSE2301 - Predictive Analytics (Autonomy)
"""

import folium
from folium import plugins
from typing import Tuple, List, Dict


def build_interactive_route_map(
    start_coords: Tuple[float, float],
    end_coords: Tuple[float, float],
    route_analysis: Dict,
    model_engine,
    time_cat: str = 'Morning',
    weather: str = 'Clear',
    road_type: str = 'Arterial',
    origin_name: str = 'Origin',
    dest_name: str = 'Destination',
    live_weather: Dict = None
) -> folium.Map:
    """
    Builds an interactive Folium map featuring:
    - Real OSRM driving polyline color-coded by predicted journey risk
    - Accident Hotspots / K-Means danger zones with proportional radius
    - High-risk segment flags and Blackspot proximity alerts
    - Origin (Green) & Destination (Red) custom markers
    - Live weather watermark overlay
    """
    route_points = route_analysis['route_points']
    center_lat = (start_coords[0] + end_coords[0]) / 2.0
    center_lon = (start_coords[1] + end_coords[1]) / 2.0

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )

    # 1. Overlay K-Means Accident Hotspots
    kmeans = model_engine.kmeans
    cluster_df = model_engine.cluster_risk_df

    for idx, center in enumerate(kmeans.cluster_centers_):
        match = cluster_df[cluster_df['Cluster'] == idx]
        score = float(match['Cluster_Risk_Score'].values[0]) if not match.empty else 1.5

        if score >= 2.0:
            circle_color = '#b30000'  # High risk: Dark Red
            fill_op = 0.35
            label_tag = "CRITICAL BLACKSPOT"
        elif score >= 1.6:
            circle_color = '#e65c00'  # Medium risk: Orange-red
            fill_op = 0.25
            label_tag = "MODERATE RISK ZONE"
        else:
            circle_color = '#ffcc00'  # Low risk: Amber
            fill_op = 0.15
            label_tag = "LOW RISK ZONE"

        radius_m = max(500, int(score * 650))

        popup_text = f"""
        <div style="font-family: sans-serif; min-width: 170px;">
            <span style="background-color: {circle_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">{label_tag}</span><br>
            <b style="font-size: 13px; color: {circle_color}; margin-top: 4px; display: inline-block;">Accident Hotspot #{idx+1}</b><br>
            <b>Historical Risk Score:</b> {score:.2f} / 3.0<br>
            <b>Coordinates:</b> {center[0]:.4f}, {center[1]:.4f}<br>
            <span style="font-size: 11px; color: #555;">K-Means Spatial Cluster Center</span>
        </div>
        """
        folium.Circle(
            location=[center[0], center[1]],
            radius=radius_m,
            color=circle_color,
            weight=1.5,
            fill=True,
            fillColor=circle_color,
            fillOpacity=fill_op,
            popup=folium.Popup(popup_text, max_width=260)
        ).add_to(m)

    # 2. Add Real Driving Route Polyline
    route_color = route_analysis['risk_color']
    route_tooltip = (
        f"Route: {route_analysis['distance_km']} km | "
        f"Est: {route_analysis['estimated_minutes']} mins | "
        f"Risk: {route_analysis['journey_risk_tier']}"
    )
    folium.PolyLine(
        locations=route_points,
        color=route_color,
        weight=6,
        opacity=0.88,
        tooltip=route_tooltip
    ).add_to(m)

    # 3. Add High-Risk Segment Waypoint Markers
    for seg in route_analysis.get('segment_details', []):
        if seg['severity'] == 'High':
            folium.CircleMarker(
                location=[seg['lat'], seg['lon']],
                radius=4,
                color='#990000',
                fill=True,
                fillColor='#ff0000',
                fillOpacity=0.9,
                tooltip=f"High Risk Collision Node: Composite Index {seg['composite_score']:.2f}"
            ).add_to(m)

    # 4. Origin Marker (Green Flag)
    origin_popup = f"""
    <div style="font-family: sans-serif;">
        <b style="color: #27ae60;">🟢 Start Location</b><br>
        <b>{origin_name}</b><br>
        GPS: {start_coords[0]:.4f}, {start_coords[1]:.4f}
    </div>
    """
    folium.Marker(
        location=[start_coords[0], start_coords[1]],
        popup=folium.Popup(origin_popup, max_width=220),
        tooltip=f"Start: {origin_name}",
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)

    # 5. Destination Marker (Red Flag)
    dest_popup = f"""
    <div style="font-family: sans-serif;">
        <b style="color: #c0392b;">🔴 Destination</b><br>
        <b>{dest_name}</b><br>
        GPS: {end_coords[0]:.4f}, {end_coords[1]:.4f}
    </div>
    """
    folium.Marker(
        location=[end_coords[0], end_coords[1]],
        popup=folium.Popup(dest_popup, max_width=220),
        tooltip=f"Destination: {dest_name}",
        icon=folium.Icon(color='red', icon='flag', prefix='fa')
    ).add_to(m)

    plugins.Fullscreen().add_to(m)
    return m
