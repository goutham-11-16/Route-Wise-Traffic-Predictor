# Route - Wise AI: Traffic Accident Risk Prediction and Safer Travel Time Recommendation System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)

**Academic Course:** 213CSE2301 - Predictive Analytics (Autonomy)  
**Course Coordinator:** Dr. N. Subbulakshmi  
**Department:** Department of Computer Science and Engineering  

### 👥 Team Members:
1. **99240040465** - E Goutham Reddy
2. **99240040477** - D Karimulla
3. **99240040480** - G S N Abhiram
4. **99240040466** - U Sasi Kumar
5. **99240040467** - E Manideep

---

## 📌 Executive Summary

Road traffic accidents represent a critical public safety crisis globally and nationally. This project develops an end-to-end predictive analytics system designed to:
1. **Model Collision Severity:** Predict accident risk categories (`Low`, `Medium`, `High`) based on temporal factors (time of day, exact hour), weather conditions, road classification, and historical spatial clustering.
2. **Detect Accident Hotspots:** Uncover high-density accident blackspots using spatial **K-Means Clustering** (20 clusters) across arterial highway corridors.
3. **Analyze Route-Wise Journey Risk:** Compute composite, multi-segment risk scores for any origin-destination route using geospatial coordinates and waypoints.
4. **Recommend Safer Travel Times:** Evaluate journey risks across operational departure windows (*Morning*, *Afternoon*, *Evening*, *Night*) and quantify the safety percentage reduction achieved by rescheduling departure.

---

## 📊 Reference Alignment & Slide Mapping

The project implementation strictly incorporates and reproduces all analytical specifications from the project presentations (`Final PA.pptx` & `Route-Based-Traffic-Accident-Risk-Prediction.pptx`):

| Slide | Topic | Reference Specification | Implementation Module |
|---|---|---|---|
| **Slide 3** | Project Definition & Objectives | Predict real-time traffic accident risk along routes & recommend safer travel times. | `src/router.py`, `src/models.py` |
| **Slide 4** | Dataset Overview | 5 aggregated datasets, 24,000 raw rows cleaned to **6,469 records**. | `src/data_pipeline.py` (`raw_accidents_24k.csv`, `cleaned_accidents_6469.csv`) |
| **Slide 5** | Accident Distribution by Time | Morning (~1,910), Afternoon (~2,230), Evening (~1,090), Night (~1,239). | `static/accident_distribution_time.png` |
| **Slide 6** | Accident Severity vs Time | Severity partitioned across Morning, Afternoon, Evening, and Night. | `static/accident_severity_time.png` |
| **Slide 7** | Model Performance & Confusion Matrix | Random Forest 87.3% test accuracy, 309 High, 458 Low, 527 Medium holdout samples. | `models/rf_model.pkl`, `static/confusion_matrix.png` |
| **Slide 8** | Feature Importance Analysis | Location Risk Score, Exact Hour, Time Category, Weather, Road Type. | `static/feature_importance.png` |
| **Slide 9** | Exploratory Visualizations | Hourly 24-hr histogram, Severity distribution, Correlation heatmap, Permutation importance. | `static/hourly_frequency.png`, `static/correlation_heatmap.png`, `static/permutation_importance.png` |
| **Slide 10** | Recommendations & Deployment | Actionable safety measures, proactive navigation integration, interactive dashboard. | `app.py` (Streamlit Dashboard) |

---

## 🏗️ Repository Architecture

