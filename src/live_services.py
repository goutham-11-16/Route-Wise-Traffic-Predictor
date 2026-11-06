"""
Live External Services Module (100% Free / Open Community APIs)
- Real Road Routing: OSRM (Open Source Routing Machine) - Zero key, Free
- Live Weather & Hourly Forecast: Open-Meteo - Zero key, Free
- Intelligent Road Hazard & Blackspot Alert Generator
Course: 213CSE2301 - Predictive Analytics (Autonomy)
"""

import math
import time
import requests
from typing import Tuple, List, Dict, Optional

# WMO Weather Interpretation Codes (WMO 4501 standard)
WMO_WEATHER_MAP = {
    0: ('Clear', 'Clear sky', '☀️'),
    1: ('Clear', 'Mainly clear', '🌤️'),
    2: ('Cloudy', 'Partly cloudy', '⛅'),
    3: ('Cloudy', 'Overcast', '☁️'),
    45: ('Foggy', 'Fog and reduced visibility', '🌫️'),
    48: ('Foggy', 'Depositing rime fog', '🌫️'),
    51: ('Rainy', 'Light drizzle', '🌦️'),
    53: ('Rainy', 'Moderate drizzle', '🌧️'),
    55: ('Rainy', 'Dense drizzle', '🌧️'),
    61: ('Rainy', 'Slight rain', '🌧️'),
    63: ('Rainy', 'Moderate rain', '🌧️'),
    65: ('Rainy', 'Heavy rain', '⛈️'),
    71: ('Rainy', 'Slight snowfall', '🌨️'),
    73: ('Rainy', 'Moderate snowfall', '🌨️'),
    75: ('Rainy', 'Heavy snowfall', '❄️'),
    80: ('Rainy', 'Slight rain showers', '🌦️'),
    81: ('Rainy', 'Moderate rain showers', '🌧️'),
    82: ('Rainy', 'Violent rain showers', '⛈️'),
    95: ('Rainy', 'Thunderstorm', '🌩️'),
    96: ('Rainy', 'Thunderstorm with slight hail', '⛈️'),
    99: ('Rainy', 'Thunderstorm with heavy hail', '⛈️'),
}


def fetch_osrm_route(start_coords: Tuple[float, float],
                     end_coords: Tuple[float, float],
                     alternatives: bool = False) -> Optional[Dict]:
    """
    Queries OSRM (Open Source Routing Machine) for real driving road geometry.
    100% Free, NO API key required.
    Returns:
        Dict with 'geometry' (list of [lat, lon]), 'distance_km', 'duration_mins', 'source'.
    """
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords

    # OSRM expects coordinates in {lon},{lat} format
    base_url = "http://router.project-osrm.org/route/v1/driving"
    url = f"{base_url}/{lon1:.6f},{lat1:.6f};{lon2:.6f},{lat2:.6f}?overview=full&geometries=geojson"
    if alternatives:
        url += "&alternatives=true"

    try:
        resp = requests.get(url, timeout=7)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                routes_out = []
                for rt in data["routes"]:
                    dist_km = round(rt["distance"] / 1000.0, 2)
                    dur_mins = round(rt["duration"] / 60.0, 1)
                    # OSRM geojson coordinates are [lon, lat], convert to [lat, lon]
                    geojson_coords = rt["geometry"]["coordinates"]
                    route_lat_lons = [(round(pt[1], 6), round(pt[0], 6)) for pt in geojson_coords]
                    routes_out.append({
                        "geometry": route_lat_lons,
                        "distance_km": dist_km,
                        "duration_mins": dur_mins,
                        "source": "OSRM Live Real-Road Engine"
                    })
                return routes_out[0] if not alternatives else routes_out
    except Exception as e:
        print(f"OSRM service notice: {e}. Switching to internal road interpolation.")

    return None


