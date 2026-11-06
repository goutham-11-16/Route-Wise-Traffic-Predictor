"""
FastAPI REST Backend for Route-Wise Traffic Accident Risk Prediction
Course: 213CSE2301 - Predictive Analytics
Serves routing, live weather, machine learning inference, hazard alerts, and EDA metrics.
"""

import os
import json
import pandas as pd
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Core project imports
from src.models import AccidentRiskModel
from src.router import RouteRiskAnalyzer, search_locations, get_coordinates, POPULAR_LOCATIONS
from src.live_services import fetch_live_weather, fetch_hourly_weather_forecast
from src.data_pipeline import get_time_category

app = FastAPI(
    title="Route - Wise AI API",
    description="Route - Wise AI: Route Accident Risk Prediction and Safer Travel Time Recommendation System",
    version="2.0.0"
)

# Enable CORS for Vite dev server (port 5173, 3000, and any localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory for slide charts & EDA
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize ML Model Engine and Router Analyzer once at startup
engine = AccidentRiskModel()
engine.load_artifacts(model_dir=MODELS_DIR)
analyzer = RouteRiskAnalyzer(engine)

# Load Model Metadata
metadata_path = os.path.join(MODELS_DIR, "model_metadata.json")
model_metadata = {}
if os.path.exists(metadata_path):
    with open(metadata_path, "r") as f:
        model_metadata = json.load(f)


# Request schemas
class RouteAnalysisRequest(BaseModel):
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    origin_coords: List[float] = Field(..., description="[latitude, longitude] of origin")
    dest_coords: List[float] = Field(..., description="[latitude, longitude] of destination")
    departure_hour: int = Field(default=9, ge=0, le=23)
    road_type: str = Field(default="Arterial")
    weather_override: Optional[str] = None
    planned_speed_kmh: int = Field(default=60, ge=20, le=140)
    vehicle_type: str = Field(default="Car / SUV")
    road_condition: str = Field(default="Dry Asphalt")


@app.get("/api/health")
def health_check():
    """Health status and course project information."""
    return {
        "status": "online",
        "service": "Route - Wise AI Risk Engine",
        "project_name": "Route - Wise AI",
        "course": "213CSE2301 - Predictive Analytics",
        "faculty": "Dr. N. Subbulakshmi",
        "models_loaded": engine.rf_model is not None and engine.kmeans is not None,
        "dataset_records": model_metadata.get("total_records", 6469),
        "primary_model_accuracy": model_metadata.get("rf_metrics", {}).get("Accuracy", 0.8416)
    }


@app.get("/api/search")
def search_places(q: str = Query(..., min_length=2, description="Place name query")):
    """
    Autocomplete search for Indian landmarks, cities, and road hubs.
    100% free with multi-tier fallback (local cache -> ArcGIS -> Nominatim).
    """
    results = search_locations(q, max_results=7)
    return {"query": q, "count": len(results), "results": results}


@app.get("/api/live-weather")
def get_live_weather(lat: float, lon: float):
    """Fetches real-time weather from Open-Meteo at coordinates (100% free)."""
    weather = fetch_live_weather(lat, lon)
    return weather


