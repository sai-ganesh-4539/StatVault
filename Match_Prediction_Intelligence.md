# ⚽ STATVAULT MATCH PREDICTION INTELLIGENCE CENTER

<div align="center">

# 🧠 Enterprise Football Forecasting Platform

<img src="https://img.shields.io/badge/XGBoost-v2.0-success?style=for-the-badge" />
<img src="https://img.shields.io/badge/Dataset-230K%2B_Matches-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/Features-18-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/Accuracy-46.95%25-yellow?style=for-the-badge" />
<img src="https://img.shields.io/badge/ROC--AUC-0.6461-brightgreen?style=for-the-badge" />
<img src="https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge" />

<br><br>

## 🚀 AI-Powered Match Outcome Prediction Engine

### Predicting Home Wins • Draws • Away Wins from 230K+ Historical Matches

---

</div>

# 🎯 EXECUTIVE OVERVIEW

<table>
<tr>
<td width="33%">

### 📦 Dataset

| Metric | Value |
|---------|--------|
| Matches | 230,554 |
| Features | 18 |
| Columns | 49 |
| Memory | 182 MB |

</td>

<td width="33%">

### 🧠 Model

| Metric | Value |
|---------|--------|
| Algorithm | XGBoost |
| Version | 2.0 |
| Classes | 3 |
| Split | Chronological |

</td>

<td width="33%">

### 🎯 Performance

| Metric | Value |
|---------|--------|
| Accuracy | 46.95% |
| ROC-AUC | 0.6461 |
| Top-2 Accuracy | 75.51% |
| Log Loss | 1.0338 |

</td>
</tr>
</table>

---

# 🌍 SYSTEM ARCHITECTURE

```mermaid
flowchart LR

A["⚽ 230,554 Historical Matches"]

A --> B["🛡️ Data Quality Engine"]

B --> C["⚙️ Feature Engineering"]

C --> D["📊 18 Production Features"]

D --> E["🧠 XGBoost Classifier"]

E --> F["🎲 Probability Engine"]

F --> G["🏠 Home Win"]
F --> H["🤝 Draw"]
F --> I["✈️ Away Win"]

G --> J["🎯 Confidence Layer"]
H --> J
I --> J

J --> K["🚀 Production Predictions"]
```

---

# 📦 DATA SPLIT STRATEGY

```mermaid
pie title Chronological Dataset Distribution

"Training 184,443" : 184443
"Validation 23,055" : 23055
"Testing 23,056" : 23056
```

---

# 🚀 PERFORMANCE COMMAND CENTER

| Metric | Score |
|----------|----------|
| Accuracy | **46.95%** |
| Balanced Accuracy | **45.44%** |
| Macro Precision | **45.35%** |
| Macro Recall | **45.44%** |
| Macro F1 | **45.26%** |
| Weighted F1 | **47.31%** |
| ROC-AUC (OVR) | **64.61%** |
| Top-2 Accuracy | **75.51%** |
| Calibration Error | **3.12%** |
| Mean Confidence | **46.79%** |

---

# 📊 PERFORMANCE VISUALIZATION

## Accuracy

```text
███████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 46.95%
```

## Balanced Accuracy

```text
██████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 45.44%
```

## ROC AUC

```text
████████████████████████████████░░░░░░░░░░░░░░░░░░░ 64.61%
```

## Top-2 Accuracy

```text
██████████████████████████████████████░░░░░░░░░░░░░ 75.51%
```

---

# 🏆 FEATURE IMPORTANCE LEADERBOARD

```mermaid
graph LR

A["🧠 Prediction Engine"]

A --> B["oddhome<br>20.85%"]
A --> C["oddaway<br>20.51%"]

A --> D["maxaway<br>3.82%"]
A --> E["odddraw<br>3.34%"]
A --> F["maxhome<br>3.27%"]

A --> G["awayelo"]
A --> H["homeelo"]

A --> I["form3home"]
A --> J["form5home"]

A --> K["form3away"]
A --> L["form5away"]
```

---

# 🎯 FEATURE POWER DISTRIBUTION

```mermaid
xychart-beta
title "Top Feature Importance"

x-axis [oddhome, oddaway, maxaway, odddraw, maxhome]

y-axis "Gain" 0 --> 25

bar [20.85, 20.51, 3.82, 3.34, 3.27]
```

---

# 🧠 CLASSIFICATION REPORT

| Outcome | Precision | Recall | F1 Score |
|----------|----------|----------|----------|
| 🏠 Home | 0.60 | 0.53 | 0.56 |
| 🤝 Draw | 0.30 | 0.32 | 0.31 |
| ✈️ Away | 0.46 | 0.51 | 0.48 |

---

# 🎯 CLASS PREDICTION STRENGTH

```mermaid
quadrantChart
title Outcome Prediction Landscape

x-axis Low Recall --> High Recall
y-axis Low Precision --> High Precision

quadrant-1 Elite
quadrant-2 Accurate
quadrant-3 Weak
quadrant-4 Balanced

Home:[0.53,0.60]
Draw:[0.32,0.30]
Away:[0.51,0.46]
```

---

# 🔥 CONFUSION MATRIX ANALYSIS

## Actual Home Matches

