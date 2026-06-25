# StatVault AI – ML Data & Training Analysis Report

> Production-grade GitHub Markdown generated from uploaded reports.

## Table of Contents
- Executive Summary
- Dataset Overview
- Warehouse Architecture
- Data Pipeline
- Dataset Statistics
- Match Statistics
- Player Statistics
- Recommendations

# Executive Summary

| Dataset | Rows | Columns |
|---|---:|---:|
| fact_matches | 245,033 | 9 |
| fact_player_stats | 5,215,834 | 15 |

## Warehouse Architecture

```mermaid
flowchart LR
    A[Raw Football Data]
    B[Dimensions]
    C[Facts]
    D[Feature Engineering]
    E[ML Models]
    F[Evaluation]

    A-->B
    A-->C
    B-->D
    C-->D
    D-->E
    E-->F
```

## Star Schema

```mermaid
flowchart TB
FM[fact_matches]
FP[fact_player_stats]
DT[dim_teams]
DP[dim_players]
DC[dim_competitions]
DS[dim_seasons]
DCO[dim_countries]

DT-->FM
DC-->FM
DP-->FP
DT-->FP
DS-.->FM
DCO-.->DT
```

# Dataset Statistics

## Warehouse Summary

| Entity | Rows |
|---|---:|
| Teams | 1,206 |
| Players | 113,647 |
| Competitions | 19 |
| Countries | 216 |
| Seasons | 155 |
| Matches | 245,033 |
| Player Stats | 5,215,834 |

```text
Relative Scale

Player Stats  ████████████████████████████████████████
Matches       ██
Dimensions    █
```

# Match Statistics

Sample statistics computed from uploaded CSV.

| Metric | Value |
|---|---:|
| Sample Rows | 5,000 |
| Avg Home Goals | 0.00 |
| Avg Away Goals | 0.00 |
| Avg Total Goals | 0.00 |

```mermaid
xychart-beta
title "Average Goals"
x-axis ["Home","Away","Total"]
y-axis "Goals" 0 --> 5
bar [0.00, 0.00, 0.00]
```

# Player Statistics

| Metric | Value |
|---|---:|
| Sample Rows | 5,000 |
| Avg Minutes | 72.21 |
| Avg Goals | 0.11 |
| Avg Assists | 0.10 |

```mermaid
flowchart LR
A[Raw Match Data]
B[Cleaning]
C[Feature Engineering]
D[Training]
E[Validation]
F[Model Export]

A-->B-->C-->D-->E-->F
```

# Recommendations

- Perform full-dataset EDA before model training.
- Add feature importance, SHAP analysis, ROC curves, confusion matrices, calibration plots, and cross-validation metrics.
- Include experiment tracking and model versioning.
- Extend documentation with training logs and evaluation outputs for complete production documentation.