@app.post("/api/analyze-route")
def analyze_route(req: RouteAnalysisRequest):
    """
    Full end-to-end route analysis:
    1. Fetches real driving road path from OSRM (100% free, real geometry).
    2. Pulls real-time weather and 24-hour forecast from Open-Meteo.
    3. Evaluates segment-by-segment ML risk scores using Random Forest & K-Means clusters.
    4. Identifies nearby accident blackspots and road hazards.
    5. Calculates dynamic speed limits at hazard stops and weather-adjusted travel times.
    6. Calculates 24-hour temporal risk curve and recommends safest departure time.
    """
    try:
        origin = (req.origin_coords[0], req.origin_coords[1])
        dest = (req.dest_coords[0], req.dest_coords[1])
        hour = req.departure_hour
        time_cat = get_time_category(hour)

        # 1. Real-time weather at origin
        live_weather = fetch_live_weather(origin[0], origin[1])
        effective_weather = req.weather_override if req.weather_override else live_weather.get("condition", "Clear")

        # 2. Analyze current journey at selected hour
        route_analysis = analyzer.analyze_route(
            start_coords=origin,
            end_coords=dest,
            hour=hour,
            time_cat=time_cat,
            weather=effective_weather,
            road_type=req.road_type,
            live_weather_info=live_weather,
            planned_speed_kmh=req.planned_speed_kmh,
            vehicle_type=req.vehicle_type,
            road_condition=req.road_condition
        )

        # 3. Compute 24-hour safe departure recommendation
        safe_rec = analyzer.recommend_safest_departure_time(
            start_coords=origin,
            end_coords=dest,
            current_hour=hour,
            current_time_cat=time_cat,
            weather=effective_weather,
            road_type=req.road_type,
            base_analysis=route_analysis,
            planned_speed_kmh=req.planned_speed_kmh,
            vehicle_type=req.vehicle_type,
            road_condition=req.road_condition
        )

        return {
            "origin": {"name": req.origin_name or "Origin", "coords": origin},
            "destination": {"name": req.destination_name or "Destination", "coords": dest},
            "departure_hour": hour,
            "time_category": time_cat,
            "road_type": req.road_type,
            "road_condition": req.road_condition,
            "vehicle_type": req.vehicle_type,
            "planned_speed_kmh": req.planned_speed_kmh,
            "weather": live_weather,
            "effective_weather": effective_weather,
            "route": {
                "distance_km": route_analysis["distance_km"],
                "estimated_minutes": route_analysis["estimated_minutes"],
                "routing_source": route_analysis["routing_source"],
                "journey_risk_tier": route_analysis["journey_risk_tier"],
                "risk_color": route_analysis["risk_color"],
                "mean_risk_score": route_analysis["mean_risk_score"],
                "peak_risk_score": route_analysis["peak_risk_score"],
                "high_risk_segment_ratio": route_analysis["high_risk_segment_ratio"],
                "route_points": route_analysis["route_points"],  # [[lat, lon], ...]
                "segment_details": route_analysis["segment_details"],
                "speed_time_metrics": route_analysis.get("speed_time_metrics", {}),
                "alerts": route_analysis["alerts"]
            },
            "recommendation": safe_rec
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route analysis error: {str(e)}")


@app.get("/api/blackspots")
def get_blackspots():
    """Returns the 20 K-Means accident blackspot cluster centroids and their historical risk metrics."""
    if engine.cluster_risk_df is None or engine.kmeans is None:
        return {"clusters": []}

    clusters = []
    centers = engine.kmeans.cluster_centers_
    for idx, row in engine.cluster_risk_df.iterrows():
        c_id = int(row['Cluster'])
        lat = float(centers[c_id][0])
        lon = float(centers[c_id][1])
        score = float(row['Cluster_Risk_Score'])
        clusters.append({
            "cluster_id": c_id,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "risk_score": round(score, 3),
            "risk_level": "High" if score >= 2.05 else ("Medium" if score >= 1.80 else "Low")
        })

    return {"count": len(clusters), "clusters": clusters}


@app.get("/api/model-performance")
def get_model_performance():
    """
    Returns comparative evaluation metrics across all 6 curriculum algorithms
    and the Random Forest confusion matrix & feature importances.
    """
    return {
        "dataset": {
            "total_records": model_metadata.get("total_records", 6469),
            "train_records": model_metadata.get("train_records", 5175),
            "test_records": model_metadata.get("test_records", 1294),
            "target_classes": model_metadata.get("target_classes", ["High", "Low", "Medium"]),
            "features": model_metadata.get("feature_names", [])
        },
        "model_comparisons": model_metadata.get("model_comparisons", {}),
        "primary_model": {
            "name": "Random Forest Classifier",
            "metrics": model_metadata.get("rf_metrics", {}),
            "confusion_matrix": model_metadata.get("confusion_matrix", []),
            "feature_importances": model_metadata.get("feature_importances", {}),
            "permutation_importances": model_metadata.get("permutation_importances", {})
        }
    }


@app.get("/api/eda-charts")
def get_eda_charts():
    """Returns metadata and URLs for presentation slides (Slides 5, 6, 8, 9)."""
    charts = [
        {
            "id": "accident_distribution_time",
            "title": "Accident Distribution Across Time of Day",
            "slide": "Slide 5",
            "description": "Historical accident frequencies by 4 operational time windows (Morning: 1,910, Afternoon: 2,230, Evening: 1,090, Night: 1,239).",
            "url": "/static/accident_distribution_time.png"
        },
        {
            "id": "accident_severity_time",
            "title": "Accident Severity Breakdown by Time Category",
            "slide": "Slide 6",
            "description": "Distribution of Low, Medium, and High severity collisions across Morning, Afternoon, Evening, and Night.",
            "url": "/static/accident_severity_time.png"
        },
        {
            "id": "hourly_frequency",
            "title": "24-Hour Accident Frequency Curve",
            "slide": "Slide 6 (Supplementary)",
            "description": "Continuous hourly accident counts showing critical rush hour and late night distribution.",
            "url": "/static/hourly_frequency.png"
        },
        {
            "id": "severity_distribution",
            "title": "Overall Severity Distribution (6,469 Records)",
            "slide": "Slide 5 (Supplementary)",
            "description": "Overall balance of target classes: Medium (2,636), Low (2,280), High (1,553).",
            "url": "/static/severity_distribution.png"
        },
        {
            "id": "correlation_heatmap",
            "title": "Feature Correlation Heatmap",
            "slide": "Slide 7",
            "description": "Pearson correlation matrix among Hour, Time Category, Weather, Road Type, and Cluster Risk Score.",
            "url": "/static/correlation_heatmap.png"
        },
        {
            "id": "feature_importance",
            "title": "Random Forest Feature Importances",
            "slide": "Slide 8",
            "description": "MDI importance ranking highlighting Hour and Time Category as primary collision predictors.",
            "url": "/static/feature_importance.png"
        },
        {
            "id": "confusion_matrix",
            "title": "Random Forest Confusion Matrix (1,294 Test Records)",
            "slide": "Slide 9",
            "description": "Multiclass confusion matrix demonstrating robust diagonal discrimination across High, Low, and Medium tiers.",
            "url": "/static/confusion_matrix.png"
        }
    ]
    return {"charts": charts}


@app.get("/api/accidents-sample")
def get_accidents_sample(limit: int = Query(50, ge=1, le=200)):
    """Returns a sample of the cleaned 6,469 records for data exploration."""
    cleaned_file = os.path.join(DATA_DIR, "cleaned_accidents_6469.csv")
    if not os.path.exists(cleaned_file):
        return {"records": []}

    df = pd.read_csv(cleaned_file).head(limit)
    return {
        "total_in_dataset": 6469,
        "sample_size": len(df),
        "records": df.to_dict(orient="records")
    }
