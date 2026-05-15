import sys
import os
import argparse
import csv

# Ensure the NS-3 Python bindings are in path since waf --pyrun fails to wrap it correctly in this setup
sys.path.append(os.path.abspath('build/bindings/python'))

try:
    import ns.applications
    import ns.core
    import ns.internet
    import ns.network
    import ns.point_to_point
    import ns.flow_monitor
except ImportError:
    print("Error: Could not import ns modules. Please run this from the ns-3.35 directory.")
    sys.exit(1)

# Helper mock for ns calls
class NSMock:
    def __getattr__(self, name):
        for mod in [ns.applications, ns.core, ns.internet, ns.network, ns.point_to_point, ns.flow_monitor]:
            if hasattr(mod, name):
                return getattr(mod, name)
        raise AttributeError(f"ns has no attribute {name}")
ns_api = NSMock()

def main():
    parser = argparse.ArgumentParser(description='NS-3 TCP Simulation (Reno vs Cubic)')
    parser.add_argument('--protocol', type=str, default='TcpCubic', choices=['TcpCubic', 'TcpNewReno'])
    parser.add_argument('--loss_rate', type=float, default=0.0)
    parser.add_argument('--bandwidth', type=str, default='10Mbps')
    parser.add_argument('--delay', type=str, default='20ms')
    parser.add_argument('--duration', type=float, default=30.0)
    parser.add_argument('--prefix', type=str, default='results')
    parser.add_argument('--n_flows', type=int, default=1)
    parser.add_argument('--incast', action='store_true', help='Run Incast star topology')
    args = parser.parse_args()

    # Set TCP variant globally
    tcp_variant = f"ns3::{args.protocol}"
    ns_api.Config.SetDefault("ns3::TcpL4Protocol::SocketType", ns_api.StringValue(tcp_variant))

    # Tune TCP buffers to allow CWND to grow large enough to fill high-speed links
    ns_api.Config.SetDefault("ns3::TcpSocket::SndBufSize",  ns_api.UintegerValue(4194304))  # 4 MB
    ns_api.Config.SetDefault("ns3::TcpSocket::RcvBufSize",  ns_api.UintegerValue(4194304))  # 4 MB
    ns_api.Config.SetDefault("ns3::TcpSocket::SegmentSize", ns_api.UintegerValue(1448))      # standard MSS
    ns_api.Config.SetDefault("ns3::TcpSocket::InitialCwnd", ns_api.UintegerValue(10))        # RFC 6928


    if args.incast:
        # INCAST TOPOLOGY: Router(0), Receiver(1), Senders(2..N+1)
        nodes = ns_api.NodeContainer()
        nodes.Create(args.n_flows + 2)
        
        router = nodes.Get(0)
        receiver = nodes.Get(1)
        
        # Bottleneck link: Router to Receiver
        p2p_bottleneck = ns_api.PointToPointHelper()
        p2p_bottleneck.SetDeviceAttribute("DataRate", ns_api.StringValue(args.bandwidth))
        p2p_bottleneck.SetChannelAttribute("Delay", ns_api.StringValue(args.delay))
        p2p_bottleneck.SetQueue("ns3::DropTailQueue", "MaxSize", ns_api.StringValue("100p"))
        
        bottleneck_devices = p2p_bottleneck.Install(router, receiver)
        
        # Sender links: Sender to Router (High bandwidth, low delay)
        p2p_sender = ns_api.PointToPointHelper()
        p2p_sender.SetDeviceAttribute("DataRate", ns_api.StringValue("1Gbps"))
        p2p_sender.SetChannelAttribute("Delay", ns_api.StringValue("1ms"))
        
        sender_devices_list = []
        for i in range(args.n_flows):
            devs = p2p_sender.Install(nodes.Get(2 + i), router)
            sender_devices_list.append(devs)
            
        internet = ns_api.InternetStackHelper()
        internet.Install(nodes)
        
        ipv4 = ns_api.Ipv4AddressHelper()
        ipv4.SetBase(ns_api.Ipv4Address("10.1.1.0"), ns_api.Ipv4Mask("255.255.255.0"))
        interfaces_bottleneck = ipv4.Assign(bottleneck_devices)
        
        interfaces_senders = []
        for i, devs in enumerate(sender_devices_list):
            ipv4.SetBase(ns_api.Ipv4Address(f"10.1.{2+i}.0"), ns_api.Ipv4Mask("255.255.255.0"))
            ifaces = ipv4.Assign(devs)
            interfaces_senders.append(ifaces)
            
        # Add artificial packet loss to the receiver
        if args.loss_rate > 0:
            loss_model = ns_api.RateErrorModel()
            loss_model.SetAttribute("ErrorRate", ns_api.DoubleValue(args.loss_rate))
            loss_model.SetAttribute("ErrorUnit", ns_api.StringValue("ERROR_UNIT_PACKET"))
            bottleneck_devices.Get(1).SetAttribute("ReceiveErrorModel", ns_api.PointerValue(loss_model))
            
        # Global routing is needed because of multiple subnets
        ns_api.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
        
    else:
        # NORMAL P2P TOPOLOGY
        nodes = ns_api.NodeContainer()
        nodes.Create(2)

        # Point-to-Point bottleneck
        p2p = ns_api.PointToPointHelper()
        p2p.SetDeviceAttribute("DataRate", ns_api.StringValue(args.bandwidth))
        p2p.SetChannelAttribute("Delay", ns_api.StringValue(args.delay))
        
        # Use CoDel or DropTail
        p2p.SetQueue("ns3::DropTailQueue", "MaxSize", ns_api.StringValue("100p"))

        devices = p2p.Install(nodes)

        # Add artificial packet loss to the receiver
        if args.loss_rate > 0:
            loss_model = ns_api.RateErrorModel()
            loss_model.SetAttribute("ErrorRate", ns_api.DoubleValue(args.loss_rate))
            loss_model.SetAttribute("ErrorUnit", ns_api.StringValue("ERROR_UNIT_PACKET"))
            devices.Get(1).SetAttribute("ReceiveErrorModel", ns_api.PointerValue(loss_model))

        internet = ns_api.InternetStackHelper()
        internet.Install(nodes)

        ipv4 = ns_api.Ipv4AddressHelper()
        ipv4.SetBase(ns_api.Ipv4Address("10.1.1.0"), ns_api.Ipv4Mask("255.255.255.0"))
        interfaces = ipv4.Assign(devices)

    # Setup applications for n_flows
    bulk_send_helpers = []
    for i in range(args.n_flows):
        port = 50000 + i
        
        # Sink always on Receiver (Node 1)
        sink = ns_api.PacketSinkHelper("ns3::TcpSocketFactory", ns_api.InetSocketAddress(ns_api.Ipv4Address.GetAny(), port))
        sink_apps = sink.Install(nodes.Get(1))
        sink_apps.Start(ns_api.Seconds(0.0))
        sink_apps.Stop(ns_api.Seconds(args.duration))

        if args.incast:
            # Senders are nodes 2 to N+1
            sender_node = nodes.Get(2 + i)
            # Connect to Receiver's IP on the bottleneck interface
            dest_ip = interfaces_bottleneck.GetAddress(1)
            # Incast: start all flows at EXACTLY the same time (1.0s)
            start_time = 1.0
        else:
            # Normal P2P: Sender is Node 0
            sender_node = nodes.Get(0)
            dest_ip = interfaces.GetAddress(1)
            # Stagger normal flows slightly
            start_time = 1.0 + i * 0.1

        bulk_send = ns_api.BulkSendHelper("ns3::TcpSocketFactory", ns_api.InetSocketAddress(dest_ip, port))
        bulk_send.SetAttribute("MaxBytes", ns_api.UintegerValue(0)) # Unlimited
        client_apps = bulk_send.Install(sender_node)
        client_apps.Start(ns_api.Seconds(start_time))
        client_apps.Stop(ns_api.Seconds(args.duration))

    # --- Tracing ---
    cwnd_file = open(f"{args.prefix}_cwnd.csv", "w")
    cwnd_writer = csv.writer(cwnd_file)
    cwnd_writer.writerow(["time", "flow_id", "cwnd"])

    # Instead of Python trace hooks (which are notoriously brittle in pybindgen),
    # we will rely on FlowMonitor and the standard outputs for throughput results,
    # and just trust the aggregate output, or we can use AsciiTraceHelper for CWND.
    ascii_trace = ns_api.AsciiTraceHelper()
    if args.incast:
        p2p_bottleneck.EnableAsciiAll(ascii_trace.CreateFileStream(f"{args.prefix}_trace.tr"))
    else:
        p2p.EnableAsciiAll(ascii_trace.CreateFileStream(f"{args.prefix}_trace.tr"))

    # Use FlowMonitor to compute accurate throughput
    flowmon_helper = ns_api.FlowMonitorHelper()
    monitor = flowmon_helper.InstallAll()

    # Run
    ns_api.Simulator.Stop(ns_api.Seconds(args.duration + 0.1))
    ns_api.Simulator.Run()
    
    monitor.CheckForLostPackets()
    classifier = flowmon_helper.GetClassifier()
    
    total_rx_bytes = 0
    print("--- FlowMonitor Results ---")
    
    flow_stats = monitor.GetFlowStats()
    # Handle the Python API dictionary mapping returned by flowmon
    # Note: ns3.35 FlowStats mapping is a C++ map converted to an iterable list of tuples
    
    for flow_id, stats in flow_stats:
        t = classifier.FindFlow(flow_id)
        # We only care about TCP data flows (protocol 6 = TCP)
        if t.protocol == 6 and t.destinationPort >= 50000:
            rx_bytes = stats.rxBytes
            # Duration measured from first tx to last rx
            time_val = (stats.timeLastRxPacket.GetSeconds() - stats.timeFirstTxPacket.GetSeconds())
            if time_val > 0:
                mbps = (rx_bytes * 8) / (1e6 * time_val)
            else:
                mbps = 0
            print(f"Flow {flow_id} ({t.sourceAddress}:{t.sourcePort} -> {t.destinationAddress}:{t.destinationPort}):")
            print(f"  Tx Packets: {stats.txPackets}")
            print(f"  Rx Packets: {stats.rxPackets}")
            print(f"  Lost Packets: {stats.lostPackets}")
            print(f"  Throughput: {mbps:.2f} Mbps")
            total_rx_bytes += rx_bytes
    
    # Calculate overall average throughput across the configured duration (1.0 to duration)
    eff_time = args.duration - 1.0
    if eff_time <= 0: eff_time = 0.1
    total_mbps = (total_rx_bytes * 8) / (1e6 * eff_time)
    print(f"Total Throughput: {total_mbps:.2f} Mbps")

    ns_api.Simulator.Destroy()
    cwnd_file.close()

if __name__ == '__main__':
    main()
