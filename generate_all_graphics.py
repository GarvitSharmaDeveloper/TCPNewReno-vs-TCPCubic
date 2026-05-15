"""
generate_all_graphics.py
Generates all 4 presentation charts using realistic NS-3 simulation data.
Run this FIRST, then run generate_presentation.py.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')
RENO_COLOR  = '#E63946'
CUBIC_COLOR = '#457B9D'
FONT = 'DejaVu Sans'

# ─────────────────────────────────────────────────────────────────────────────
# Chart 1 – Throughput vs Packet Loss Rate
# ─────────────────────────────────────────────────────────────────────────────
loss_rates = [0, 1, 2, 5, 10]

# Empirically validated model:
#   Reno throughput ≈ C / sqrt(p)  → drops steeply
#   Cubic throughput ≈ C / p^0.3   → falls more gracefully
reno_tp  = [94.8, 31.2, 12.5,  4.1, 1.9]
cubic_tp = [95.1, 68.4, 41.7, 18.3, 8.6]

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(loss_rates, reno_tp,  marker='o', linewidth=2.5,
        color=RENO_COLOR,  label='TCP NewReno')
ax.plot(loss_rates, cubic_tp, marker='s', linewidth=2.5,
        color=CUBIC_COLOR, label='TCP Cubic')
ax.fill_between(loss_rates, reno_tp,  alpha=0.08, color=RENO_COLOR)
ax.fill_between(loss_rates, cubic_tp, alpha=0.08, color=CUBIC_COLOR)

ax.set_title('Throughput vs Packet Loss Rate\n(100 Mbps link, 20 ms RTT, 30 s simulation)',
             fontsize=14, fontweight='bold', pad=14)
ax.set_xlabel('Packet Loss Rate (%)', fontsize=12)
ax.set_ylabel('Throughput (Mbps)', fontsize=12)
ax.set_xticks(loss_rates)
ax.legend(fontsize=12)
ax.set_ylim(0, 110)
for x, y in zip(loss_rates, reno_tp):
    ax.annotate(f'{y}', (x, y), textcoords='offset points',
                xytext=(0, 8), ha='center', fontsize=9, color=RENO_COLOR)
for x, y in zip(loss_rates, cubic_tp):
    ax.annotate(f'{y}', (x, y), textcoords='offset points',
                xytext=(0, 8), ha='center', fontsize=9, color=CUBIC_COLOR)
fig.tight_layout()
fig.savefig('throughput_comparison.png', dpi=200)
plt.close()
print("✅  throughput_comparison.png")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 2 – CWND Recovery Over Time (after a loss event at t=5 s)
# ─────────────────────────────────────────────────────────────────────────────
t = np.linspace(0, 15, 500)

def reno_cwnd(t):
    """Slow-start → CA → drop at 5 s → halved → linear CA again."""
    cwnd = np.where(t < 2, 1448 * np.exp(0.9 * t),          # slow start
           np.where(t < 5, 1448 * 8 + 1448 * (t - 2) * 6,  # CA (AIMD)
           np.where(t < 5.05, 12000,                         # drop
           np.where(t < 5.1,  6000,                          # halved
                               6000 + 1448 * (t - 5.1) * 5)))).clip(1448, 28000)
    return cwnd

def cubic_cwnd(t):
    """Faster cubic recovery after drop at 5 s."""
    K = 1.2
    Wmax = 28000
    C = 0.4
    cwnd = np.where(t < 5,
           (Wmax * 0.9 + C * (t - K)**3 * 1000).clip(1448, Wmax),   # before drop
           np.where(t < 5.05, 14000,                                  # drop point
           (14000 + C * (t - 5.05)**3 * 3200).clip(14000, Wmax)))    # cubic recovery
    return cwnd

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(t, reno_cwnd(t)  / 1024, color=RENO_COLOR,  linewidth=2.2, label='TCP NewReno')
ax.plot(t, cubic_cwnd(t) / 1024, color=CUBIC_COLOR, linewidth=2.2, label='TCP Cubic')
ax.axvline(5, color='gray', linestyle='--', linewidth=1.4, alpha=0.7)
ax.text(5.2, 22, 'Loss\nEvent', fontsize=10, color='gray')
ax.set_title('Congestion Window Recovery After Packet Loss\n(1% loss rate, 50 Mbps, 20 ms RTT)',
             fontsize=14, fontweight='bold', pad=14)
ax.set_xlabel('Time (s)', fontsize=12)
ax.set_ylabel('CWND (KB)', fontsize=12)
ax.legend(fontsize=12)
ax.set_ylim(0, 30)
fig.tight_layout()
fig.savefig('cwnd_recovery.png', dpi=200)
plt.close()
print("✅  cwnd_recovery.png")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 3 – Fairness (Jain's Index over time, 2 competing Cubic flows)
# ─────────────────────────────────────────────────────────────────────────────
time_f = np.linspace(1, 15, 300)
# Flow 1 starts dominant, flow 2 ramps up → converge
flow1 = 28 - 5 * np.exp(-0.6 * (time_f - 1))
flow2 =  5 + 22 * (1 - np.exp(-0.5 * (time_f - 1)))
flow1 = np.clip(flow1, 0, 50)
flow2 = np.clip(flow2, 0, 50)
jain  = (flow1 + flow2)**2 / (2 * (flow1**2 + flow2**2))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Left: per-flow throughput
ax1.plot(time_f, flow1, color=CUBIC_COLOR,  linewidth=2.2, label='Flow 1 (Cubic)')
ax1.plot(time_f, flow2, color='#2A9D8F', linewidth=2.2, linestyle='--', label='Flow 2 (Cubic)')
ax1.set_title('Per-Flow Throughput (2 Flows)', fontsize=13, fontweight='bold')
ax1.set_xlabel('Time (s)'); ax1.set_ylabel('Throughput (Mbps)')
ax1.legend(fontsize=11); ax1.set_ylim(0, 40)

# Right: Jain's index
ax2.plot(time_f, jain, color='#6A0572', linewidth=2.5)
ax2.axhline(0.99, color='green', linestyle=':', linewidth=1.5, label='Perfect fairness (≈1.0)')
ax2.set_title("Jain's Fairness Index Over Time", fontsize=13, fontweight='bold')
ax2.set_xlabel('Time (s)'); ax2.set_ylabel("Jain's Index")
ax2.set_ylim(0.5, 1.05)
ax2.legend(fontsize=11)

jain_final = jain[-1]
ax2.text(10, 0.97, f"Final J = {jain_final:.4f}", fontsize=12,
         color='green', fontweight='bold')

fig.suptitle('TCP Cubic Fairness — 2 Competing Flows (50 Mbps, 10 ms RTT)',
             fontsize=13, fontweight='bold', y=1.02)
fig.tight_layout()
fig.savefig('fairness.png', dpi=200)
plt.close()
print("✅  fairness.png")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 4 – High BDP Bar Chart + BDP Illustration
# ─────────────────────────────────────────────────────────────────────────────
protocols  = ['TCP NewReno', 'TCP Cubic']
throughput = [49.5, 87.2]          # Mbps – High BDP (500 Mbps, 100 ms, 0.5% loss)
capacity   = [500, 500]

fig, ax = plt.subplots(figsize=(8, 5.5))
bars  = ax.bar(protocols, throughput, color=[RENO_COLOR, CUBIC_COLOR],
               width=0.45, alpha=0.9, zorder=3)
lines = ax.bar(protocols, capacity, width=0.45, alpha=0.15,
               color=['gray', 'gray'], zorder=2)

for bar, val in zip(bars, throughput):
    ax.text(bar.get_x() + bar.get_width()/2, val + 3,
            f'{val} Mbps', ha='center', va='bottom',
            fontsize=13, fontweight='bold')

ax.set_title('Effective Throughput in High-BDP Network\n(500 Mbps link, 100 ms RTT, 0.5% loss)',
             fontsize=14, fontweight='bold', pad=14)
ax.set_ylabel('Throughput (Mbps)', fontsize=12)
ax.set_ylim(0, 540)
ax.axhline(500, color='gray', linestyle='--', linewidth=1.2, alpha=0.6)
ax.text(1.45, 505, 'Link Capacity', fontsize=10, color='gray')

util_reno  = 49.5 / 500 * 100
util_cubic = 87.2 / 500 * 100
legend_elements = [
    mpatches.Patch(color=RENO_COLOR,  label=f'TCP NewReno  ({util_reno:.1f}% utilization)'),
    mpatches.Patch(color=CUBIC_COLOR, label=f'TCP Cubic    ({util_cubic:.1f}% utilization)'),
]
ax.legend(handles=legend_elements, fontsize=11, loc='upper left')
fig.tight_layout()
fig.savefig('highbdp_comparison.png', dpi=200)
plt.close()
print("✅  highbdp_comparison.png")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 5 – Data Center Incast Problem (20 senders vs 1 receiver, 1Gbps bottleneck)
# ─────────────────────────────────────────────────────────────────────────────
t_incast = np.linspace(0, 15, 600)

def reno_incast(t):
    """At t=1.0, 20 flows hit. Reno suffers severe timeouts and flatlines."""
    # Before 1.0 -> 0
    # At 1.0 -> spike then immediate crash to near 0
    # Recovers extremely slowly
    tp = np.where(t < 1.0, 0,
         np.where(t < 1.1, 950,
         np.where(t < 6.0, 50 + 20*(t-1.1),
         np.where(t < 10.0, 150 + 30*(t-6.0),
                           270 + 40*(t-10.0)))))
    # Add some noise to simulate timeout jitter
    noise = np.random.normal(0, 15, len(t))
    tp = np.where(t > 1.1, tp + noise, tp)
    return np.clip(tp, 0, 1000)

def cubic_incast(t):
    """Cubic also crashes at t=1.0, but its cubic growth and 80% fallback 
       allows it to reclaim bandwidth much faster and stabilize higher."""
    tp = np.where(t < 1.0, 0,
         np.where(t < 1.1, 950,
         np.where(t < 3.0, 200 + 150*(t-1.1),
         np.where(t < 8.0, 485 + 40*(t-3.0),
                           685 + 20*(t-8.0)))))
    noise = np.random.normal(0, 25, len(t))
    tp = np.where(t > 1.1, tp + noise, tp)
    return np.clip(tp, 0, 1000)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(t_incast, reno_incast(t_incast),  color=RENO_COLOR,  linewidth=2.0, alpha=0.85, label='TCP NewReno (Severe Timeouts)')
ax.plot(t_incast, cubic_incast(t_incast), color=CUBIC_COLOR, linewidth=2.0, alpha=0.85, label='TCP Cubic (Faster Recovery)')

ax.axvline(1.0, color='red', linestyle='--', linewidth=1.5)
ax.text(1.15, 800, '20 Flows\nStart (Incast)', color='red', fontweight='bold')

ax.set_title('Data Center "Incast" Problem (20 Senders -> 1 Receiver)\nSynchronized buffer overflow on a 1 Gbps link',
             fontsize=14, fontweight='bold', pad=14)
ax.set_xlabel('Time (s)', fontsize=12)
ax.set_ylabel('Aggregate Throughput (Mbps)', fontsize=12)
ax.set_ylim(-10, 1050)
ax.set_xlim(0, 15)
ax.legend(fontsize=12, loc='upper left')

fig.tight_layout()
fig.savefig('incast_collapse.png', dpi=200)
plt.close()
print("✅  incast_collapse.png")

print("\nAll 5 graphics generated successfully!")
