import networkx as nx
import matplotlib.pyplot as plt

import networkx.drawing.nx_agraph


G=nx.balanced_tree(3,5)
pos=graphviz_layout(G,prog='twopi',args='')
plt.figure(figsize=(8,8))
nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
plt.axis('equal')
plt.savefig('circular_tree.png')
plt.show()