import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import csv

def plot_throughput_vs_loss():
    if not os.path.exists("exp1_throughput.csv"):
        print("Missing exp1_throughput.csv")
        return
        
    df = pd.read_csv("exp1_throughput.csv")
    reno = df[df['Protocol'] == 'TcpNewReno']
    cubic = df[df['Protocol'] == 'TcpCubic']
    
    plt.figure(figsize=(8, 5))
    plt.plot(reno['LossRate']*100, reno['Throughput_Mbps'], marker='o', label='TCP Reno', color='red', linestyle='--')
    plt.plot(cubic['LossRate']*100, cubic['Throughput_Mbps'], marker='s', label='TCP Cubic', color='blue', linestyle='-')
    
    plt.title("Throughput vs. Packet Loss Rate")
    plt.xlabel("Packet Loss Rate (%)")
    plt.ylabel("Throughput (Mbps)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("throughput_comparison.png", dpi=300)
    print("Saved throughput_comparison.png")

def plot_cwnd_recovery():
    plt.figure(figsize=(10, 5))
    
    for proto, color, style in [('TcpNewReno', 'red', '--'), ('TcpCubic', 'blue', '-')]:
        fname = f"out_exp2_recovery_{proto}_cwnd.csv"
        if os.path.exists(fname):
            df = pd.read_csv(fname)
            # Filter for first flow
            df = df[df['flow_id'] == 0]
            # Since NS-3 outputs cwnd at specific times, we plot it directly
            plt.plot(df['time'], df['cwnd'], label=proto, color=color, linestyle=style, alpha=0.8)
    
    plt.title("CWND Recovery Over Time (1% Packet Loss)")
    plt.xlabel("Time (s)")
    plt.ylabel("Congestion Window (Bytes)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("cwnd_recovery.png", dpi=300)
    print("Saved cwnd_recovery.png")

def plot_fairness():
    if not os.path.exists("exp3_fairness.csv"):
        print("Missing exp3_fairness.csv")
        return
        
    df = pd.read_csv("exp3_fairness.csv")
    if len(df) == 0:
        return
        
    mbps_vals = df['Throughput_Mbps'].values
    
    # Calculate Jain's Fairness Index
    sum_t = np.sum(mbps_vals)
    jain_index = (sum_t ** 2) / (len(mbps_vals) * np.sum(mbps_vals ** 2)) if sum_t > 0 else 0
    
    plt.figure(figsize=(6, 5))
    bars = plt.bar([f"Flow {i}" for i in df['Flow_ID']], mbps_vals, color=['#2ca02c', '#ff7f0e'])
    plt.title(f"TCP Cubic Fairness (2 Flows)\\nJain's Index: {jain_index:.4f}")
    plt.ylabel("Throughput (Mbps)")
    plt.grid(axis='y', alpha=0.3)
    
    # Label bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.2f}", ha='center', va='bottom')
        
    plt.tight_layout()
    plt.savefig("fairness.png", dpi=300)
    print("Saved fairness.png")

if __name__ == "__main__":
    plot_throughput_vs_loss()
    plot_cwnd_recovery()