def fetch_live_weather(lat: float, lon: float) -> Dict:
    """
    Fetches real-time weather at the given coordinates using Open-Meteo.
    100% Free, NO API key required.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat:.4f}&longitude={lon:.4f}"
        f"&current_weather=true"
        f"&hourly=precipitation,visibility,relative_humidity_2m"
        f"&timezone=auto"
    )

    default_weather = {
        "condition": "Clear",
        "temperature": 27.0,
        "windspeed": 5.0,
        "description": "Clear skies (Fallback estimate)",
        "icon": "☀️",
        "code": 0,
        "source": "Default Estimation"
    }

    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            cw = data.get("current_weather", {})
            w_code = int(cw.get("weathercode", 0))
            category, desc, icon = WMO_WEATHER_MAP.get(w_code, ("Clear", "Normal Weather", "🌤️"))
            return {
                "condition": category,
                "temperature": round(float(cw.get("temperature", 25.0)), 1),
                "windspeed": round(float(cw.get("windspeed", 5.0)), 1),
                "description": desc,
                "icon": icon,
                "code": w_code,
                "source": "Open-Meteo Live API"
            }
    except Exception as e:
        print(f"Weather service notice: {e}")

    return default_weather


def fetch_hourly_weather_forecast(lat: float, lon: float) -> Dict[int, Dict]:
    """
    Fetches 24-hour weather forecast for the current day from Open-Meteo.
    Maps each hour (0 to 23) to forecasted condition, temperature, and precipitation chance.
    100% Free, NO API key required.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat:.4f}&longitude={lon:.4f}"
        f"&hourly=weathercode,temperature_2m,precipitation_probability,visibility"
        f"&timezone=auto"
    )

    hourly_forecast = {}
    # Sensible defaults
    for h in range(24):
        hourly_forecast[h] = {
            "condition": "Clear",
            "temperature": 26.0,
            "precip_pct": 0,
            "visibility_km": 10.0,
            "icon": "☀️"
        }

    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            hourly = data.get("hourly", {})
            codes = hourly.get("weathercode", [])
            temps = hourly.get("temperature_2m", [])
            precips = hourly.get("precipitation_probability", [])
            visibs = hourly.get("visibility", [])

            for h in range(min(24, len(codes))):
                code = int(codes[h]) if h < len(codes) else 0
                cat, desc, icon = WMO_WEATHER_MAP.get(code, ("Clear", "Normal", "🌤️"))
                temp = float(temps[h]) if h < len(temps) else 26.0
                precip = int(precips[h]) if h < len(precips) else 0
                visib_km = (float(visibs[h]) / 1000.0) if (h < len(visibs) and visibs[h] is not None) else 10.0

                hourly_forecast[h] = {
                    "condition": cat,
                    "temperature": round(temp, 1),
                    "precip_pct": precip,
                    "visibility_km": round(visib_km, 1),
                    "icon": icon,
                    "desc": desc
                }
    except Exception as e:
        print(f"Hourly forecast notice: {e}")

    return hourly_forecast


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two coordinates in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def generate_road_hazard_alerts(route_points: List[Tuple[float, float]],
                                live_weather: Dict,
                                departure_hour: int,
                                cluster_centers,
                                cluster_risk_df) -> List[Dict]:
    """
    Intelligent Road Hazard Alert Engine:
    Evaluates:
    1. Accident Blackspot Proximity Alerts (routes passing near historical high-fatality clusters)
    2. Weather Hazard Alerts (fog/low visibility, rain, aquaplaning risk)
    3. Peak Congestion / Speed Differential Alerts (rush hour vs late night)
    """
    alerts = []

    # 1. Check Proximity to Historical Accident Blackspots
    blackspot_matches = []
    for idx, center in enumerate(cluster_centers):
        match = cluster_risk_df[cluster_risk_df['Cluster'] == idx]
        risk_score = float(match['Cluster_Risk_Score'].values[0]) if not match.empty else 1.5

        cond_weather = live_weather.get("condition", "Clear")
        # Enforce weather-adapted speed limit for this stop/blackspot
        if cond_weather == "Foggy":
            spot_speed_limit = 25
        elif cond_weather == "Rainy":
            spot_speed_limit = 30
        else:
            spot_speed_limit = 40

        min_dist_km = min(haversine_km(pt[0], pt[1], center[0], center[1]) for pt in route_points)
        if min_dist_km <= 1.2 and risk_score >= 1.9:
            blackspot_matches.append({
                "hotspot_id": idx + 1,
                "distance_m": int(min_dist_km * 1000),
                "risk_score": round(risk_score, 2),
                "coords": (center[0], center[1]),
                "hazard_speed_limit": spot_speed_limit,
                "advisory": f"Slow down to {spot_speed_limit} km/h before entering this high-collision zone."
            })

    if blackspot_matches:
        # Sort by distance
        blackspot_matches.sort(key=lambda x: x["distance_m"])
        top = blackspot_matches[0]
        alerts.append({
            "type": "blackspot",
            "severity": "CRITICAL",
            "icon": "🚨",
            "title": f"Accident Blackspot Proximity Alert ({len(blackspot_matches)} Hotspots Detected)",
            "message": (
                f"Route passes within {top['distance_m']}m of High-Risk Hotspot #{top['hotspot_id']} "
                f"(Historical Severity Score: {top['risk_score']}/3.0). Enforced Safe Speed Limit: {top['hazard_speed_limit']} km/h! "
                f"Double your following distance and decelerate smoothly."
            ),
            "speed_limit_at_stops": top["hazard_speed_limit"],
            "details": blackspot_matches
        })

    # 2. Weather Hazard Alerts
    cond = live_weather.get("condition", "Clear")
    temp = live_weather.get("temperature", 25.0)
    wind = live_weather.get("windspeed", 5.0)

    if cond == "Foggy":
        alerts.append({
            "type": "weather",
            "severity": "HIGH",
            "icon": "🌫️",
            "title": "Dense Fog & Low Visibility Advisory",
            "message": "Severe visibility reduction detected along route. Use low-beam fog headlights, avoid sudden braking, and increase gap distance."
        })
    elif cond == "Rainy":
        alerts.append({
            "type": "weather",
            "severity": "WARNING",
            "icon": "🌧️",
            "title": "Wet Surface / Aquaplaning Hazard",
            "message": "Rainy weather detected. Pavement skid resistance drops by up to 40%. Reduce cruising speed on flyovers and interchange ramps."
        })
    elif wind >= 35.0:
        alerts.append({
            "type": "weather",
            "severity": "MODERATE",
            "icon": "💨",
            "title": "High Crosswind Advisory",
            "message": f"Strong crosswinds of {wind} km/h detected. Exercise caution on elevated corridors and open expressways."
        })

    # 3. Temporal Congestion & Speed Hazard Alerts
    if 8 <= departure_hour <= 10:
        alerts.append({
            "type": "traffic",
            "severity": "INFO",
            "icon": "🚗",
            "title": "Morning Commuter Rush Alert",
            "message": "High vehicle density during morning rush hours. Expect intersection stop-and-go delays. Moderate minor fender-bender risk."
        })
    elif 17 <= departure_hour <= 20:
        alerts.append({
            "type": "traffic",
            "severity": "WARNING",
            "icon": "🚦",
            "title": "Evening Peak Traffic Alert",
            "message": "Peak evening rush hour combined with fading daylight significantly elevates rear-end collision probability."
        })
    elif departure_hour >= 22 or departure_hour <= 4:
        alerts.append({
            "type": "traffic",
            "severity": "CRITICAL",
            "icon": "🌙",
            "title": "Late Night / High-Speed Risk Warning",
            "message": "Night driving presents 3x higher fatal accident severity due to heavy freight truck movement, reduced illumination, and driver fatigue."
        })

    return alerts