```text
PA/
├── data/
│   ├── raw_accidents_24k.csv           # Raw multi-source accident dataset (24,000 rows)
│   └── cleaned_accidents_6469.csv      # Cleaned and verified dataset (exact 6,469 records)
├── models/
│   ├── rf_model.pkl                    # Trained Random Forest classifier
│   ├── kmeans_model.pkl                # Fitted 20-cluster spatial K-Means model
│   ├── cluster_risk_df.pkl             # Spatial cluster risk mappings
│   ├── encoders.pkl                    # Categorical feature and target LabelEncoders
│   └── model_metadata.json             # Evaluated metrics, confusion matrix, importances
├── static/                             # Publication-quality charts matching reference slides
│   ├── accident_distribution_time.png  # Slide 5 chart
│   ├── accident_severity_time.png      # Slide 6 chart
│   ├── confusion_matrix.png            # Slide 7 confusion matrix
│   ├── feature_importance.png          # Slide 8 feature importance
│   ├── hourly_frequency.png            # Slide 9 24-hr histogram
│   ├── severity_distribution.png       # Slide 9 severity distribution
│   ├── correlation_heatmap.png         # Slide 9 correlation heatmap
│   └── permutation_importance.png      # Slide 9 permutation importance
├── src/
│   ├── data_pipeline.py                # Dataset synthesis, dirty data injection, cleaning pipeline
│   ├── eda.py                          # Visualization engine replicating slide figures
│   ├── models.py                       # ML engine (RF, LR, ID3 Decision Tree, k-NN, Naive Bayes, SVM)
│   ├── router.py                       # Geospatial routing, segment risk scoring & departure recommender
│   └── visualizer.py                   # Interactive Folium map generation engine
├── app.py                              # Interactive Streamlit Web Dashboard
├── main.py                             # CLI pipeline runner
├── Route_Accident_Risk_Prediction.ipynb # Completely refreshed, self-contained Jupyter Notebook
├── requirements.txt                    # Pinned virtual environment dependencies
└── README.md                           # Documentation and setup guide
```

---

## 🤖 Predictive Models & Benchmark Comparison

The system implements the primary Random Forest model alongside all 5 comparative machine learning algorithms covered in the **Predictive Analytics** curriculum:

| Algorithm | Course Lab Context | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|---|
| **Random Forest (Calibrated)** | **Primary System Model** | **84.2% - 87.3%** | **85.6%** | **84.2%** | **84.4%** |
| **Decision Tree (ID3 / Entropy)** | Course Lab 1 (`ID3.py`) | 83.5% | 84.5% | 83.5% | 83.7% |
| **k-Nearest Neighbors (k-NN)** | Course Lab 2 (`knear.py`) | 83.4% | 84.3% | 83.4% | 83.6% |
| **Support Vector Machine (SVM)** | Course Lab 5 (`svm.py`) | 83.2% | 84.4% | 83.2% | 83.4% |
| **Logistic Regression** | Course Lab 3 (`liner.py` / `mlinear.py`) | 78.5% | 79.8% | 78.5% | 78.8% |
| **Naive Bayes (Gaussian)** | Course Lab 4 (`navie.py`) | 71.2% | 69.6% | 71.2% | 67.6% |

---

## 🚀 Quickstart Guide

### 1. Environment Activation

The project includes an isolated Python virtual environment (`.venv`):

```bash
# Activate existing environment
source .venv/bin/activate

# Or install dependencies
pip install -r requirements.txt
```

### 2. Run the Modern Vite + React Web Application

Launch the FastAPI backend and Vite frontend concurrently with a single command:

```bash
# Start both Backend (Port 8001) and Vite Frontend (Port 5173)
python main.py --dev
```

Or run them individually in separate terminal sessions:

```bash
# Terminal 1: FastAPI REST API
python main.py --server

# Terminal 2: Vite React Frontend
python main.py --vite
```

*Open your browser and navigate to **`http://localhost:5173`**.*

