<!-- ================= HERO ================= -->

<div align="center">

# ⚽ StatVault AI

### Football Intelligence Platform

**Predict Match Outcomes • Scout Players • Detect Anomalies • Estimate Market Value**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python">
  <img src="https://img.shields.io/badge/XGBoost-Latest-orange">
  <img src="https://img.shields.io/badge/PostgreSQL-16-blue">
  <img src="https://img.shields.io/badge/ONNX-Ready-success">
  <img src="https://img.shields.io/badge/Status-Production-green">
</p>

</div>

---

# 🎥 Demo

<p align="center">
  <img width="100%" src="assets/demo.gif">
</p>

---

# 📊 Platform Capabilities

| Capability | Description |
|------------|-------------|
| ⚽ Match Prediction | Predict Home Win / Draw / Away Win |
| 💰 Market Value | Estimate Player Transfer Value |
| 🧠 Similarity Search | Find Players With Similar Profiles |
| 🚨 Anomaly Detection | Detect Unusual Player Performance |
| 📈 Evaluation Suite | Full Metrics & Reports |
| 🚀 ONNX Deployment | Production-Ready Exports |

---

# 🏛 Architecture

```mermaid
graph LR

A[Raw Datasets] --> B[Data Validation]
B --> C[Data Cleaning]

C --> D[Feature Engineering]

D --> E[Match Prediction]
D --> F[Market Value Prediction]
D --> G[Player Clustering]
D --> H[Anomaly Detection]

E --> I[Model Evaluation]
F --> I
G --> I
H --> I

I --> J[ONNX Export]
J --> K[Deployment]
```

---

# 🧬 End-to-End ML Lifecycle

```mermaid
journey
title StatVault ML Lifecycle

section Data
Collect Datasets: 5
Validate Data: 5
Clean Data: 5

section Features
Engineer Features: 5
Generate Training Sets: 5

section Models
Train Models: 5
Evaluate Models: 5

section Deployment
Export ONNX: 5
Deploy: 5
```

---

# 📁 Repository Structure

```text
statvault-ml
│
├── data
├── notebooks
├── models
├── reports
├── outputs
│
├── build_features.py
├── train_xgboost.py
├── train_market_value.py
├── cluster_players.py
├── detect_anomalies.py
├── evaluate_models.py
└── export_onnx.py
```

---

# ⚙ Data Pipeline

```mermaid
flowchart TB

RAW[Raw Data]
    --> CLEAN[Cleaning]
    --> FE[Feature Engineering]
    --> TRAIN[Training]
    --> EVAL[Evaluation]
    --> EXPORT[ONNX Export]
    --> PROD[Production]
```

---

# 🤖 Models

## ⚽ Match Prediction

| Property | Value |
|-----------|---------|
| Algorithm | XGBoost |
| Type | Multi-Class Classification |
| Classes | Win / Draw / Loss |
| Target Accuracy | > 60% |

---

## 💰 Market Value Prediction

| Property | Value |
|-----------|---------|
| Algorithm | XGBoost Regressor |
| Target | Market Value (€) |
| Metric | R² Score |

---

## 🧠 Player Clustering

| Property | Value |
|-----------|---------|
| Algorithm | K-Means |
| Output | Player Archetypes |

---

## 🚨 Anomaly Detection

| Property | Value |
|-----------|---------|
| Algorithm | Isolation Forest |
| Output | Anomaly Score |

---

# 📈 Example Dashboard

<div align="center">
  <img width="90%" src="assets/dashboard.png">
</div>

---

# 🎯 KPI Targets

| Metric | Target |
|---------|---------|
| Match Accuracy | > 60% |
| Market Value R² | > 0.80 |
| Silhouette Score | > 0.50 |
| Anomaly Precision | > 75% |
| Inference Time | < 100 ms |

---

# 🚀 Quick Start

```bash
git clone repo-url

cd statvault-ml

pip install -r requirements.txt

python build_features.py
python train_xgboost.py
python evaluate_models.py
```

---

# 🗺 Roadmap

- [x] Dataset Collection
- [x] Exploratory Data Analysis (EDA)
- [x] Feature Engineering
- [ ] Match Prediction
- [ ] Market Value Prediction
- [ ] Player Clustering
- [ ] Anomaly Detection
- [ ] ONNX Export
- [ ] Deployment

---

# 📜 License

MIT License

---

<div align="center">

### Built for Football Intelligence

⚽ Data → Features → Models → Insights

</div>