def compute_route_speed_and_time(
    distance_km: float,
    road_type: str = "Arterial",
    road_condition: str = "Dry Asphalt",
    weather_condition: str = "Clear",
    departure_hour: int = 14,
    planned_speed_kmh: int = 60,
    vehicle_type: str = "Car / SUV",
    nearby_blackspots_count: int = 0
) -> Dict:
    """
    Computes dynamic road travel time, weather-adapted safe speed limits,
    stopping distance physics, and speed hazard alerts across route corridors.
    """
    # 1. Base Road Speed Limits by Vehicle Type (IRC Regulations)
    base_limits = {
        "Expressway": {"Car / SUV": 100, "Two-Wheeler": 80, "Commercial Truck": 80},
        "Arterial": {"Car / SUV": 60, "Two-Wheeler": 50, "Commercial Truck": 50},
        "Collector": {"Car / SUV": 45, "Two-Wheeler": 40, "Commercial Truck": 40},
        "Local": {"Car / SUV": 30, "Two-Wheeler": 30, "Commercial Truck": 25}
    }
    road_cfg = base_limits.get(road_type, base_limits["Arterial"])
    legal_speed_limit = road_cfg.get(vehicle_type, 60)

    # 2. Weather-Adapted Safe Cruising Speed Limits
    weather_factors = {
        "Clear": 1.0,
        "Cloudy": 0.95,
        "Rainy": 0.70,   # Wet asphalt, hydroplaning risk
        "Foggy": 0.45,   # Low visibility (<1.5 km)
        "Snowy": 0.40,
        "Stormy": 0.50
    }
    w_factor = weather_factors.get(weather_condition, 1.0)
    weather_safe_speed_limit = max(20, int(legal_speed_limit * w_factor))

    # 3. Road Surface Friction and Delay Multipliers
    road_conditions_info = {
        "Dry Asphalt": {"friction": 0.85, "speed_factor": 1.0, "status": "Optimal Grip", "color": "#10b981"},
        "Wet Asphalt": {"friction": 0.52, "speed_factor": 0.82, "status": "Reduced Traction (-39%)", "color": "#f59e0b"},
        "Slippery / Low Grip": {"friction": 0.35, "speed_factor": 0.68, "status": "Critical Slip Risk (-59%)", "color": "#ef4444"},
        "Under Construction": {"friction": 0.58, "speed_factor": 0.55, "status": "Rough / Pothole Delays", "color": "#f97316"}
    }
    rc_info = road_conditions_info.get(road_condition, road_conditions_info["Dry Asphalt"])

    # 4. Temporal Congestion Flow Factor
    if 8 <= departure_hour <= 10:
        traffic_factor = 0.72  # Morning peak
        traffic_label = "Morning Peak Congestion"
    elif 17 <= departure_hour <= 20:
        traffic_factor = 0.68  # Evening peak
        traffic_label = "Evening Peak Congestion"
    elif departure_hour >= 22 or departure_hour <= 4:
        traffic_factor = 1.05  # Late night free-flow
        traffic_label = "Night Free-Flow (Elevated Fatal Risk)"
    else:
        traffic_factor = 0.92  # Normal daytime
        traffic_label = "Normal Daytime Flow"

    # 5. Blackspot Hazard Zone Speed Limit at Stops
    if weather_condition == "Foggy":
        blackspot_stop_speed_limit = 20 if road_type != "Expressway" else 30
    elif weather_condition == "Rainy" or road_condition != "Dry Asphalt":
        blackspot_stop_speed_limit = 25 if road_type != "Expressway" else 35
    else:
        blackspot_stop_speed_limit = 30 if road_type != "Expressway" else 45

    # 6. Calculate Effective Speed & Travel Duration
    effective_target_speed = min(planned_speed_kmh, legal_speed_limit)
    effective_speed = max(15.0, effective_target_speed * w_factor * rc_info["speed_factor"] * traffic_factor)

    # Total estimated travel minutes
    estimated_mins = round((distance_km / effective_speed) * 60.0, 1)
    ideal_mins = round((distance_km / legal_speed_limit) * 60.0, 1)
    weather_traffic_delay_mins = max(0.0, round(estimated_mins - ideal_mins, 1))

    # 7. Stopping Distance Physics (Braking distance + 1.2s driver perception reaction)
    # v in m/s: v = kmh / 3.6; d_braking = v^2 / (2 * mu * g); d_reaction = v * 1.2
    v_ms = planned_speed_kmh / 3.6
    mu = rc_info["friction"]
    g = 9.81
    d_braking = (v_ms ** 2) / (2 * mu * g)
    d_reaction = v_ms * 1.2
    total_stopping_distance_m = round(d_braking + d_reaction, 1)

    # 8. Overspeeding vs Weather Limit Warning
    speed_hazard = "Normal"
    speed_hazard_message = None
    if planned_speed_kmh > weather_safe_speed_limit:
        diff = planned_speed_kmh - weather_safe_speed_limit
        if diff >= 20:
            speed_hazard = "CRITICAL_OVERSPEED"
            speed_hazard_message = (
                f"🚨 Critical Over-speeding! Planned speed {planned_speed_kmh} km/h is {diff} km/h above "
                f"the safe weather-adapted limit ({weather_safe_speed_limit} km/h for {weather_condition} on {road_condition}). "
                f"Stopping distance increases to {total_stopping_distance_m}m!"
            )
        else:
            speed_hazard = "WARNING_OVERSPEED"
            speed_hazard_message = (
                f"⚠️ Excessive Cruising Speed: Planned speed {planned_speed_kmh} km/h exceeds "
                f"recommended weather speed limit of {weather_safe_speed_limit} km/h. Reduce speed to prevent skidding."
            )

    return {
        "planned_speed_kmh": planned_speed_kmh,
        "vehicle_type": vehicle_type,
        "legal_speed_limit_kmh": legal_speed_limit,
        "weather_safe_speed_limit_kmh": weather_safe_speed_limit,
        "blackspot_stop_speed_limit_kmh": blackspot_stop_speed_limit,
        "road_condition": road_condition,
        "friction_coefficient": rc_info["friction"],
        "road_condition_status": rc_info["status"],
        "effective_speed_kmh": round(effective_speed, 1),
        "estimated_minutes": estimated_mins,
        "ideal_minutes": ideal_mins,
        "delay_minutes": weather_traffic_delay_mins,
        "stopping_distance_m": total_stopping_distance_m,
        "traffic_status": traffic_label,
        "speed_hazard": speed_hazard,
        "speed_hazard_message": speed_hazard_message
    }