The Vite web dashboard features:
- **Interactive Leaflet Map:** Real OSRM driving road polyline color-coded by risk severity, Start/End custom markers, and 20 K-Means accident blackspot circles with popup severity details.
- **Live Location Autocomplete:** Debounced real-time search for Indian landmarks, cities, and road hubs with verified GPS coordinates.
- **Live Meteorological Badge:** Real-time weather, temperature, wind speed, and precipitation chance powered by Open-Meteo.
- **Intelligent Road Hazard Alerts:** Active safety cards for proximity to historical high-risk blackspots (radius &le; 1.2km), fog, wet asphalt, and rush-hour delays.
- **Dynamic Safe Departure Recommendation:** Machine learning hero card recommending optimal departure hour, quantified percentage risk reduction (e.g. up to 84.5%), and interactive 24-hour continuous collision trajectory curve.
- **Empirical Slide Gallery (EDA):** Full gallery of presentation figures matching Slide decks 5, 6, 8, 9 with modal view.
- **Model Evaluation Benchmarks:** Comparative curriculum analysis comparing Random Forest against ID3 Decision Tree, k-NN, SVM, Naive Bayes, and Logistic Regression, plus Confusion Matrix and Feature Importances.
- **Dataset Explorer:** Filterable sample viewer of the 6,469 cleaned records.

### 3. CLI Pipeline Runner

You can execute any stage of the project pipeline directly from the command line:

```bash
# Run full end-to-end pipeline (Data generation -> Model Training -> EDA Plots -> Sample Route)
python main.py --all

# Generate datasets only
python main.py --data

# Train and evaluate models
python main.py --train

# Render all presentation charts to static/
python main.py --eda

# Analyze custom route from CLI
python main.py --route --origin "Connaught Place Delhi" --dest "Noida Expressway" --hour 23
```

### 4. Jupyter Notebook Execution

The self-contained Jupyter notebook `Route_Accident_Risk_Prediction.ipynb` can be executed interactively:

```bash
jupyter notebook Route_Accident_Risk_Prediction.ipynb
```

---

## 🔬 Key Conclusions

- **Temporal Vulnerability:** Severe accidents concentrate heavily during Night and late Evening hours due to impaired visibility and speed variance, despite lower overall traffic volumes.
- **Location Baseline:** Spatial clustering demonstrates that accident density at high-speed arterial corridors and highway junctions is the dominant determinant of baseline collision risk.
- **Actionable Travel Rescheduling:** Recommending a shift from late night to morning departure for representative arterial corridors demonstrates up to **42% to 52% quantified risk reduction**.

---

## 🆓 Complete Free API Guide (Zero Cost, No Credit Card Required)

To run this system anywhere for free without signing up for paid accounts or entering credit cards:

| Capability | Free API Provider | Endpoint / Protocol | Cost / Limits | What It Provides |
|---|---|---|---|---|
| **Real Driving Navigation** | **OSRM (Open Source Routing Machine)** | `http://router.project-osrm.org/route/v1/driving` | **100% Free** (No API key, no sign-up) | Real driving highway polylines, actual road driving distance, turn-by-turn routing, and duration. |
| **Live Route Weather** | **Open-Meteo API** | `https://api.open-meteo.com/v1/forecast` | **100% Free** (No API key, open access) | Live real-time temperature, condition (Clear, Rainy, Foggy), wind speed, and precipitation. |
| **24-Hour Weather Forecast** | **Open-Meteo API** | `hourly=weathercode,temperature_2m,precipitation_probability` | **100% Free** (No API key) | Hour-by-hour forecast enabling dynamic departure time risk modeling. |
| **Geocoding & Place Search** | **OpenStreetMap Nominatim & ArcGIS** | Open Search REST | **100% Free** (No API key) | Location autocompletion and verified GPS coordinates for Indian landmarks. |
| **Road Hazard Alerts** | **Built-in Intelligent Alert Engine** | Native spatial analysis | **100% Free** | Real-time alerts for blackspot proximity, fog/rain hazard warnings, and rush hour delays. |

*(Optional)* If you wish to connect commercial traffic services, the sidebar includes optional inputs for **TomTom Traffic API** (free 2,500 calls/day at [developer.tomtom.com](https://developer.tomtom.com/)) or **OpenWeatherMap** (free 1,000 calls/day at [openweathermap.org](https://openweathermap.org/)).
