# 📊 STATVAULT ML — EXECUTIVE DASHBOARD

---

# 🎯 SYSTEM HEALTH

```mermaid
pie title Project Completion
    "EDA" : 100
    "Feature Engineering" : 100
    "Model Training" : 95
    "ONNX Export" : 100
    "Documentation" : 90
```

---

# 🏗️ PIPELINE ARCHITECTURE

```mermaid
flowchart LR

A[Raw Datasets] --> B[EDA Engine]

B --> C[Feature Engineering]

C --> D1[Match Features]
C --> D2[Player Features]
C --> D3[Cluster Features]
C --> D4[Anomaly Features]

D1 --> E[XGBoost Match Predictor]
D2 --> F[Market Value Model]
D3 --> G[KMeans Clustering]
D4 --> H[Isolation Forest]

E --> I[ONNX Export]
F --> I
G --> I
H --> I

I --> J[Production Deployment]
```

---

# 📦 DATA ECOSYSTEM

```mermaid
mindmap
  root((StatVault))
    Players
      FIFA22
      FIFA24
      Attributes
      Market Value

    Matches
      Elo Ratings
      Team Form
      Odds
      Statistics

    Analytics
      EDA
      Correlation
      Outliers
      Missing Values

    Models
      XGBoost
      KMeans
      Isolation Forest

    Deployment
      ONNX
      APIs
      Dashboards
```

---

# 🚀 ML MODEL LANDSCAPE

```mermaid
graph TD

A[Football Data]

A --> B[Match Prediction]
A --> C[Market Value Prediction]
A --> D[Player Clustering]
A --> E[Anomaly Detection]

B --> F[XGBoost]
C --> G[XGBoost Regressor]
D --> H[KMeans]
E --> I[Isolation Forest]

F --> J[Win / Draw / Loss]
G --> K[Player Value]
H --> L[Player Archetypes]
I --> M[Unusual Performance]
```

---

# 📈 DATA QUALITY MATRIX

| Dataset        | Records | Features | Quality                 |
| -------------- | ------- | -------- | ----------------------- |
| FIFA22 Players | 19,239  | 110      | 🟢 Excellent            |
| Matches        | 230,557 | 48       | 🟡 Moderate Missingness |
| Player Scores  | 47K+    | 26       | 🟢 Excellent            |

---

# 🔥 FEATURE IMPORTANCE PYRAMID

```text
                    Release Clause
                 ──────────────────

                      Wage EUR
                 ──────────────

                 Overall Rating
              ───────────────────

                    Potential
              ─────────────────

                   Reputation
            ─────────────────────
```

---

# ⚽ MATCH PREDICTION FLOW

```mermaid
sequenceDiagram

participant User
participant Features
participant XGBoost
participant Prediction

User->>Features: Match Data
Features->>XGBoost: Engineered Features
XGBoost->>Prediction: Probability Scores
Prediction-->>User: Home / Draw / Away
```

---

# 🧠 PLAYER SCOUTING ENGINE

```mermaid
journey
    title Player Intelligence Pipeline

    section Data Collection
      FIFA Data: 5
      Match Data: 5

    section Feature Engineering
      Performance Features: 5
      Market Features: 5

    section Machine Learning
      Clustering: 5
      Embeddings: 5

    section Insights
      Similar Players: 5
      Scouting Reports: 5
```

---

# 🏆 PROJECT STATUS

```mermaid
gitGraph
   commit id:"EDA"
   commit id:"Features"
   commit id:"Match Model"
   commit id:"Market Model"
   commit id:"Clustering"
   commit id:"Anomaly"
   commit id:"Embeddings"
   commit id:"ONNX"
   commit id:"Production Ready"
```
