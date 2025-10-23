<div align="center">
  <img src="https://cdn.freebiesupply.com/logos/large/2x/sharif-logo-png-transparent.png" width="150" height="150" alt="Sharif University Logo">
  <br><br>
  <h2 style="color:#0F5298;">TAGE Branch Predictor Implementation in ChampSim</h2>
  <p>
    <b>Computer Architecture Project</b><br>
    <i>Sharif University of Technology</i><br><br>
    Implementing and analyzing the <b>TAGE (TAgged GEometric)</b> branch predictor — 
    a state-of-the-art prediction algorithm used in modern CPU designs.
  </p>
  <img src="https://img.shields.io/badge/Language-C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white">
  <img src="https://img.shields.io/badge/Simulator-ChampSim-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Category-Branch%20Prediction-success?style=for-the-badge">
</div>
This project implements the TAGE (TAgged GEometric) branch predictor one of the most accurate and widely used prediction algorithms in modern processor design.  
Branch prediction plays a crucial role in improving instruction throughput and minimizing stalls caused by control-flow dependencies.  
The **TAGE predictor** achieves state-of-the-art performance by using multiple predictor tables with geometric history lengths, combined with advanced tagging and confidence mechanisms.

---

## 🚀 Project Overview

In this project, we implemented a simplified yet functional version of the **TAGE branch predictor** within the **ChampSim** simulator framework.  
Our goal was to:
- Understand the internal working of TAGE.
- Tune and test its parameters (e.g., number of tables, history lengths, tag sizes).
- Compare its prediction accuracy against other predictors.
- Analyze how configuration changes affect accuracy and performance.

The report accompanying this project describes all implementation details, design decisions, and test results.

---

Each branch predictor in **ChampSim** is organized as a separate folder inside `branch/`, containing its own `.cc` and `.h` files.  
Each predictor class inherits from the base class `branch_predictor` defined in ChampSim’s core.  
Our `tage` folder follows this exact structure.

---

## ⚙️ Implementation Details

- The main predictor logic resides in `tage.cc` and `tage.h`.
- The class `tage` implements two essential functions:
  - `predict_branch(uint64_t pc)` → returns a boolean prediction.
  - `update(branch_update_info info)` → updates internal predictor tables based on the actual outcome.
- All **hyper-parameters** (e.g., table sizes, history lengths, tag bits) are defined in `tage_config.h`, allowing easy tuning during experiments.
- For testing flexibility, we defined duplicated parameters in `tage.h` to dynamically modify them through scripts.

---

## 🧪 Testing and Evaluation

A set of shell and Python scripts were used to automate:
- Running multiple test configurations with different hyper-parameters.
- Collecting and comparing accuracy results against other predictors.
- Generating plots for accuracy and misprediction rates.

The chosen hyper-parameters were evaluated to find the most efficient configuration in terms of accuracy and hardware cost.

---

## 📊 Results Summary

TAGE achieved significantly higher prediction accuracy compared to simpler predictors such as bimodal or gshare, particularly in workloads with complex branching behavior.  
The experiments confirmed TAGE’s adaptive strength in handling long and short branch histories efficiently.

---

## 📘 References

- Seznec, A., “TAGE: A tag-based predictor with geometric history length,” *Journal of Instruction-Level Parallelism (JILP)*, 2007.
- ChampSim simulator: [https://github.com/ChampSim/ChampSim](https://github.com/ChampSim/ChampSim)

---


## 🧠 Keywords

`Branch Prediction` · `TAGE` · `ChampSim` · `Computer Architecture` · `Simulation` · `C++`

---

✨ *"Accurate branch prediction is the art of guessing the future — and TAGE does it remarkably well."*




