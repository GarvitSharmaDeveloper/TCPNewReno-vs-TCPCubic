import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

fig, ax = plt.subplots(figsize=(10, 6))

G = nx.DiGraph()

# Add central nodes
G.add_node("Router", pos=(0, 0), color="#F2A900", size=3000)
G.add_node("Receiver\n(Node 1)", pos=(3, 0), color="#E63946", size=3000)

# Add sender nodes in a semicircle
senders = []
for i in range(10):  # Showing 10 visually to avoid clutter, representing 20
    name = f"Sender {i+1}"
    y_pos = 4.5 - i
    G.add_node(name, pos=(-3, y_pos * 0.5), color="#457B9D", size=1500)
    G.add_edge(name, "Router", label="1 Gbps / 1ms")
    senders.append(name)

G.add_edge("Router", "Receiver\n(Node 1)", label="1 Gbps Bottleneck\nDropTail Queue")

pos = nx.get_node_attributes(G, 'pos')
colors = [G.nodes[n]['color'] for n in G.nodes()]
sizes = [G.nodes[n]['size'] for n in G.nodes()]

# Draw edges
nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True, arrowsize=20, width=2.0)

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes, edgecolors="white", linewidths=2)

# Draw labels
nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", font_color="white")

# Draw edge labels
edge_labels = {("Router", "Receiver\n(Node 1)"): "1 Gbps Bottleneck\nDropTail Queue"}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=10, font_weight="bold")

# Title and formatting
plt.title("Data Center Incast Topology (Many-to-1)", fontsize=16, fontweight="bold", pad=20)
plt.text(-4, 0, "20 High-Speed\nMicroservices\n(Simultaneous Burst)", fontsize=12, color="#457B9D", 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='#457B9D', boxstyle='round,pad=0.5'))

ax.axis('off')
plt.tight_layout()
plt.savefig('network_topology.png', dpi=300, transparent=True)
print("Topology diagram generated successfully as network_topology.png")