```text
Correct Home Predictions      ████████████████████  5,351

Predicted Draw                ██████████           2,663

Predicted Away                ████████             2,133
```

## Actual Draw Matches

```text
Predicted Home                ███████              2,025

Correct Draw Predictions      ███████              1,958

Predicted Away                ███████              2,043
```

## Actual Away Matches

```text
Predicted Home                ██████               1,557

Predicted Draw                ███████              1,810

Correct Away Predictions      ██████████████       3,516
```

---

# 📊 NORMALIZED CONFUSION MATRIX

| Actual ↓ / Predicted → | Home | Draw | Away |
|----------|----------|----------|----------|
| 🏠 Home | **53%** | 26% | 21% |
| 🤝 Draw | 34% | **32%** | 34% |
| ✈️ Away | 23% | 26% | **51%** |

---

# 🌊 PREDICTION FLOW MAP

```mermaid
sankey-beta

Home Matches,Correct Home Predictions,5351
Home Matches,Predicted Draw,2663
Home Matches,Predicted Away,2133

Draw Matches,Predicted Home,2025
Draw Matches,Correct Draw Predictions,1958
Draw Matches,Predicted Away,2043

Away Matches,Predicted Home,1557
Away Matches,Predicted Draw,1810
Away Matches,Correct Away Predictions,3516
```

---

# 🛡️ DATA QUALITY COMMAND CENTER

```mermaid
mindmap
  root((🛡️ Data Quality))

    Dataset
      230557 Rows
      49 Columns
      182 MB

    Missing Values
      HomeELO 38.58%
      AwayELO 38.61%

      HomeShots 50.24%
      AwayShots 50.23%

      HomeTarget 50.59%
      AwayTarget 50.58%

    Integrity
      Duplicate Rows 0

    Constants
      source_dataset
```

---

# 🚨 LEAKAGE PROTECTION WALL

```mermaid
flowchart TD

A["🚨 Potential Leakage Sources"]

A --> B["fthome"]
A --> C["ftaway"]
A --> D["ftresult"]

A --> E["Match Statistics"]

E --> F["Shots"]
E --> G["Corners"]
E --> H["Cards"]

B --> I["❌ Removed"]
C --> I
D --> I
F --> I
G --> I
H --> I

I --> J["✅ Clean Feature Space"]
```

---

# 📉 FEATURE DRIFT MONITOR

```mermaid
pie title Feature Stability Analysis

"Stable Features (4)" : 4

"Drifted Features (8)" : 8
```

---

# 🎯 MODEL CONFIDENCE ENGINE

## Mean Prediction Confidence

```text
███████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 46.79%
```

## Confidence Variability

```text
█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 11.40%
```

## Calibration Error

```text
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 3.12%
```

---

# ⚠️ KNOWN LIMITATIONS

```mermaid
mindmap
  root((⚠️ Model Limits))

    Prediction
      Pre Match Only
      No Live Events

    Football
      Injuries
      Transfers
      Manager Changes
      Red Cards

    Data
      Drift
      Imbalance

    External
      League Evolution
      Tactical Changes
      Upsets
```

---

# 🚀 PRODUCTION READINESS MATRIX

```mermaid
journey

title Production Deployment Readiness

section Data

Quality Validation: 5
Leakage Detection: 5

section Features

Engineering: 5
Selection: 5

section Modeling

Training: 5
Calibration: 5

section Evaluation

Metrics: 5
Robustness: 4

section Deployment

Serving: 5
Monitoring: 5
```

---

# 🎖️ SYSTEM HEALTH DASHBOARD

| Component | Status |
|------------|------------|
| Data Quality | 🟢 Healthy |
| Leakage Validation | 🟢 Passed |
| Feature Engineering | 🟢 Stable |
| Model Training | 🟢 Completed |
| Calibration | 🟢 Good |
| Drift Monitoring | 🟡 Attention Required |
| Confidence Engine | 🟢 Active |
| Production Readiness | 🟢 Ready |

---

# 🏁 FINAL EXECUTIVE SUMMARY

```text
╔══════════════════════════════════════════════════════════════╗
║                    STATVAULT MATCH AI                       ║
╠══════════════════════════════════════════════════════════════╣
║ DATASET SIZE             : 230,554 Matches                  ║
║ FEATURES                 : 18                               ║
║ MODEL                    : XGBoost v2.0                    ║
║ ACCURACY                 : 46.95%                           ║
║ BALANCED ACCURACY        : 45.44%                           ║
║ MACRO F1                : 45.26%                           ║
║ ROC-AUC                 : 0.6461                           ║
║ TOP-2 ACCURACY          : 75.51%                           ║
║ LOG LOSS                : 1.0338                           ║
║ MEAN CONFIDENCE         : 46.79%                           ║
║ CALIBRATION ERROR       : 3.12%                            ║
║ FEATURE DRIFT           : 8 / 12 FEATURES                  ║
║ LEAKAGE CHECK           : PASSED                           ║
║ DEPLOYMENT STATUS       : READY                            ║
╚══════════════════════════════════════════════════════════════╝
```

---

<div align="center">

# 🚀 STATVAULT v2.0

### Enterprise Football Intelligence Platform

**Predict • Analyze • Optimize • Win**

---

Built with XGBoost • 230K+ Matches • Production Ready

</div>
