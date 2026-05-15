# 📡 Performance Benchmarking of TCP Reno vs. TCP Cubic

> **CS258 — Computer Networks Final Project**  
> **Team:** Garvit Sharma & Yukta Vajpayee  
> **Instructor:** Prof. Navrati Saxena  
> **Simulator:** NS-3 v3.35

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Core Innovation](#-core-innovation-data-center-incast)
3. [Hypotheses](#-hypotheses)
4. [Project Structure](#-project-structure)
5. [Prerequisites](#-prerequisites)
6. [How to Run](#-how-to-run)
7. [Experiments](#-experiments)
8. [Results Summary](#-results-summary)
9. [Documentation Files](#-documentation-files)

---

## 🔬 Project Overview

This project empirically benchmarks two of the most widely deployed TCP congestion control algorithms:

- **TCP NewReno** — The classical AIMD algorithm (RFC 5681). On every packet loss, it cuts its Congestion Window by exactly **50%** and recovers linearly.
- **TCP Cubic** — The modern standard (RFC 9438, 2023), used by default on Linux, macOS, and Android. On packet loss, it cuts its window by only **30%** and recovers using an aggressive **cubic polynomial curve** `W(t) = C(t-K)³ + Wmax`.

We ran **five distinct NS-3 simulations** across two different network topologies to quantify the performance difference across realistic network scenarios.

---

## 🚀 Core Innovation: Data Center Incast

Beyond standard benchmarks, our key contribution is modeling the **Data Center Incast Problem** using a **Many-to-1 Star Topology**:

```
Sender 1  ─┐
Sender 2  ─┤
Sender 3  ─┤
   ...      ├──► Router (DropTail, 100p cap) ──► Receiver
Sender 19 ─┤         ▲
Sender 20 ─┘   1 Gbps Bottleneck
                (20 Gbps aggregate demand)
```

When all 20 senders burst simultaneously at `t=1.0s`, the router buffer overflows catastrophically — this is the Incast collapse. We measure which algorithm recovers faster.

---

## 📐 Hypotheses

| ID | Hypothesis |
|----|-----------|
| **H1** | Cubic achieves higher throughput than Reno under random packet loss |
| **H2** | Cubic recovers its CWND ~2× faster after a loss event |
| **H3** | Two competing Cubic flows share bandwidth fairly (Jain's Index ≈ 1.0) |
| **H4** | Cubic exploits High-BDP links more efficiently than Reno |
| **H5** | Cubic recovers faster from synchronized Data Center Incast crashes |

---

## 📁 Project Structure

```
computernetworks_research/
│
├── 📂 ns-allinone-3.35/ns-3.35/    # NS-3 simulator (pre-built)
│
├── 🔧 SIMULATION SCRIPTS
│   ├── simulation.py               # Core NS-3 engine (P2P + Star topology)
│   ├── run_experiments.py          # Orchestrator — runs all 5 experiments
│   ├── generate_all_graphics.py    # Generates all result charts (PNG)
│   ├── generate_presentation.py    # Auto-builds PowerPoint deck
│   └── generate_topology_diagram.py # Draws the Star Topology diagram
│
├── 📊 RESULTS DATA
│   ├── exp1_throughput.csv         # Throughput vs loss rate results
│   ├── exp3_fairness.csv           # Per-flow fairness data
│   ├── exp4_highbdp.csv            # High-BDP utilization results
│   └── exp5_incast.csv             # Incast aggregate throughput
│
├── 🖼️ GENERATED CHARTS (after running)
│   ├── throughput_comparison.png   # Exp 1 — Line graph
│   ├── cwnd_recovery.png           # Exp 2 — CWND over time
│   ├── fairness.png                # Exp 3 — Jain's Index
│   ├── highbdp_comparison.png      # Exp 4 — Bar chart
│   ├── incast_collapse.png         # Exp 5 — Time-series crash
│   └── network_topology.png        # Star topology diagram
│
└── 📚 DOCUMENTATION
    ├── README.md                   # This file
    ├── PROJECT_DOCUMENTATION.md    # Full technical documentation
    ├── RESULTS_EXPLAINED.md        # Plain-English results explanation
    ├── TECHNICAL_GLOSSARY.md       # All terminology explained
    ├── CODE_WALKTHROUGH.md         # How the code pipeline works
    ├── PROFESSOR_QA_CHEAT_SHEET.md # Likely viva/defense questions
    └── PRESENTER_SPEECH.md         # 10-minute timed presentation script
```

---

## ⚙️ Prerequisites

### 1. NS-3 v3.35 (with Python bindings)
NS-3 is included in the `ns-allinone-3.35/` folder and must already be built. Verify with:
```bash
ls ns-allinone-3.35/ns-3.35/build/bindings/python/ns/
# Should show: applications.cpython-*.so, core.py, etc.
```

### 2. Python Dependencies
```bash
pip install matplotlib python-docx python-pptx networkx
```

### 3. Python Version
```bash
python3 --version   # Requires Python 3.8+
```

---

## ▶️ How to Run

> ⚠️ **Important:** All NS-3 simulations MUST be run from inside the `ns-3.35` directory so the Python bindings are found correctly.

### Quick Start — Run All Experiments
```bash
cd /path/to/computernetworks_research/ns-allinone-3.35/ns-3.35
python3 ../../run_experiments.py
```

### Generate All Charts
```bash
cd /path/to/computernetworks_research
python3 generate_all_graphics.py
```

### Generate PowerPoint Presentation
```bash
python3 generate_presentation.py
```

---

## 🧪 Experiments

### Experiment 1 — Throughput vs. Packet Loss (Tests H1)
```bash
cd ns-allinone-3.35/ns-3.35

# TCP NewReno
python3 ../../simulation.py \
  --protocol TcpNewReno --bandwidth 1Gbps \
  --delay 20ms --loss_rate 0.001 --duration 60 \
  --prefix demo_reno

# TCP Cubic
python3 ../../simulation.py \
  --protocol TcpCubic --bandwidth 1Gbps \
  --delay 20ms --loss_rate 0.001 --duration 60 \
  --prefix demo_cubic
```

---

### Experiment 2 — CWND Recovery Speed (Tests H2)
```bash
python3 ../../simulation.py \
  --protocol TcpNewReno --bandwidth 1Gbps \
  --delay 20ms --loss_rate 0.001 --duration 30 \
  --prefix demo_cwnd_reno

python3 ../../simulation.py \
  --protocol TcpCubic --bandwidth 1Gbps \
  --delay 20ms --loss_rate 0.001 --duration 30 \
  --prefix demo_cwnd_cubic
```
*Generates `*_trace.tr` files for CWND reconstruction.*

---

### Experiment 3 — Fairness (Tests H3)
```bash
python3 ../../simulation.py \
  --protocol TcpCubic --bandwidth 1Gbps \
  --delay 20ms --loss_rate 0.001 --n_flows 2 \
  --duration 30 --prefix demo_fair
```
*Run with `--n_flows 2` to create two competing Cubic connections.*

---

### Experiment 4 — High-BDP Satellite Link (Tests H4)
```bash
python3 ../../simulation.py \
  --protocol TcpNewReno --bandwidth 1Gbps \
  --delay 100ms --loss_rate 0.001 --duration 60 \
  --prefix demo_bdp_reno

python3 ../../simulation.py \
  --protocol TcpCubic --bandwidth 1Gbps \
  --delay 100ms --loss_rate 0.001 --duration 60 \
  --prefix demo_bdp_cubic
```
*Key change: `--delay 100ms` simulates a satellite link.*

---

### Experiment 5 — Data Center Incast (Tests H5)
```bash
# Use reduced parameters for faster runtime (~12 seconds total)
python3 ../../simulation.py \
  --protocol TcpNewReno --bandwidth 100Mbps \
  --delay 1ms --incast --n_flows 10 --duration 5 \
  --prefix demo_incast_reno

python3 ../../simulation.py \
  --protocol TcpCubic --bandwidth 100Mbps \
  --delay 1ms --incast --n_flows 10 --duration 5 \
  --prefix demo_incast_cubic
```
*Uses `--incast` flag to activate the 22-node Star Topology.*

---

## 📊 Results Summary

| Experiment | Metric | TCP NewReno | TCP Cubic | Winner |
|---|---|---|---|---|
| 1. Throughput vs Loss | Throughput @ 0.1% loss | ~8.9 Mbps | ~9.2 Mbps | **Cubic** ✅ |
| 2. CWND Recovery | Throughput after loss | ~10.4 Mbps | ~12.0 Mbps | **Cubic** ✅ |
| 3. Fairness | Jain's Index | — | 0.999 | **Cubic** ✅ |
| 4. High-BDP | Throughput (100ms RTT) | ~2.95 Mbps | ~6.54 Mbps | **Cubic** ✅ |
| 5. Incast | Recovery speed | Slow / Flatlines | Fast recovery | **Cubic** ✅ |

> **Key Finding:** TCP Cubic is decisively superior in high-speed, high-loss, and high-delay network environments. Its β=0.7 window reduction and cubic polynomial recovery directly address the fundamental limitations of Reno's conservative AIMD strategy.

---

## 📚 Documentation Files

| File | Purpose |
|---|---|
| `PROJECT_DOCUMENTATION.md` | Full technical and architectural overview |
| `RESULTS_EXPLAINED.md` | Each experiment explained + code used |
| `TECHNICAL_GLOSSARY.md` | 25 key terms defined with project context |
| `CODE_WALKTHROUGH.md` | How the automation pipeline works end-to-end |
| `PROFESSOR_QA_CHEAT_SHEET.md` | 30+ likely viva questions with model answers |
| `PRESENTER_SPEECH.md` | Timed 10-minute presentation script |

---

## 📖 Key References

1. Ha, S., Rhee, I., & Xu, L. (2008). *CUBIC: A new TCP-friendly high-speed TCP variant.* ACM SIGOPS, 42(5), 64–74.
2. RFC 9438 — *CUBIC for Fast and Long-Distance Networks.* IETF, August 2023.
3. Vasudevan, V. et al. (2009). *Safe and effective fine-grained TCP retransmissions for datacenter communication.* ACM SIGCOMM.
4. Hock, M. et al. (2022). *Experimental evaluation of TCP Cubic.* IEEE.
5. Al-Saadi, R. et al. (2021). *A survey of delay-based and hybrid TCP congestion control algorithms.* IEEE Access.

---

*Generated as part of CS258 Final Project — May 2025*
