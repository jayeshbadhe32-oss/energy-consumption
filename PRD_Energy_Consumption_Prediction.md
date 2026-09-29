# Product Requirement Document (PRD)
## Energy Consumption Prediction Dashboard for Electricity Distribution Companies

| | |
|---|---|
| **Document Version** | 1.0 |
| **Date** | September 2026 |
| **Status** | Draft |

---

## 1. Overview

This project delivers a **zone-wise electricity consumption forecasting dashboard** built using machine learning, intended for use by electricity **distribution companies (DISCOMs)**. The tool divides a city into multiple zones/areas, analyzes historical electricity consumption for each zone, predicts future consumption, and provides actionable suggestions to support load planning and grid management decisions.

The project builds on an existing machine learning foundation (regression models for energy consumption prediction, originally developed on the "Smart Meters in London" dataset) and extends it into a city-specific, zone-based, decision-support tool.

---

## 2. Problem Statement

Distribution companies need to forecast electricity demand at a granular (area/zone) level to:
- Procure the right amount of power in advance (avoid over- or under-supply)
- Plan infrastructure upgrades in high-growth-demand zones
- Detect unusual consumption patterns early
- Respond to seasonal/weather-driven demand spikes

Currently, most public forecasting tools and academic projects operate at the **household level** or **state/national level**, with no accessible, simple tool that bridges the gap to **zone-level, actionable forecasting** for a distribution company's day-to-day planning.

---

## 3. Goals and Objectives

| Goal | Description |
|---|---|
| G1 | Predict future electricity consumption for each defined zone within a city |
| G2 | Visualize historical consumption trends per zone |
| G3 | Identify key factors (weather, day type, holidays) driving consumption in each zone |
| G4 | Generate actionable suggestions for each zone based on predicted trends |
| G5 | Present all of the above through a simple, interactive dashboard |

---

## 4. Target Users

| User | Need |
|---|---|
| **Primary: Electricity Distribution Company (DISCOM) planning/operations team** | Zone-wise demand forecasts to plan power procurement, load balancing, and infrastructure investment |
| **Secondary: Energy policy analysts** | Insight into which factors (temperature, weekday/holiday) drive consumption, to inform policy or demand-side management programs |
| **Secondary: Project stakeholders/evaluators** | A working, demonstrable proof-of-concept showing the full ML pipeline: data → model → insight → action |

---

## 5. Scope

### 5.1 In Scope
- Household-level smart meter consumption data (Bangalore, India) grouped into simulated zones
- Historical consumption visualization per zone
- Machine learning-based prediction of future consumption per zone (regression models: Linear Regression, Decision Tree, Random Forest; optionally XGBoost)
- Integration of weather data (temperature, humidity) as a predictive feature
- Integration of calendar features (day of week, holidays)
- Rule-based suggestion engine tied to prediction outputs
- Interactive dashboard (zone selector, historical vs. predicted charts, suggestions panel)

### 5.2 Out of Scope (for prototype/v1)
- Real-time/live data streaming from actual smart meters
- Integration with an actual DISCOM's billing or SCADA systems
- Individual household-level personalized recommendations
- Mobile application
- Multi-city support (v1 focuses on one city: Bangalore)

---

## 6. Data Requirements

| Data Type | Source | Notes |
|---|---|---|
| Household electricity consumption | "Smart Energy Meters in Bangalore India" (Kaggle) | To be grouped into zones by household ID clustering (simulated zoning, since true geographic zone data is not publicly available) |
| Weather data (temperature, humidity) | Open-Meteo API or equivalent, for Bangalore | To be merged by date/timestamp |
| Calendar data (holidays, weekends) | Indian national + Karnataka state holiday list | To be merged by date |

**Known limitation:** True DISCOM zone/substation-level data is not publicly available due to privacy and commercial confidentiality. Zones will be **simulated** by grouping households (e.g., N households per zone), which is a standard and academically valid approach for prototype-stage projects.

---

## 7. Functional Requirements

| ID | Requirement |
|---|---|
| FR1 | System shall group households into a configurable number of zones |
| FR2 | System shall calculate aggregate (sum/average) consumption per zone per time period |
| FR3 | System shall display historical consumption trend for a selected zone |
| FR4 | System shall predict future consumption for a selected zone using a trained regression model |
| FR5 | System shall display model accuracy metrics (R², RMSE, MAE) per zone or overall |
| FR6 | System shall display which features (temperature, day type, holiday) most influence consumption |
| FR7 | System shall generate a suggestion (e.g., "prepare for peak load," "consumption trending down") based on the prediction output |
| FR8 | Dashboard shall allow the user to select a zone and view all of the above in one view |

