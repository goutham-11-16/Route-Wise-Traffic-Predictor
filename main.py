"""
CLI Pipeline Runner for Route-Wise Traffic Accident Risk Prediction System
Course: 213CSE2301 - Predictive Analytics (Autonomy)
"""

import argparse
import sys
import os

def run_data():
    from src.data_pipeline import run_pipeline
    print("=== Step 1: Running Data Pipeline ===")
    run_pipeline('data')

def run_models():
    from src.models import train_and_save
    print("\n=== Step 2: Training & Evaluating Machine Learning Models ===")
    train_and_save('data/cleaned_accidents_6469.csv', 'models')

def run_plots():
    from src.eda import generate_all_eda_plots
    print("\n=== Step 3: Generating Presentation Figures & EDA Plots ===")
    generate_all_eda_plots('data/cleaned_accidents_6469.csv', 'static')

def run_route(origin: str, dest: str, hour: int, weather: str, road: str):
    from src.models import AccidentRiskModel
    from src.router import get_coordinates, RouteRiskAnalyzer
    from src.live_services import fetch_live_weather
    from src.data_pipeline import get_time_category

    print(f"\n=== Real-Road Route & Risk Analysis: '{origin}' ➔ '{dest}' ===")
    c1 = get_coordinates(origin)
    c2 = get_coordinates(dest)
    if not c1 or not c2:
        print(f"❌ Error: Could not resolve coordinates for '{origin}' or '{dest}'.")
        return

    time_cat = get_time_category(hour)
    model = AccidentRiskModel()
    model.load_artifacts('models')
    analyzer = RouteRiskAnalyzer(model)

    # Fetch live weather at origin
    live_w = fetch_live_weather(c1[0], c1[1])
    effective_weather = live_w.get('condition', weather)

    res = analyzer.analyze_route(c1, c2, hour, time_cat, weather=effective_weather, road_type=road, live_weather_info=live_w)
    rec = analyzer.recommend_safest_departure_time(c1, c2, current_hour=hour, current_time_cat=time_cat, road_type=road)

    print("-" * 55)
    print(f"📍 Origin Coords:        {c1}")
    print(f"🎯 Destination Coords:   {c2}")
    print(f"🛣️ Routing Source:       {res.get('routing_source', 'OSRM')}")
    print(f"📏 Driving Distance:     {res['distance_km']} km")
    print(f"⏱️ Estimated Duration:   {res['estimated_minutes']} mins")
    print(f"🌤️ Live Route Weather:   {live_w['condition']} ({live_w['temperature']}°C, Wind: {live_w['windspeed']} km/h) [Open-Meteo]")
    print(f"⚠️ Journey Risk:         {res['journey_risk_tier']} (Score: {res['mean_risk_score']})")
    print(f"🕒 Selected Departure:   {time_cat} ({hour:02d}:00 hrs)")
    print("-" * 55)

    alerts = res.get('alerts', [])
    if alerts:
        print(f"🚨 ACTIVE ROAD & HAZARD ALERTS ({len(alerts)}):")
        for a in alerts:
            print(f"   [{a['severity']}] {a['icon']} {a['title']}")
            print(f"      ↳ {a['message']}")
        print("-" * 55)

    print("🌟 SAFER TRAVEL TIME RECOMMENDATION:")
    print(f"   Optimal Departure:    {rec['safest_hour_label']} ({rec['safest_time_category']})")
    print(f"   Risk Reduction:       {rec['risk_reduction_pct']}% safer than planned departure")
    print("-" * 55)
    print("Departure Window Comparison:")
    for w in rec['all_time_evaluations']:
        print(f" - {w['weather_icon']} {w['time_category']:<10} (Hour {w['nominal_hour']:02d}:00): Risk Tier {w['journey_risk_tier']:<14} Score {w['mean_risk_score']}")
    print("-" * 55)

def main():
    parser = argparse.ArgumentParser(description="Route Accident Risk Prediction System CLI")
    parser.add_argument('--all', action='store_true', help="Run complete pipeline")
    parser.add_argument('--data', action='store_true', help="Generate raw and clean datasets")
    parser.add_argument('--train', action='store_true', help="Train and evaluate ML models")
    parser.add_argument('--eda', action='store_true', help="Generate slide EDA charts")
    parser.add_argument('--route', action='store_true', help="Analyze risk for a route")
    parser.add_argument('--origin', type=str, default="Connaught Place Delhi", help="Origin location")
    parser.add_argument('--dest', type=str, default="Noida Expressway", help="Destination location")
    parser.add_argument('--hour', type=int, default=22, help="Departure hour (0-23)")
    parser.add_argument('--weather', type=str, default="Clear", help="Weather condition")
    parser.add_argument('--road', type=str, default="Arterial", help="Road type")
    parser.add_argument('--server', action='store_true', help="Run FastAPI backend on port 8001")
    parser.add_argument('--vite', action='store_true', help="Run Vite React frontend on port 5173")
    parser.add_argument('--dev', action='store_true', help="Run both FastAPI backend and Vite frontend concurrently")
    parser.add_argument('--app', action='store_true', help="Run legacy Streamlit app")

    args = parser.parse_args()

    if args.server:
        import uvicorn
        print("🚀 Starting FastAPI REST backend on http://127.0.0.1:8001...")
        uvicorn.run("backend.api:app", host="127.0.0.1", port=8001, reload=True)
        return

    if args.vite:
        print("⚡ Starting Vite dev server on http://localhost:5173...")
        os.system("cd frontend && npm run dev")
        return

    if args.dev:
        import subprocess
        print("🚀 Launching FastAPI Backend (Port 8001) & Vite Frontend (Port 5173)...")
        b_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "8001"])
        try:
            subprocess.run(["npm", "run", "dev"], cwd="frontend")
        except KeyboardInterrupt:
            print("\nShutting down dev servers...")
        finally:
            b_proc.terminate()
        return

    if args.app:
        os.system(".venv/bin/streamlit run app.py")
        return

    if args.all or (not any([args.data, args.train, args.eda, args.route])):
        run_data()
        run_models()
        run_plots()
        run_route(args.origin, args.dest, args.hour, args.weather, args.road)
    else:
        if args.data: run_data()
        if args.train: run_models()
        if args.eda: run_plots()
        if args.route: run_route(args.origin, args.dest, args.hour, args.weather, args.road)

if __name__ == '__main__':
    main()
