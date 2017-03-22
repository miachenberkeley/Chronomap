import Controller
import BasicModel as md

MainModel = md.Model()
A = Controller.Controller(MainModel)

# List Graphs
avail_graphs = A.list_available_graphs()
print ("List of Recorded Graphs:")
print(avail_graphs);

# Load Graph - open the first graph
if avail_graphs:
    print ("Opening Graph:")
    print(avail_graphs[0])

    A.load_graph(avail_graphs[0])

    print(A.model.total_graph.nodes())

    raw_input("Graph Loaded. Presse any key to continue")
else:
    print("No graph found")

# Create new graph
name_graph = A.create_new_graph("GraphOK")
nodeA = A.create_evenement("EV A", "07-08-2016 17:25:00", "08-08-2016 17:25:01", 1, "BLAH BLAH BLAH", "http://")
nodeB = A.create_evenement("EV B", "08-08-2016 17:25:00", "09-08-2016 17:25:01", 1, "OK", "http://")
nodeC = A.create_evenement("EV C", "08-07-2016 00:00:00", "09-08-2016 00:00:00", 1, "HOOOOO", "http://")
nodeD = A.create_evenement("EV D", "08-07-2016 00:00:01", "09-08-2016 00:00:10", 1, "DD", "http://")

A.create_edge(nodeA,nodeB, "LeLien", "Une mega explosion", "[]")
A.create_edge(nodeB,nodeA, "InverseLien", "Une giga explosion", "[]")
#print(type(nodeA),type(nodeB))

#print(A.edge_data(nodeA,nodeB))

A.create_weak_link(nodeA, nodeB, nodeC)
A.create_weak_link(nodeA, nodeB, nodeD)

raw_input("Weak Link Ok")

print(A.list_weak_link(nodeA,nodeB))

raw_input("List weak link Ok")

A.export_loaded_graph_xml("test_export.xml")

raw_input("Export Graph OK")

#A.import_graph_xml("test_export.xml", "importedGraph")

A.remove_weak_link(nodeA,nodeB,nodeD)

raw_input("Weak Link Removed. Press any key to rollback")

print(Controller.undo.stack().undotext())

Controller.undo.stack().undo()

raw_input("Weak Link Ok")

A.remove_edge(nodeA,nodeB)

raw_input("Press any key to rollback")

Controller.undo.stack().undo()

raw_input("Press any key to delete node")

A.delete_evenement(nodeA)

raw_input("Press any key to rollback")

Controller.undo.stack().undo()

raw_input("Press any key to modify node A")

dict_changedata = {}

dict_changedata['title'] = "EV BA2"
dict_changedata['description'] = "New description"
dict_changedata['start_time'] = "12-10-2016 17:25:01"
dict_changedata['end_time'] = "13-10-2016 17:25:02"
dict_changedata['node_group'] = "2"
dict_changedata['drawing'] = {}
dict_changedata['drawing']['x'] = 99
dict_changedata['drawing']['y'] = 98
dict_changedata['drawing']['color'] = "black"
dict_changedata['drawing']['size'] = "150%"
dict_changedata['drawing']['border'] = "1"
dict_changedata['drawing']['order'] = "0"

A.modify_evemenement(nodeA, **dict_changedata)



raw_input("Press any key to rollback")

Controller.undo.stack().undo()

raw_input("Presse any key to delete graph")

A.delete_graph(name_graph)

raw_input("Press any key to rollback")

Controller.undo.stack().undo()

raw_input("Press any key to change graph")

nodes = A.get_node_list()
#print("nodes %s" %nodes)
edges=A.get_edge_list()
#print("edges %s" %edges)

nodeEditA = nodes[0]
nodeEditB = nodes[1]
nodeEditC = nodes[2]

dict_change_edge = {}
dict_change_edge['label'] = "LIEN MAGIQUE"
dict_change_edge['description'] = "OH NON UNE GRANDE CATASTROPHE"

print(nodeEditA)
print(nodeEditB)
print(dict_change_edge)


A.modify_edge(nodeEditA, nodeEditB, **dict_change_edge)

raw_input("Press any key to rollback")

Controller.undo.stack().undo()

raw_input("Press any key to create a weak link");

A.create_weak_link(nodeEditA, nodeEditB, nodeEditC)
A.create_weak_link(nodeEditA, nodeEditB, nodeEditC)

raw_input("Press any key for force atlas layout")

#pos = A.calculate_position(A.model.total_graph,'fa2_layout')

#Controller.nx.draw_networkx(A.model.total_graph, pos)
#Controller.plt.show()
#raw_input("Press any key to rollback")

Controller.undo.stack().undo()

pos = A.model.build_pos_from_graph()
#print(pos)
Controller.nx.draw_networkx(A.model.total_graph, A.model.build_pos_from_graph())
Controller.plt.show()

raw_input("Press any key to rollback")

Controller.undo.stack().undo()
