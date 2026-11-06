"""
Geospatial Routing & Safer Travel Time Recommendation Engine
Integrates Real Road Routing (OSRM), Live Weather (Open-Meteo), and Intelligent Hazard Alerts.
Course: 213CSE2301 - Predictive Analytics (Autonomy)
"""

import math
import time
import numpy as np
from typing import Tuple, List, Dict, Optional
from geopy.geocoders import ArcGIS, Nominatim

from src.live_services import (
    fetch_osrm_route, fetch_live_weather, fetch_hourly_weather_forecast,
    generate_road_hazard_alerts, haversine_km, compute_route_speed_and_time
)

# Built-in fast offline geocoding cache for major Indian points of interest
POPULAR_LOCATIONS = {
    'connaught place delhi': (28.6315, 77.2167),
    'connaught place': (28.6315, 77.2167),
    'india gate delhi': (28.6129, 77.2295),
    'india gate': (28.6129, 77.2295),
    'noida sector 18': (28.5708, 77.3271),
    'noida expressway': (28.5100, 77.3800),
    'cyber city gurgaon': (28.4950, 77.0895),
    'gurgaon': (28.4595, 77.0266),
    'gurugram': (28.4595, 77.0266),
    'delhi airport': (28.5562, 77.1000),
    'igi airport': (28.5562, 77.1000),
    'anand vihar': (28.6469, 77.3160),
    'dwarka': (28.5921, 77.0460),
    'kashmere gate': (28.6675, 77.2285),
    'faridabad': (28.4089, 77.3178),
    'ghaziabad': (28.6692, 77.4538),
    'bangalore': (12.9716, 77.5946),
    'mysore': (12.2958, 76.6394),
    'tirupati': (13.6288, 79.4192),
    'madurai': (9.9252, 78.1198),
    'chennai': (13.0827, 80.2707),
    'hyderabad': (17.3850, 78.4867),
    'mumbai': (19.0760, 72.8777),
    'pune': (18.5204, 73.8567),
    'chandigarh': (30.7333, 76.7794),
    'jaipur': (26.9124, 75.7873),
    'agra': (27.1767, 78.0081),
}


def get_coordinates(place_query: str) -> Optional[Tuple[float, float]]:
    """Resolves place query to (latitude, longitude)."""
    if not place_query:
        return None
    query_clean = place_query.lower().strip().replace(',', ' ')
    query_tokens = ' '.join(query_clean.split())

    for key, coords in POPULAR_LOCATIONS.items():
        if key in query_tokens or query_tokens in key:
            return coords

    try:
        arcgis = ArcGIS(timeout=4)
        loc = arcgis.geocode(place_query + ", India")
        if loc:
            return (round(loc.latitude, 6), round(loc.longitude, 6))
    except Exception:
        pass

    try:
        nom = Nominatim(user_agent="pa_traffic_risk_v4", timeout=4)
        loc = nom.geocode(place_query + ", India")
        if loc:
            return (round(loc.latitude, 6), round(loc.longitude, 6))
    except Exception:
        pass

    return None


def search_locations(query: str, max_results: int = 6) -> List[Dict]:
    """Searches for locations matching query with address and coordinates."""
    if not query or len(query.strip()) < 2:
        return []

    results = []
    seen = set()
    q_lower = query.lower().strip()

    # 1. Local landmarks
    for name, coords in POPULAR_LOCATIONS.items():
        if q_lower in name or name in q_lower:
            label = f"{name.title()} (Verified Hub)"
            coord_key = (round(coords[0], 3), round(coords[1], 3))
            if coord_key not in seen:
                seen.add(coord_key)
                results.append({'name': label, 'coords': coords, 'source': 'Verified Database'})

    # 2. ArcGIS
    try:
        arcgis = ArcGIS(timeout=4)
        locs = arcgis.geocode(query + ", India", exactly_one=False)
        if locs:
            for l in locs:
                coord_key = (round(l.latitude, 3), round(l.longitude, 3))
                if coord_key not in seen:
                    seen.add(coord_key)
                    results.append({
                        'name': l.address,
                        'coords': (round(l.latitude, 6), round(l.longitude, 6)),
                        'source': 'ArcGIS Geocoder'
                    })
                if len(results) >= max_results:
                    break
    except Exception:
        pass

    # 3. Nominatim
    if len(results) < max_results:
        try:
            nom = Nominatim(user_agent="pa_location_search_v4", timeout=4)
            locs = nom.geocode(query + ", India", exactly_one=False, limit=max_results)
            if locs:
                for l in locs:
                    coord_key = (round(l.latitude, 3), round(l.longitude, 3))
                    if coord_key not in seen:
                        seen.add(coord_key)
                        results.append({
                            'name': l.address,
                            'coords': (round(l.latitude, 6), round(l.longitude, 6)),
                            'source': 'OpenStreetMap'
                        })
                    if len(results) >= max_results:
                        break
        except Exception:
            pass

    return results


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return haversine_km(lat1, lon1, lat2, lon2)


