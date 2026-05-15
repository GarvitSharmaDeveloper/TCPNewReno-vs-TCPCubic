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
5. [Installing NS-3](#-installing-ns-3-v335)
6. [Prerequisites](#-prerequisites)
7. [How to Run](#-how-to-run)
8. [Experiments](#-experiments)
9. [Results Summary](#-results-summary)

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
├── 📂 ns-allinone-3.35/ns-3.35/    # NS-3 simulator (must be built locally)
│
├── 🔧 SIMULATION SCRIPTS
│   ├── simulation.py               # Core NS-3 engine (P2P + Star topology)
│   ├── run_experiments.py          # Orchestrator — runs all 5 experiments
│   ├── generate_all_graphics.py    # Generates all result charts (PNG)
│   ├── generate_topology_diagram.py # Draws the Star Topology diagram
│   └── plot_results.py             # Extra plotting utilities
│
├── 📊 RESULTS DATA
│   ├── exp1_throughput.csv         # Throughput vs loss rate results
│   ├── exp3_fairness.csv           # Per-flow fairness data
│   ├── exp4_highbdp.csv            # High-BDP utilization results
│   └── exp5_incast.csv             # Incast aggregate throughput
│
├── 🖼️ GENERATED CHARTS
│   ├── throughput_comparison.png   # Exp 1 — Line graph
│   ├── cwnd_recovery.png           # Exp 2 — CWND over time
│   ├── fairness.png                # Exp 3 — Jain's Index
│   ├── highbdp_comparison.png      # Exp 4 — Bar chart
│   ├── incast_collapse.png         # Exp 5 — Time-series crash
│   ├── network_topology.png        # Star topology diagram
│   ├── project_flow_diagram.png    # Pipeline diagram
│   └── data_flow_diagram.png       # DFD diagram
│
└── README.md                       # This file
```

---

## 🛠️ Installing NS-3 v3.35

> This project uses **NS-3 version 3.35** with Python bindings. Follow the steps below to install it from scratch if you do not already have it built.

### Step 1 — Install System Dependencies

#### Ubuntu / Debian / WSL
```bash
sudo apt update && sudo apt install -y \
  gcc g++ python3 python3-dev python3-pip \
  cmake ninja-build git \
  libgsl-dev libsqlite3-dev \
  qt5-qmake qtbase5-dev \
  tcpdump wireshark-dev \
  mercurial cvs bzr \
  gdb valgrind \
  libxml2 libxml2-dev \
  libgtk-3-dev \
  python3-pygraphviz python3-gi python3-gi-cairo \
  gir1.2-gtk-3.0
```

#### macOS (via Homebrew)
```bash
brew install gcc cmake ninja gsl sqlite3 libxml2
brew install python@3.10
```

---

### Step 2 — Download NS-3 v3.35

Download the official all-in-one package from the NS-3 website:
```bash
wget https://www.nsnam.org/releases/ns-allinone-3.35.tar.bz2
tar -xjf ns-allinone-3.35.tar.bz2
cd ns-allinone-3.35
```

Or clone directly from the GitLab mirror:
```bash
git clone https://gitlab.com/nsnam/ns-3-allinone.git ns-allinone-3.35
cd ns-allinone-3.35
git checkout -b ns-3.35 ns-3.35
```

---

### Step 3 — Build NS-3 with Python Bindings

Run the all-in-one build script, which automatically builds NS-3 and its Python bindings:
```bash
cd ns-allinone-3.35
./build.py --enable-examples --enable-tests 2>&1 | tee build.log
```

> ⏱️ **Build time:** ~10–25 minutes depending on your CPU. The `--enable-examples` flag is optional but recommended to verify the build.

Alternatively, if you prefer the CMake-based build (NS-3.36+) or want fine-grained control, use `waf` directly inside the `ns-3.35` folder:
```bash
cd ns-allinone-3.35/ns-3.35
./waf configure --enable-python-bindings --enable-examples
./waf build
```

---

### Step 4 — Enable Python Bindings

After the build, add the NS-3 Python path to your environment so Python can find the `ns` module:
```bash
# Add to your ~/.bashrc or ~/.zshrc
export PYTHONPATH=$PYTHONPATH:/path/to/ns-allinone-3.35/ns-3.35/build/bindings/python
```

Apply immediately:
```bash
source ~/.bashrc   # or: source ~/.zshrc
```

---

### Step 5 — Verify the Installation

Run a quick sanity check from inside the `ns-3.35` directory:
```bash
cd ns-allinone-3.35/ns-3.35

# Check Python bindings are loadable
python3 -c "import ns.core; print('NS-3 Python bindings OK')"

# Run the built-in test suite (optional but recommended)
./test.py -s tcp-general
```

Expected output:
```
NS-3 Python bindings OK
PASS: TestSuite tcp-general
```

Also verify the bindings folder contains compiled `.so` files:
```bash
ls build/bindings/python/ns/
# Expected: applications.cpython-*.so, core.cpython-*.so, internet.cpython-*.so ...
```

---

### 🔧 Common Installation Issues

| Issue | Fix |
|---|---|
| `No module named 'ns'` | Set `PYTHONPATH` (Step 4) and re-run from inside `ns-3.35/` |
| `waf: command not found` | Use `./waf` (note the `./`) |
| Build fails on macOS with `clang` | Install `gcc` via Homebrew and set `CC=gcc-12 CXX=g++-12 ./waf configure` |
| `libgsl not found` | Run `sudo apt install libgsl-dev` or `brew install gsl` |
| `python3-dev not found` | Run `sudo apt install python3.X-dev` matching your Python version |
| Slow build | Use `./waf build -j$(nproc)` to parallelize across all CPU cores |

---

## ⚙️ Prerequisites

### 1. NS-3 v3.35 (with Python bindings)
NS-3 must be built (see [Installing NS-3](#-installing-ns-3-v335) above). Verify with:
```bash
ls ns-allinone-3.35/ns-3.35/build/bindings/python/ns/
# Should show: applications.cpython-*.so, core.py, etc.
```

### 2. Python Dependencies
```bash
pip install matplotlib networkx
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

---

## 📖 Key References

1. Ha, S., Rhee, I., & Xu, L. (2008). *CUBIC: A new TCP-friendly high-speed TCP variant.* ACM SIGOPS, 42(5), 64–74.
2. RFC 9438 — *CUBIC for Fast and Long-Distance Networks.* IETF, August 2023.
3. Vasudevan, V. et al. (2009). *Safe and effective fine-grained TCP retransmissions for datacenter communication.* ACM SIGCOMM.
4. Hock, M. et al. (2022). *Experimental evaluation of TCP Cubic.* IEEE.
5. Al-Saadi, R. et al. (2021). *A survey of delay-based and hybrid TCP congestion control algorithms.* IEEE Access.

---

*Generated as part of CS258 Final Project — May 2025*
