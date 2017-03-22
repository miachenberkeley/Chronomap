"""Manages actions."""

import BasicModel as md
import View as vw
import networkx as nx
import forceatlas.forceatlas as nxfa2
import undo
import ViewHandler as V

import warnings

class Controller:
    """
    Main controller class.
    """
    def __init__(self, model):
        """
        Initialization: Gets the model

        :param model: Model class to use
        """
        # Loads the model
        self.model = model

    @undo.undoable
    def create_evenement(self,
                         title,
                         start_time,
                         end_time,
                         node_group,
                         description="",
                         attachment_list=None):
        """
        Creates a node and add it to the graph. Pushes to the database.

        It's undoable. Undoing it deletes the node in the database but lets your
        repush it.

        """
        new_evenement = self.model.init_evenement(title,
                                                  start_time,
                                                  end_time,
                                                  node_group,
                                                  description,
                                                  attachment_list)
        self.model.total_graph.add_node(new_evenement)
        self.model.push_node(new_evenement)
        yield "Evenement " + str(new_evenement) + " created", new_evenement

        # Case undo
        self.model.db_connection.delete(new_evenement)
        self.clear_remote(new_evenement)
        self.model.total_graph.remove_node(new_evenement)

    @undo.undoable
    def delete_evenement(self, node):
        """
        delete_evenement(node)
        Deletes a node. Undoable.

        :param node: Node to delete
        :type node: Evenement
        """
        # Records information from before, in case of undo
        old_node = node

        # Records the nodes that come and go from this node, in case of undo
        old_connection_list_suc = self.model.total_graph.successors(node)
        old_connection_list_pre = self.model.total_graph.predecessors(node)

        # Records the properties of the connected nodes
        old_connection_properties_suc = [self.model.total_graph.get_edge_data(node, x)
                                         for x in old_connection_list_suc]
        old_connection_properties_pre = [self.model.total_graph.get_edge_data(x, node)
                                         for x in old_connection_list_pre]

        if self.model.total_graph.has_node(node):
            # Remove connections that comes to the node
            for connected_node in old_connection_list_pre:
                self.remove_edge(connected_node, node)

            # Delete the node
            self.model.total_graph.remove_node(node)
            self.model.delete_node(node)
            self.clear_remote(node)
            yield "Node " + str(node) + " deleted"

            # Case undo
            # Read node to the graph
            self.model.total_graph.add_node(old_node)

            # Readd edges to the graph
            for i, connected_node in enumerate(old_connection_list_suc):
                self.model.total_graph.add_edge(node,
                                                connected_node,
                                                old_connection_properties_suc[i])
            for i, connected_node in enumerate(old_connection_list_pre):
                self.model.total_graph.add_edge(connected_node,
                                                node,
                                                old_connection_properties_pre[i])

            # Convert a node to neo4j and push
            self.model.push_node(old_node)

            # Pushes all the nodes that are connected to this one
            for connected_node in old_connection_list_pre:
                self.model.push_node(connected_node)
        else:
            warnings.warn("Impossible to find node")
            yield "Impossible to delete node", False

    @undo.undoable
    def modify_evemenement(self, node, **kwargs):
        """
        Modify an evenement.

        :param node: node to edit
        :type node: Evenement
        :param **kwargs: dictionnary explosion of parameters of a node to change
        """
        old_node_properties = self.get_all_evenement_data(node)
        self.set_evenement_data(node, **kwargs)
        # Sends the node to the database
        self.model.push_node(node)
        yield "Node " + str(node) + " modified"
        # Undo actions
        self.set_evenement_data(node, **old_node_properties)
        self.model.push_node(node)

    @undo.undoable
    def create_edge(self,
                    node1,
                    node2,
                    title,
                    description=None,
                    attachment_list=None,
                    weak_link_list=[]):
        """
        Creates an undoable directional edge.

        :param node1: Start edge node.
        :type node1: Evenement.
        :param node2: End edge node.
        :type node2: Evenement.

        :param title: Edge title.
        :param description: Edge description.
        :param attachment_list: List of attached objects.
        :param weak_link_list: List of nodes id that are weak-linked to this edge
        """
        # Verify nodes exist
        if (node1 in self.model.total_graph.nodes()
                and node2 in self.model.total_graph.nodes()):
            edge_prop = self.model.edge_attributes(title,
                                                   description,
                                                   attachment_list,
                                                   weak_link_list)
            self.model.total_graph.add_edge(node1, node2, edge_prop)
            self.model.push_node(node1)
            yield "Added edge " + str(node1) + " " + str(node2)
            # Undoes, delete edge
            self.remove_edge(node1, node2)
        else:
            warnings.warn("Impossible to find edge")
            yield "Create edge failed", False

    @undo.undoable
    def remove_edge(self, node1, node2):
        """
        Removes an edge. Is directionnal.

        :param node1: first node of the edge.
        :type node1: Evenement.
        :param node2: second node.
        :type node2: Evenement.
        """
        if self.model.total_graph.has_edge(node1, node2):
            # Records data in case of an undo
            edge_data = self.model.total_graph.get_edge_data(node1, node2)
            # Removes the edge
            self.model.total_graph.remove_edge(node1, node2)
            # Pushes the node
            self.model.push_node(node1)
            # Action done yields until undo
            yield "Deleted edge " + str(node1) + " " + str(node2)
            # Undos, recreate edge
            self.create_edge(node1, node2, *edge_data.values())
        else:
            warnings.warn("Impossible to find edge")
            yield "Egde not found", False

    @undo.undoable
    def reverse_edge(self, node1, node2):
        """
        Reverse direction of an edge

        .. todo:: Not implemented.
        """
        pass

    @undo.undoable
    def modify_edge(self, node1, node2, **kwargs):
        """
        Modifies an edge given its nodes. Undoable.

        :param node1: Start edge node.
        :type node1: Evenement.
        :param node2: End edge node.
        :type node2: Evenement.

        :param **kwargs: Properties to edit.
        """
        if self.model.total_graph.has_edge(node1, node2):
            old_edge_data = self.model.total_graph.get_edge_data(
                node1, node2).copy()
            edge_data = self.model.total_graph.get_edge_data(node1, node2)

            # Which to change?
            if 'label' in kwargs:
                edge_data['label'] = kwargs['label']
            if 'title' in kwargs:
                edge_data['label'] = kwargs['title']
            if 'description' in kwargs:
                edge_data['description'] = kwargs['description']
            if 'attachment_list' in kwargs:
                edge_data['attachment_list'] = kwargs['attachment_list']
            if 'weak_link_append' in kwargs:
                if isinstance(edge_data['weak_link'] , list):
                    edge_data['weak_link'].extend(kwargs['weak_link_append'])
                else:
                    edge_data['weak_link'] = kwargs['weak_link_append']
            if 'weak_list' in kwargs:
                    edge_data['weak_link'] = kwargs['weak_link']

            self.model.total_graph.add_edge(node1, node2, edge_data)
            self.model.push_node(node1)

            yield "Edit edge " + str(node1) + " , " + str(node2)
            # Case UNDO
            self.model.total_graph.add_edge(node1, node2, old_edge_data)
            self.model.push_node(node1)
        else:
            warnings.warn("Impossible to find edge")
            yield "Edit edge failed: edge doesn't exist", False


    @undo.undoable
    def create_weak_link (self, node1, node2, node_to_link):
        '''
        Creates a weak_link between two nodes 1 and 2.
        It is directionnal.

        :param node1: First node of the edge
        :param node2: Second node of the edge
        :param node_to_link: node that references that edge

        '''
        if self.model.total_graph.has_edge(node1, node2):
            old_edge_data = self.model.total_graph.get_edge_data(
                node1, node2).copy()
            edge_data = self.model.total_graph.get_edge_data(node1, node2)

            dict_change_edge = {}
            dict_change_edge['weak_link_append'] = [ node_to_link.unique_id ]
            # Adds the weak link to the edge
            self.modify_edge(node1, node2, **dict_change_edge)
            yield "Weak link added"
            # Undo
            dict_change_edge = old_edge_data
            self.modify_edge(node1, node2, **dict_change_edge)
        else:
            warnings.warn("Impossible to find edge")
            yield "Operation Failed", False

    @undo.undoable
    def remove_weak_link (self, node1, node2, node_to_unlink):
        '''
        Destroys a weak_link between two nodes 1 and 2.
        It is directionnal.

        :param node1: First node of the edge
        :param node2: Second node of the edge
        :param node_to_unlink: node that references that edge

        '''
        if self.model.total_graph.has_edge(node1, node2):
            old_edge_data = self.model.total_graph.get_edge_data(
                node1, node2).copy()
            edge_data = self.model.total_graph.get_edge_data(node1, node2)

            if(node_to_unlink.unique_id in edge_data['weak_link']):
                edge_data['weak_link'].remove(node_to_unlink.unique_id)
                dict_change_edge = {}
                dict_change_edge['weak_link'] = edge_data['weak_link']
                # Adds the weak link to the edge
                self.modify_edge(node1, node2, **dict_change_edge)
                yield "Weak link removed"
                # Undo - Reloads old edge data
                dict_change_edge = old_edge_data
                self.modify_edge(node1, node2, **dict_change_edge)
        else:
            warnings.warn("Impossible to find edge")
            yield "Remove weak link Failed", False

    def list_weak_link (self,node1, node2):
        '''
        Lists all weak links from an edge. May lag for big data.

        :param node1: First node of the edge
        :param node2: Second node of the edge
        :param node_to_unlink: node that references that edge

        '''
        # Exists edge?
        if self.model.total_graph.has_edge(node1, node2):
            edge_data = self.model.total_graph.get_edge_data(node1, node2)

            weak_linked_nodes = []
            dict_id_nodes = self.nodes_id_dict()
            # Any weak links?
            if edge_data['weak_link']:
                for node_num in edge_data['weak_link']:
                    if dict_id_nodes[node_num]:
                        weak_linked_nodes.append(dict_id_nodes[node_num])

        return weak_linked_nodes


    # get edge data
    def edge_data(self,node1,node2):
        return self.model.total_graph.get_edge_data(node1,node2)

    # Dictionnary of nodes based by id
    def nodes_id_dict(self):
        all_nodes = self.get_node_list()
        all_nodes_dict = {}
        for node in all_nodes:
            all_nodes_dict[node.unique_id] = node
        return all_nodes_dict

    @undo.undoable
    def create_new_graph(self, graph_name):
        """
        Creates a new graph. Undoable.

        .. warning:: Needs to have at least 1 node assigned to persist into the
        database

        :param graph_name: Desired graph name.
        """
        old_label_graph = self.model.label_graph
        old_graph = self.model.total_graph
        name_chosen = self.model.create_next_available_graph(graph_name)
        yield "Created graph " + name_chosen, name_chosen
        # Undo - Delete graph
        self.delete_graph(name_chosen)
        self.model.total_graph = old_graph
        self.model.label_graph = old_label_graph
        self.model.push_graph()

    @undo.undoable
    def delete_graph(self, graph_name):
        print("delete %s" %graph_name)
        """
        Delete a graph given its name. Undoable.

        :param graph_name: Exact match of the graph name to delete.
        """
        # Verify if the graph exists
        if graph_name in self.model.list_recorded_graphs():
            # Records the old graph in case of undo
            old_label_graph = self.model.label_graph
            old_graph = self.model.total_graph
            self.model.delete_graph(graph_name)
            yield "Deleted graph" + graph_name
            # Undo - Rebuilds last graph
            self.model.total_graph = old_graph
            self.model.label_graph = old_label_graph
            self.model.push_graph()
        else:
            warnings.warn("Impossible to find graph")
            yield "Action delete_graph failed"

    @undo.undoable
    def load_graph(self, graph_name):
        """
        Loads a graph given its name. Undoable

        :param graph_name: Exact match of the graph name to load_graph
        """
        if graph_name in self.model.list_recorded_graphs():
            # Records the old graph in case of undo
            old_label_graph = self.model.label_graph
            self.model.load_graph(graph_name)
            yield "Deleted graph" + graph_name
            # Undo - Rebuilds last graph
            self.model.label_graph = old_label_graph
            self.model.load_graph(old_label_graph)
        else:
            warnings.warn("Impossible to find graph_name")
            yield "Action load_graph failed"

    def list_available_graphs(self):
        """
        Lists the name of recorded graphs
        """
        return self.model.list_recorded_graphs()

    def export_loaded_graph_xml(self, file_path):
        """
        Call to the export_graph of the model. Doesn't preserve every propertie
        of the graph. Needs improvement.

        :param file_path: Path to save
        """
        self.model.export_graph(file_path)

    def import_graph_xml(self, file_path, graph_name):
        """
        Call of the import_graph of the model.

        :param file_path: Path to load
        :param graph_name: Graph name to record
        """
        self.model.import_graph(file_path, graph_name)

    @undo.undoable
    def calculate_position(self, algorithm, **kwargs):
        """
        Computes node position. Registers the result directly into the graph
        properties.

        Possible algorithms:
        ---------------------

        * 'circular_layout'
        * 'random_layout'
        * 'shell_layout'
        * 'spring_layout'
        * 'spectral_layout'
        * 'fa2_layout'

        :param algorithm:
        :type algorithm: string
        :param **kwargs:
        """
        old_pos = self.model.build_pos_from_graph()

        switcher = {
            'circular_layout': nx.circular_layout(self.model.total_graph, **kwargs),
            'random_layout': nx.random_layout(self.model.total_graph, **kwargs),
            'shell_layout': nx.shell_layout(self.model.total_graph, **kwargs),
            'spring_layout': nx.spring_layout(self.model.total_graph, **kwargs),
            'spectral_layout': nx.spectral_layout(self.model.total_graph, **kwargs),
            'fa2_layout': nxfa2.forceatlas2_layout(self.model.total_graph, **kwargs)
        }

        # 'graphviz_layout': nx.graphviz_layout(self.model.total_graph, **kwargs)

        result_pos = switcher.get(algorithm, None)

        if result_pos:
            self.model.update_nodes_from_pos(result_pos)
            yield "Layout calculated using " + algorithm, result_pos
            # Case undo - Goes back to previous Layout
            self.model.update_nodes_from_pos(old_pos)
        else:
            warnings.warn("Impossible to calculate position")
            yield "Failed to calculate position"


    def get_position(self):
        return self.model.build_pos_from_graph()

    def save_current_graph(self):
        """
        Saves the current graph
        """
        if self.model.label_graph:
            self.model.push_graph()

    def get_node_list(self):
        """
        Gets the node list
        """
        return self.model.total_graph.nodes()

    def get_edge_list(self):
        """
        Gets the edge list
        """
        return self.model.total_graph.edges()

    def total_graph(self):
        """
        Gets the total graph
        """
        return self.model.total_graph

    def set_evenement_data(self, node, **kwargs):
        """
        Sets every parameter of a node
        """
        if 'title' in kwargs:
            node.title = kwargs['title']
        if 'description' in kwargs:
            node.description = kwargs['description']
        if 'start_time' in kwargs:
            # Accepts time in string or number format
            if isinstance(kwargs['start_time'], basestring):
                node.start_time = self.model.date_from_string(
                    kwargs['start_time'])
            else:
                node.start_time = kwargs['start_time']
        if 'end_time' in kwargs:
            # Accepts time in string or number format
            if isinstance(kwargs['end_time'], basestring):
                node.end_time = self.model.date_from_string(kwargs['end_time'])
            else:
                node.end_time = kwargs['end_time']
        if 'attachment_list' in kwargs:
            node.attachment_list = kwargs['attachment_list']
        if 'node_group' in kwargs:
            node.node_group = kwargs['node_group']
        if 'drawing' in kwargs:
            if 'x' in kwargs['drawing']:
                node.d_posx = kwargs['drawing']['x']
            if 'y' in kwargs['drawing']:
                node.d_posy = kwargs['drawing']['y']
            if 'color' in kwargs['drawing']:
                node.d_color = kwargs['drawing']['color']
            if 'size' in kwargs['drawing']:
                node.d_size = kwargs['drawing']['size']
            if 'border' in kwargs['drawing']:
                node.d_border = kwargs['drawing']['border']
            if 'order' in kwargs['drawing']:
                node.d_order = kwargs['drawing']['order']

    def get_all_evenement_data(self, node):
        """
        Lists every property of a node
        """
        node_dict = {}
        if self.model.total_graph.has_node(node):
            node_dict['title'] = node.title
            node_dict['description'] = node.description
            node_dict['start_time'] = node.start_time
            node_dict['end_time'] = node.end_time
            node_dict['node_group'] = node.node_group
            node_dict['attachment_list'] = node.attachment_list
            node_dict['drawing'] = {}
            node_dict['drawing']['x'] = node.d_posx
            node_dict['drawing']['y'] = node.d_posy
            node_dict['drawing']['color'] = node.d_color
            node_dict['drawing']['size'] = node.d_size
            node_dict['drawing']['border'] = node.d_border
            node_dict['drawing']['order'] = node.d_order
        return node_dict

    def get_closeness_centrality(self):
        return self.model.compute_closeness_centrality()

    def get_betweeness_centrality(self):
        return self.model.compute_betweeness_centrality()

    def clear_remote(self, node):
        del node.__ogm__.node.__remote__


if __name__ == '__main__':
    # Init Model
    MainModel = md.Model()

    # Init Controller
    MainController = Controller(MainModel)

    # Init View
    MainView = vw.View(MainController, V.ViewHandler)

    # Program Running.