def generate_fallback_route(start_coords: Tuple[float, float],
                            end_coords: Tuple[float, float],
                            num_points: int = 30) -> List[Tuple[float, float]]:
    """Geometric road interpolation fallback if live network is offline."""
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    dx = lon2 - lon1
    dy = lat2 - lat1
    perp_dx = -dy
    perp_dy = dx
    norm = math.sqrt(perp_dx ** 2 + perp_dy ** 2) or 1.0
    perp_dx /= norm
    perp_dy /= norm

    curve_amp = 0.008 * math.sin(lat1 + lon1)
    route = []
    for i in range(num_points):
        frac = i / (num_points - 1)
        perturb = math.sin(frac * math.pi) * curve_amp
        lat = lat1 + frac * (lat2 - lat1) + perturb * perp_dy
        lon = lon1 + frac * (lon2 - lon1) + perturb * perp_dx
        route.append((round(lat, 6), round(lon, 6)))
    return route


class RouteRiskAnalyzer:
    def __init__(self, model_engine):
        self.model = model_engine

    def analyze_route(self,
                      start_coords: Tuple[float, float],
                      end_coords: Tuple[float, float],
                      hour: int,
                      time_cat: str,
                      weather: str = "Clear",
                      road_type: str = "Arterial",
                      live_weather_info: Optional[Dict] = None,
                      route_points: Optional[List[Tuple[float, float]]] = None,
                      dist_km: Optional[float] = None,
                      duration_mins: Optional[float] = None,
                      routing_source: Optional[str] = None,
                      generate_alerts: bool = True,
                      planned_speed_kmh: int = 60,
                      vehicle_type: str = "Car / SUV",
                      road_condition: str = "Dry Asphalt") -> Dict:
        """
        Calculates multi-segment route risk along real OSRM road geometry.
        Generates live hazard alerts and segment classifications.
        """
        # 1. Fetch Real Driving Road Route from OSRM (or reuse provided geometry)
        if route_points is None or len(route_points) < 2:
            osrm_res = fetch_osrm_route(start_coords, end_coords)
            if osrm_res and len(osrm_res.get("geometry", [])) > 2:
                route_points = osrm_res["geometry"]
                dist_km = osrm_res["distance_km"]
                duration_mins = osrm_res["duration_mins"]
                routing_source = "OSRM Live Real-Road Driving Engine"
            else:
                route_points = generate_fallback_route(start_coords, end_coords, num_points=30)
                straight_dist = haversine_km(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
                dist_km = round(straight_dist * 1.25, 2)
                duration_mins = round((dist_km / 45.0) * 60.0, 1)
                routing_source = "Internal Curvature Kinematic Model"
        else:
            dist_km = dist_km or 10.0
            duration_mins = duration_mins or 20.0
            routing_source = routing_source or "OSRM Live Real-Road Driving Engine"

        # 2. Sample waypoints for segment risk calculation (up to 35 evenly spaced nodes)
        step = max(1, len(route_points) // 35)
        sampled_points = route_points[::step]
        if route_points[-1] not in sampled_points:
            sampled_points.append(route_points[-1])

        # 3. Vectorized evaluation of segment risks
        lats = [pt[0] for pt in sampled_points]
        lons = [pt[1] for pt in sampled_points]
        segment_results = self.model.predict_batch_risk(lats, lons, hour, time_cat, weather, road_type)
        composite_scores = [s['composite_score'] for s in segment_results]
        high_risk_count = sum(1 for s in segment_results if s['severity'] == 'High')

        mean_comp = float(np.mean(composite_scores)) if composite_scores else 0.3
        max_comp = float(np.max(composite_scores)) if composite_scores else 0.5
        high_risk_ratio = high_risk_count / len(sampled_points) if sampled_points else 0.0

        # Classify overall journey risk tier
        if mean_comp >= 0.58 or high_risk_ratio >= 0.35:
            journey_tier = "HIGH RISK"
            risk_color = "#d9383a"
        elif mean_comp >= 0.35 or high_risk_ratio >= 0.15:
            journey_tier = "MODERATE RISK"
            risk_color = "#e67e22"
        else:
            journey_tier = "LOW RISK"
            risk_color = "#27ae60"

        # 4. Generate Live Road Hazard & Safety Alerts (only when enabled, using sampled waypoints)
        alerts = []
        if generate_alerts:
            cluster_centers = self.model.kmeans.cluster_centers_
            cluster_risk_df = self.model.cluster_risk_df
            w_info = live_weather_info or {"condition": weather, "temperature": 27.0, "windspeed": 5.0}
            alerts = generate_road_hazard_alerts(
                sampled_points, w_info, hour, cluster_centers, cluster_risk_df
            )

        # 5. Compute Weather-Adapted Speed Limits, Physics Stopping Distance & Estimated Time
        speed_metrics = compute_route_speed_and_time(
            distance_km=dist_km,
            road_type=road_type,
            road_condition=road_condition,
            weather_condition=weather,
            departure_hour=hour,
            planned_speed_kmh=planned_speed_kmh,
            vehicle_type=vehicle_type,
            nearby_blackspots_count=len(alerts)
        )

        if speed_metrics.get("speed_hazard_message") and generate_alerts:
            alerts.insert(0, {
                "type": "overspeed",
                "severity": "CRITICAL" if speed_metrics["speed_hazard"] == "CRITICAL_OVERSPEED" else "WARNING",
                "icon": "⚡",
                "title": "Weather & Road Condition Speed Violation",
                "message": speed_metrics["speed_hazard_message"]
            })

        effective_duration_mins = speed_metrics["estimated_minutes"]

        return {
            'route_points': route_points,
            'distance_km': dist_km,
            'estimated_minutes': effective_duration_mins,
            'routing_source': routing_source,
            'journey_risk_tier': journey_tier,
            'risk_color': risk_color,
            'mean_risk_score': round(mean_comp, 3),
            'peak_risk_score': round(max_comp, 3),
            'high_risk_segment_ratio': round(high_risk_ratio, 3),
            'segment_details': segment_results,
            'speed_time_metrics': speed_metrics,
            'alerts': alerts
        }

    def recommend_safest_departure_time(self,
                                        start_coords: Tuple[float, float],
                                        end_coords: Tuple[float, float],
                                        current_hour: int,
                                        current_time_cat: str,
                                        weather: Optional[str] = None,
                                        road_type: str = "Arterial",
                                        base_analysis: Optional[Dict] = None,
                                        planned_speed_kmh: int = 60,
                                        vehicle_type: str = "Car / SUV",
                                        road_condition: str = "Dry Asphalt",
                                        **kwargs) -> Dict:
        """
        Pulls the real 24-hour weather forecast from Open-Meteo and combines it
        with temporal collision models to recommend the safest departure time.
        """
        # Fetch actual 24-hour hourly forecast along the route from Open-Meteo
        hourly_forecast = fetch_hourly_weather_forecast(start_coords[0], start_coords[1])

        from src.data_pipeline import get_time_category

        cached_points = base_analysis.get('route_points') if base_analysis else None
        cached_dist = base_analysis.get('distance_km') if base_analysis else None
        cached_dur = base_analysis.get('estimated_minutes') if base_analysis else None
        cached_src = base_analysis.get('routing_source') if base_analysis else None

        # Evaluate all 24 hours of the day
        hour_evaluations = []
        for h in range(24):
            t_cat = get_time_category(h)
            h_weather = hourly_forecast.get(h, {}).get("condition", "Clear")
            analysis = self.analyze_route(
                start_coords, end_coords, h, t_cat, weather=h_weather, road_type=road_type,
                route_points=cached_points, dist_km=cached_dist, duration_mins=cached_dur,
                routing_source=cached_src, generate_alerts=False,
                planned_speed_kmh=planned_speed_kmh, vehicle_type=vehicle_type,
                road_condition=road_condition
            )
            hour_evaluations.append({
                "hour": h,
                "hour_label": f"{h:02d}:00",
                "time_category": t_cat,
                "weather": h_weather,
                "weather_desc": hourly_forecast.get(h, {}).get("desc", "Normal"),
                "weather_icon": hourly_forecast.get(h, {}).get("icon", "☀️"),
                "temperature": hourly_forecast.get(h, {}).get("temperature", 25.0),
                "precip_pct": hourly_forecast.get(h, {}).get("precip_pct", 0),
                "mean_risk_score": analysis["mean_risk_score"],
                "journey_risk_tier": analysis["journey_risk_tier"],
                "risk_color": analysis["risk_color"]
            })

        # Evaluate representative operational windows (Morning, Afternoon, Evening, Night)
        window_reps = [
            ('Morning', 9),
            ('Afternoon', 14),
            ('Evening', 19),
            ('Night', 23)
        ]

        window_evals = []
        for w_name, rep_h in window_reps:
            match = next((item for item in hour_evaluations if item['hour'] == rep_h), hour_evaluations[0])
            window_evals.append({
                'time_category': w_name,
                'nominal_hour': rep_h,
                'journey_risk_tier': match['journey_risk_tier'],
                'mean_risk_score': match['mean_risk_score'],
                'risk_color': match['risk_color'],
                'weather': match['weather'],
                'weather_icon': match['weather_icon']
            })

        # Best hour overall (lowest mean risk score)
        best_hour_entry = min(hour_evaluations, key=lambda x: x["mean_risk_score"])
        current_hour_entry = next((e for e in hour_evaluations if e["hour"] == current_hour), hour_evaluations[0])

        current_score = current_hour_entry["mean_risk_score"]
        safest_score = best_hour_entry["mean_risk_score"]

        risk_reduction = 0.0
        if current_score > 0:
            risk_reduction = max(0.0, ((current_score - safest_score) / current_score) * 100.0)

        window_evals.sort(key=lambda x: x["mean_risk_score"])
        safest_window = window_evals[0]

        return {
            'safest_hour': best_hour_entry['hour'],
            'safest_hour_label': best_hour_entry['hour_label'],
            'safest_time_category': safest_window['time_category'],
            'safest_risk_tier': best_hour_entry['journey_risk_tier'],
            'safest_risk_score': safest_score,
            'current_hour_risk_score': current_score,
            'risk_reduction_pct': round(risk_reduction, 1),
            'all_time_evaluations': window_evals,
            'hourly_24_evaluations': hour_evaluations
        }
