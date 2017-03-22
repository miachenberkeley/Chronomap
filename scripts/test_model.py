import BasicModel as md
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Loads the model
model = md.Model()

# List all recorded graphs
all_graphes = model.list_recorded_graphs()

# Load Graph
if all_graphes:
    model.load_graph(all_graphes[0])
else:
    model.load_graph("chronograph0-GRAPH-TEST")

nx.draw_networkx(model.total_graph)
# print(model.total_graph.nodes())

# Graph empty
if not model.total_graph.nodes():
    print("Creating Nodes\n")
    # Create evenements
    a = model.init_evenement("Action A", "07-08-2016 17:25:04", "08-08-2016 17:25:00", "1", "0")
    b = model.init_evenement("Action B", "08-08-2016 17:25:05", "09-08-2016 17:25:00", "1", "0")
    c = model.init_evenement("Action C", "08-08-2016 10:25:06", "09-08-2016 20:25:01", "1", "0")
    d = model.init_evenement("Action D", "09-08-2016 17:25:07", "10-08-2016 17:25:02", "1", "0")
    e = model.init_evenement("Action E", "10-08-2016 17:25:08", "11-08-2016 17:25:03", "1", "0")

    # Edge List
    edges = [(a,b),(a,c),(a,d),(a,e),(b,d),(b,e),(c,d),(d,e)]

    # Add nodes
    model.total_graph.add_node(a)
    model.total_graph.add_node(b)
    model.total_graph.add_node(c)
    model.total_graph.add_node(d)
    model.total_graph.add_node(e)

    # Add edges
    model.total_graph.add_edges_from(edges)

# Create edge data between node x and y
edge_xy = model.edge_attributes("test_relation", "une grande explosion")


x = model.total_graph.nodes()[0]
if model.total_graph.successors(x):
    y = model.total_graph.successors(x)[0]
    model.total_graph.add_edge(x,y,edge_xy)

# Push Graph
model.push_graph()

# Draw resulting graph

pos=nx.shell_layout(model.total_graph)
#print(pos)
nx.draw(model.total_graph,pos)
plt.show()

# Export graph
model.export_graph("graph1.xml")

# Import graph
model.import_graph("graph1.xml", "chronograph1")


#model.list_recorded_graphs()