---

## 8. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR1 | Dashboard should load and respond within a few seconds for a given zone selection |
| NFR2 | Code and pipeline should be modular (data prep, model training, dashboard as separate components) |
| NFR3 | Dashboard should be usable without ML background (simple UI, plain-language suggestions) |
| NFR4 | Solution should be reproducible — anyone should be able to re-run the pipeline on the same dataset |

---

## 9. Proposed Tech Stack

| Layer | Tool |
|---|---|
| Data processing | Python, Pandas, NumPy |
| Modeling | Scikit-learn (Linear Regression, Decision Tree, Random Forest); optionally XGBoost |
| Model serving | FastAPI (Python REST API layer) |
| Backend server | FastAPI + Uvicorn |
| Frontend | React (with a charting library such as Recharts or Chart.js) |
| Weather data | Open-Meteo API |
| Model storage | Pickle/Joblib serialized model files, loaded by the backend at startup |

---

## 9A. System Architecture

The system is split into three independent layers, communicating over REST APIs:

```
[React Frontend]  <--- REST API (JSON) --->  [FastAPI Backend]  <--- reads --->  [Trained Models + Processed Data]
```

### 9A.1 Frontend (React)
Responsible only for presentation and user interaction; holds no business logic or ML code.
- Zone selector component
- Historical consumption chart (fetched from backend)
- Predicted consumption chart (fetched from backend)
- Feature-importance chart (fetched from backend)
- Suggestion panel (text returned by backend)
- Calls backend REST endpoints using `fetch`/`axios` and renders the returned JSON

### 9A.2 Backend (Python, FastAPI)
Responsible for all data access, ML inference, and business logic. Exposes REST endpoints consumed by the React frontend.

**Proposed API endpoints:**

| Endpoint | Method | Purpose |
|---|---|---|
| `/zones` | GET | Return list of available zones |
| `/zones/{zone_id}/history` | GET | Return historical consumption data for a zone |
| `/zones/{zone_id}/predict` | GET | Return predicted future consumption for a zone |
| `/zones/{zone_id}/features` | GET | Return feature importance / key drivers for a zone |
| `/zones/{zone_id}/suggestion` | GET | Return a rule-based suggestion derived from the prediction |

**Backend internal components:**
- Data pipeline module (cleaning, zone grouping, weather/holiday merge) — runs offline to prepare data
- Model training module (offline) — trains and saves per-zone or unified models
- Inference module (runs at request time) — loads saved model, builds input features for the requested future period, returns prediction
- Suggestion engine (rule-based) — converts prediction output into a plain-language recommendation

### 9A.3 Data & Model Layer
- Cleaned, zone-aggregated dataset (CSV/Parquet)
- Serialized trained models (one per zone or one unified model with zone as a feature)
- Weather and holiday reference data used at inference time to build future-date inputs

### 9A.4 Why this split
- React gives a more polished, production-like UI compared to a Python-only dashboard
- FastAPI keeps all ML/data logic in Python (where the existing regression models already live), avoiding any need to port modeling code to another language
- The REST API boundary means frontend and backend can be developed and tested independently

---

## 10. Success Metrics

| Metric | Target (prototype stage) |
|---|---|
| Model accuracy (R²) | Reasonable fit (baseline comparison across models, no fixed threshold at prototype stage) |
| Dashboard functionality | All defined zones selectable, with working historical + predicted views |
| Suggestion relevance | Suggestions logically align with predicted trend direction |
| Demo readiness | End-to-end flow (data → prediction → dashboard) working without manual intervention |

---

## 11. Milestones (Suggested)

| Phase | Deliverable |
|---|---|
| 1 | Data collection, cleaning, and zone simulation logic |
| 2 | Weather + calendar data integration |
| 3 | Model training and evaluation (per zone) |
| 4 | Suggestion logic (rule-based) |
| 5 | Streamlit dashboard build |
| 6 | End-to-end testing and demo preparation |

---

## 12. Assumptions

- Simulated zoning (grouping households) is an acceptable substitute for true geographic zone data at the prototype stage
- Bangalore weather and holiday data is used as a proxy for all households in the dataset (exact household geolocation not required for v1)
- The dashboard is a decision-support tool for demonstration purposes, not a production system for an actual DISCOM

---

## 13. Risks

| Risk | Mitigation |
|---|---|
| Dataset may have limited number of households, making zones too small to be meaningful | Adjust number of zones based on actual household count in dataset |
| Simulated zones do not reflect real geography | Clearly document this as a known limitation in the final report |
| Prediction accuracy may vary across zones due to inconsistent data quality | Report per-zone accuracy transparently rather than a single aggregate number |
