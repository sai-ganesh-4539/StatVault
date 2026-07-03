
# StatVault AI — Machine Learning

> Production-ready Machine Learning subsystem powering football intelligence.

## Table of Contents
- Executive Summary
- System Architecture
- Repository Structure
- Data Warehouse
- Feature Engineering
- ML Models
- Performance
- Data Quality
- Deployment

---

# Executive Summary

| Capability | Status |
|---|---|
| Match Prediction | ✅ |
| Player Clustering | ✅ |
| Similar Player Search | ✅ |
| Anomaly Detection | ✅ |

```mermaid
flowchart LR
A[Football Data]-->B[Cleaning]
B-->C[Feature Engineering]
C-->D[XGBoost]
C-->E[KMeans]
C-->F[Cosine Similarity]
C-->G[Isolation Forest]
D-->H[API]
E-->H
F-->H
G-->H
```

# Repository Structure

```text
statvault-ai/
├── data/
│   ├── raw/
│   ├── processed/
│   └── features/
├── models/
├── reports/
├── scripts/
├── src/
│   ├── features/
│   └── models/
├── notebooks/
├── tests/
├── README.md
└── requirements.txt
```

# Data Warehouse

```mermaid
erDiagram
FACT_MATCHES }o--|| DIM_TEAMS : home
FACT_MATCHES }o--|| DIM_TEAMS : away
FACT_MATCHES }o--|| DIM_COMPETITIONS : competition
FACT_MATCHES }o--|| DIM_SEASONS : season
FACT_PLAYER_STATS }o--|| DIM_PLAYERS : player
FACT_PLAYER_STATS }o--|| DIM_TEAMS : team
```

| Dataset | Rows |
|---|---:|
| Matches | 245,033 |
| Player Stats | 5,215,834 |
| Players | 113,647 |
| Teams | 1,206 |

# Feature Engineering

### Match Features
- Team Form
- Head-to-Head
- Home Advantage
- FIFA Rank Difference
- ELO Difference
- Rolling Goals
- Rolling xG / xGA

### Player Features
- Overall Rating
- Potential
- Pace
- Shooting
- Passing
- Dribbling
- Defending
- Physical
- Age
- Height
- Preferred Foot
- Position

```mermaid
mindmap
root((Features))
  Match
    Team Form
    ELO
    xG
    H2H
  Player
    Rating
    Pace
    Passing
    Physical
```

# ML Models

| Model | Purpose |
|---|---|
| XGBoost | Match Outcome Prediction |
| KMeans | Player Archetype Discovery |
| Cosine Similarity | Similar Player Search |
| Isolation Forest | Performance Anomaly Detection |

## Match Predictor

| Accuracy | Precision | Recall | F1 | ROC-AUC |
|---:|---:|---:|---:|---:|
|0.677|0.672|0.677|0.652|0.811|

```mermaid
xychart-beta
title "Classification Metrics"
x-axis ["Acc","Prec","Recall","F1","ROC"]
y-axis 0 --> 1
bar [0.677,0.672,0.677,0.652,0.811]
```

## Player Archetypes

| Cluster |
|---|
|Poacher|
|Playmaker|
|Winger|
|Ball Winner|
|Target Man|
|Box-to-Box|

# Data Quality

| Metric | Value |
|---|---:|
|Total Records|631,321|
|Missing %|30.63|
|Duplicate Rows|116|
|Detected Anomalies|50|

```mermaid
pie
title Data Readiness
"Complete" : 69.37
"Missing" : 30.63
```

# Deployment

```mermaid
flowchart LR
Client-->FastAPI
FastAPI-->Models
Models-->Prediction
Prediction-->Dashboard
Prediction-->JSON
```



