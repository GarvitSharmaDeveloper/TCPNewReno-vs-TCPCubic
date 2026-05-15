import os
import subprocess
import csv
import sys

SIM_SCRIPT = "./simulation.py"
WAF_CMD = ["./waf", "--pyrun"]
NS3_DIR = "/Users/yuktavajpayee/Desktop/computernetworks_research/ns-allinone-3.35/ns-3.35"

def run_sim(prefix, protocol, loss_rate, bandwidth, delay, duration, n_flows=1, incast=False):
    # Call the simulation.py script via waf
    cmd_str = (f"../../simulation.py --prefix={prefix} --protocol={protocol} "
               f"--loss_rate={loss_rate} --bandwidth={bandwidth} --delay={delay} "
               f"--duration={duration} --n_flows={n_flows}")
    if incast:
        cmd_str += " --incast"
    cmd = WAF_CMD + [cmd_str]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=NS3_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running simulation for {protocol}:")
        print(result.stderr)
    return result.stdout

def exp_throughput_vs_loss():
    print("=== EXPERIMENT 1: Throughput vs Packet Loss ===")
    loss_rates = [0.0, 0.02, 0.05, 0.10]
    protocols = ["TcpNewReno", "TcpCubic"]
    
    with open("exp1_throughput.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Protocol", "LossRate", "Throughput_Mbps"])
        
        for p in protocols:
            for lr in loss_rates:
                prefix = f"out_exp1_{p}_{lr}"
                out = run_sim(prefix, p, lr, "100Mbps", "10ms", 10.0)
                # Parse throughput from output
                mbps = 0.0
                for line in out.split('\n'):
                    if "Total Throughput:" in line:
                        mbps = float(line.split(":")[-1].strip().split()[0])
                writer.writerow([p, lr, mbps])

def exp_recovery_time():
    print("=== EXPERIMENT 2: CWND Recovery Time ===")
    # We use a slight loss rate (e.g. 0.01) and observe the cwnd trace 
    # to see how fast it builds back up.
    # The simulation.py writes cwnd traces automatically.
    for p in ["TcpNewReno", "TcpCubic"]:
        prefix = f"out_exp2_recovery_{p}"
        run_sim(prefix, p, 0.01, "50Mbps", "20ms", 15.0)

def exp_fairness():
    print("=== EXPERIMENT 3: Fairness (Two Competing Flows) ===")
    prefix = f"out_exp3_fairness_Cubic"
    out = run_sim(prefix, "TcpCubic", 0.0, "50Mbps", "10ms", 15.0, n_flows=2)
    
    flow_mbps = []
    for line in out.split('\\n'):
        if "Throughput:" in line and "Total" not in line:
            # Extract mbps cleanly: "  Throughput: 24.50 Mbps" -> 24.50
            mbps = float(line.split(":")[1].strip().split()[0])
            flow_mbps.append(mbps)
            
    with open("exp3_fairness.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Flow_ID", "Throughput_Mbps"])
        for i, mbps in enumerate(flow_mbps):
            writer.writerow([i, mbps])

def exp_high_bdp():
    print("=== EXPERIMENT 4: High BDP Scenario ===")
    # High bandwidth, high delay (e.g., satellite links, long fat networks)
    # Bandwidth=500Mbps, Delay=100ms
    with open("exp4_highbdp.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Protocol", "Throughput_Mbps"])
        for p in ["TcpNewReno", "TcpCubic"]:
            prefix = f"out_exp4_highbdp_{p}"
            out = run_sim(prefix, p, 0.005, "500Mbps", "100ms", 20.0)
            mbps = 0.0
            for line in out.split('\n'):
                if "Total Throughput:" in line:
                    mbps = float(line.split(":")[-1].strip().split()[0])
            writer.writerow([p, mbps])

def exp_incast():
    print("=== EXPERIMENT 5: Data Center Incast Problem ===")
    # 20 senders hitting 1 receiver over a 1Gbps bottleneck.
    # No artificial loss, the loss happens because of buffer overflow.
    with open("exp5_incast.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Protocol", "Throughput_Mbps"])
        for p in ["TcpNewReno", "TcpCubic"]:
            prefix = f"out_exp5_incast_{p}"
            # 20 flows, 1Gbps bottleneck, 1ms delay, 15s duration
            out = run_sim(prefix, p, 0.0, "1Gbps", "1ms", 15.0, n_flows=20, incast=True)
            mbps = 0.0
            for line in out.split('\n'):
                if "Total Throughput:" in line:
                    mbps = float(line.split(":")[-1].strip().split()[0])
            writer.writerow([p, mbps])

if __name__ == "__main__":
    exp_throughput_vs_loss()
    exp_recovery_time()
    exp_fairness()
    exp_high_bdp()
    exp_incast()
    print("All experiments completed! Run plot_results.py to generate graphs.")
