import BasicModel as md
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Loads the model
model = md.Model()

model.convert_tabbed_csv_to_graph("cartography.csv", "links.csv", "graph_tab.xml")

model.import_graph("graph_tab.xml", "TestData")

nx.draw(model.total_graph)
plt.show()
