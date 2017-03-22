"""Model: Manages data in and connection to database."""
# -*-coding:Latin-1 -*

import networkx as nx
import py2neo
import csv
from py2neo import ogm
import matplotlib
import matplotlib.pyplot as plt
import ConfigParser
import os
import datetime
import re
import numpy as np
# import matplotlib
import sys

class Model:
    """
    Class that represents the model. Connects to the database and manages all
    data operations.

    The file config.ini is used to load database information. The local graph
    is where the operations are treated. At any moment you can push the
    modifications to the remote version.


    :var total_graph: Local graph with all nodes.
    :var label_graph: Name of the loaded graph.
    :var db_connection: Connection to neo4j using py2neo.

    .. todo:: Possibility of simultaneous operation.

    """

    def __init__(self):
        # Config Parser
        config = ConfigParser.ConfigParser()
        #print(os.path.join(os.path.dirname(__file__),  'config.ini'))
        if getattr(sys, 'frozen', False):
		    # frozen
			dir_path = os.path.dirname(sys.executable)
        else:
		    # unfrozen
			dir_path = os.path.dirname(os.path.realpath(__file__))
        config.read(os.path.join(dir_path,  'config.ini'))
        #config.read(os.path.join(os.path.dirname(sys.executable) ,  'config.ini'))
        optionDict = {}
        options = config.options("Database")
        for option in options:
            optionDict[option] = config.get("Database", option)

        db_user = optionDict["user"]
        db_pass = optionDict["pass"]
        db_host = optionDict["url"]

        # Create empty NetworkX Graph
        self.total_graph = nx.DiGraph()
        # Initiates connetion with the Database
        self.db_connection = py2neo.database.Graph(host=db_host,
                                                   user=db_user,
                                                   password=db_pass)
        self.label_graph = None
        # Loads unique id generator or creates it
        self.get_unique_id_generator()

    def date_from_string(self, string_date):
        """
        Transform a date string into a number
        since 0001-01-01 00:00:00 UTC, plus one

        :param string_date: Date in the format "%d-%m-%Y %H:%M:%S" to be transformed.
        :returns: the time equivalent integer.
        """
        date = datetime.datetime.strptime(string_date, "%d-%m-%Y %H:%M:%S")
        num_date = matplotlib.dates.date2num(date)

        return num_date

    def string_from_numdate(self, num_date):
        """
        Transform a date number into a string.

        :param num_date: Integer from 0001-01-01 00:00:00 UTC, plus one.
        :returns: Date in the format "%d-%m-%Y %H:%M:%S".
        """
        date = matplotlib.dates.num2date(num_date)
        string_date = date.strftime("%d-%m-%Y %H:%M:%S")

        return string_date

    def get_unique_id_generator(self):
        """
        Get/Creates a special node into the database that registers one UniqueID
        starts with id=0.
        """

        container_uuid = UniqueID.select(self.db_connection).first()

        if not container_uuid:
            id_node = UniqueID()
            id_node.actual_id = 0
            self.db_connection.push(id_node)
            self.id_generator = id_node
        else:
            self.id_generator = container_uuid

    def generate_id(self):
        """
        Gets the next available node id using an unique id generator. Updates the
        id generator in the database.

        :returns: Next free integer for a node.
        """
        actual_id = self.id_generator.actual_id
        self.id_generator.actual_id = actual_id + 1
        self.db_connection.push(self.id_generator)
        return actual_id

    def list_recorded_graphs(self):
        """
        List all graphs that are currently in the database
        * Organized in chronographXX-NAME

        :returns labels: Existing labels in the database
        """
        # Query database
        labels = []
        query = "START n=node(*) RETURN distinct labels(n)"
        data = self.db_connection.data(query)
        # Get all data
        for response_data in data:
            temp = response_data.values()
        # Parse data found
            if len(temp[0]):
                temp = temp[0]
                for a in temp:
                    if 'chronograph' in a:
                        labels.append(a)
        return labels

    def create_next_available_graph(self, graph_name):
        """
        Sets the graph the next available graph.
        .. warning:: Use simple graph names
                     Overwites the actual graph without saving!

        :params graph_name: Graph string to recorded
        :returns: Loaded graph name
        """

        # Gets the list of recorded networks
        all_graphs = self.list_recorded_graphs()
        # Empty list
        if not all_graphs:
            # Starts by 0
            graph_number = 0
        else:
            # Finds the biggest number
            list_id_found = []
            for x in all_graphs:
                find_result = re.search('(?<=chronograph)[0-9]*?(?=-)', x)
                if find_result:
                    list_id_found.append(int(find_result.group(0)))

            #print(list_id_found)
            if list_id_found:
                graph_number = max(list_id_found) + 1
            else:
                graph_number = 0
        self.label_graph = "chronograph" + str(graph_number) + "-" + graph_name
        self.total_graph = nx.DiGraph()

        return self.label_graph

    def delete_graph(self, full_graph_name):
        """
        Delete a graph by its full name.

        :param full_graph_name: Name of the graph to delete
        """
        escaped_graph_name = "`" + full_graph_name + "`"

        # Get nodes
        all_nodes = list(Evenement.select(
            self.db_connection).where("_:" + escaped_graph_name))
        # Erase all nodes matching
        self.db_connection.run(
            "MATCH (n:" + escaped_graph_name + ")  DETACH DELETE n")

        # Make it undoable
        for node in all_nodes:
            del node.__ogm__.node.__remote__

    def load_graph(self, label):
        """
        Load a graph into the system.

        :param label: name of the graph to load.
        """

        self.label_graph = label

        # Gets the nodes
        nodes = Evenement.select(self.db_connection).where(
            "_: `" + self.label_graph + "`")

        # Builds the graph
        if nodes:
            for node in nodes:
                # Add nodes
                self.total_graph.add_node(node)

            for node in self.total_graph.nodes():
                # Find equivalences
                inter = [x for x in self.total_graph.nodes()
                         if x in node.consequence]
                for i_node in inter:
                    # Get edge properties from database
                    edge_prop = self.edge_attributes(node.consequence.get(i_node, 'label'),
                                                     node.consequence.get(
                                                         i_node, 'descrption'),
                                                     node.consequence.get(i_node, 'attachment_list'))
                    # Grow edge and import properties
                    self.total_graph.add_edge(node, i_node, edge_prop)
                # self.total_graph.add_star([node] + inter)

    def push_graph(self):
        """ Pushes all nodes from the local graph to the database."""
        for node in self.total_graph.nodes():
            self.transform_node_to_neo4j(node)
        for node in self.total_graph:
            self.db_connection.push(node)

    def transform_node_to_neo4j(self, node):
        '''
        Updates an Evenement node into a neo4j node equivalent.
        '''
        # Get nodes that are connected to this one
        related_nodes = self.total_graph.successors(node)

        # Finds intersection
        recorded_nodes = set(node.consequence)
        related_nodes = set(related_nodes)

        nodes_to_delete = recorded_nodes.difference(related_nodes)

        # Adds new nodes
        for actual_node in related_nodes:
            # Read properties
            edge_data = self.total_graph.get_edge_data(node, actual_node)
            # Write properties
            node.consequence.update(actual_node, edge_data)

        # Removes erased nodes
        for actual_node in nodes_to_delete:
            node.consequence.remove(actual_node)

    def push_node(self, node):
        """
        Pushes a node to the database.

        :param node: Node to push
        :type node: Evenement
        """
        self.transform_node_to_neo4j(node)
        self.db_connection.push(node)

    def delete_node(self, node):
        """
        Deletes a node in the database
        """
        self.db_connection.delete(node)

    def init_evenement(self,
                       title,
                       start_time="11-08-2016 17:25",
                       end_time="11-08-2016 17:25",
                       node_group=0,
                       description="",
                       attachment_list=[]):
        """
        Creates a new evenement

        :param title: Name of the node.
        :param start_time: Start time of the node.
        :param end_time: End time of the node.
        :param node_group: Group which the node is into.
        :param description: Description of the node.
        :param attachment_list: List of attached files/urls.

        :returns: Evenement node or False if no graph loaded.
        """
        if self.label_graph:
            # Create Evenement instance
            ev = Evenement()

            # Create Properties
            ev.unique_id = self.generate_id()
            ev.title = title
            ev.description = description
            ev.start_time = self.date_from_string(start_time)
            ev.end_time = self.date_from_string(end_time)
            ev.node_group = node_group
            ev.attachment_list = attachment_list

            # Drawing properites

            # ev.drawing = {"x": 0, "y": 0, "color": ""}

            # Assign to active graph
            ev.__ogm__.node.add_label(self.label_graph)
            return ev
        return False

    def edge_attributes(self, label_name, description=None, attachment_list=None, weak_link=None):
        """
        Format edge atributes.

        :param label_name: Title of the edge.
        :param description: Edge description.
        :param attachment_list: List of attached files/urls.
        :param weak_link
        """
        edge_properties = {}
        edge_properties['label'] = label_name
        edge_properties['description'] = description
        edge_properties['attachment_list'] = attachment_list
        edge_properties['weak_link'] = weak_link
        return edge_properties

    def build_pos_from_graph(self):
        '''
        Builds a pos dictionnary using the actual graph.

        :returns: A dictionnary with nodes as keys that represents the graph pos.
        '''
        pos = {}
        for node in self.total_graph.nodes():
            if node.d_posx:
                x = node.d_posx
            else:
                x = 0
            if node.d_posy:
                y = node.d_posy
            else:
                y = 0

            pos[node] = np.array([x, y])
        return pos

    def update_nodes_from_pos(self, pos):
        for node in self.total_graph.nodes():
            if node in pos:
                node.d_posx = float(pos[node][0])
                node.d_posy = float(pos[node][1])
        self.push_graph()

    def export_graph(self, file_path, graph_to_export = None):
        """
        Exports a graph into GraphML format

        :param file_path: File path to record the graph
        :param graph_to_export: Optional parameter to export another graph

        ..todo: Preserve drawing properties and attachments.
        """
        # Create equivalent structure
        graph_export = nx.DiGraph()

        if graph_to_export is None:
            graph_to_export = self.total_graph
        # Read graph objects
        graph_nodes = graph_to_export.nodes()

        graph_edges = graph_to_export.edges()

        equivalent_id = {}

        for i, node in enumerate(graph_nodes):
            node_properties = {}
            if node.title:
                node_properties['title'] = node.title
            if node.start_time:
                node_properties['start_time'] = self.string_from_numdate(
                    node.start_time)
            if node.end_time:
                node_properties['end_time'] = self.string_from_numdate(
                    node.end_time)
            if node.node_group:
                node_properties['node_group'] = node.node_group
            graph_export.add_node(i, **node_properties)

            # Equivalence dict
            equivalent_id[node.unique_id] = i

            # graph_export.add_node(i,
            #                       title = node.title,
            #                       start_time = node.start_time,
            #                       end_time = node.end_time,
            #                       duration = node.duration,
            #                       node_group = node.node_group
            #                       )

        #print(graph_export.nodes())

        for edge in graph_edges:
            start = graph_nodes.index(edge[0])
            end = graph_nodes.index(edge[1])
            data = self.total_graph.get_edge_data(*edge)

            data = data.copy()

            # Weak link, finds equivalent nodes
            if data['weak_link']:
                weak_link_equivalent_ids = []
                for node_id in data['weak_link']:
                    if equivalent_id[node_id]:
                        weak_link_equivalent_ids.append(equivalent_id[node_id])

                data['weak_link'] = ",".join(str(x) for x in weak_link_equivalent_ids);


            data = dict((k, v) for k, v in data.iteritems() if v)
            graph_export.add_edge(start, end, **data)

        #print(graph_export.edges())
        nx.write_graphml(graph_export, file_path)

    def import_graph(self, file_path, graph_name):
        """
        Imports a graph based on the GraphML format.

        - Unloads the current graph without saving
        - Always creates new nodes

        ..todo: Improve weak link import.

        :param file_path: File to load
        :param graph_name: Name to record the graph.
        """
        import_graph = nx.read_graphml(file_path)

        # Unloads actual graph
        self.total_graph = nx.DiGraph()

        # Sets graph name
        self.create_next_available_graph(graph_name)

        # Builds graph from import
        node_list = import_graph.nodes(data=True)
        edge_list = import_graph.edges()

        node_equivalence = []
        for node, data in node_list:
            graph_ev = self.init_evenement(**data)
            node_equivalence.append((node, graph_ev))
            self.total_graph.add_node(graph_ev)

        for node1, node2 in edge_list:
            for number, node in node_equivalence:
                if number == node1:
                    first = node
                if number == node2:
                    second = node
            data = import_graph.get_edge_data(node1, node2)

            if data['weak_link']:
                weak_link_str = []
                weak_link_list = []
                # Converts weak link str to list
                weak_link_str = data['weak_link'].split(",")
                print(weak_link_str)
                # Searchs the equivalent id
                equivalent_weak_link = False
                for weak_link_value in weak_link_str:
                    # Searchs for equivalence
                    for number, node in node_equivalence:
                        if number == weak_link_value:
                            equivalent_weak_link = node.unique_id
                            break
                    if equivalent_weak_link:
                        weak_link_list.append(equivalent_weak_link)

                data['weak_link'] = weak_link_list
            self.total_graph.add_edge(first, second, data)
        # Sends graph to db
        self.push_graph()

    def convert_tabbed_csv_to_graph(self, node_csv_file, edge_csv_file, out_xml):
        """
        Imports a tabbed csv and converts it to a GraphML format.

        :param node_csv_file: Tabbed node csv to transform.
        :param edge_csv_file: Tabbed edge csv to transform.
        :param out_xml: Converted graphML.
        """

        temporary_graph = nx.DiGraph()

        # Opens the csv files
        node_list = list(csv.reader(open(node_csv_file, 'rb'), delimiter='\t'))
        edge_list = list(csv.reader(open(edge_csv_file, 'rb'), delimiter='\t'))

        # Create nodes
        for line in node_list:
            id_node = int(line[0])
            node_title = line[2]

            string_start_time =  line[3]
            string_end_time = line[4]

            # Convert start date
            start_time = datetime.datetime.strptime(string_start_time, "%Y-%m-%d %H:%M:%S")
            start_num_date = matplotlib.dates.date2num(start_time)

            # Convert end date
            end_time = datetime.datetime.strptime(string_end_time, "%Y-%m-%d %H:%M:%S")
            end_num_date = matplotlib.dates.date2num(end_time)

            # Create node properties
            node_properties = {}
            node_properties['title'] = node_title
            node_properties['start_time'] = self.string_from_numdate(start_num_date)
            node_properties['end_time'] = self.string_from_numdate(end_num_date)

            temporary_graph.add_node(id_node, **node_properties)

        # Create edges
        for line in edge_list:
            id_edge = int(line[0])
            label_edge = str(line[1])
            start = int(line[2])
            end = int(line[3])

            edge_properties = self.edge_attributes(label_edge)
            data = dict((k, v) for k, v in edge_properties.iteritems() if v)

            temporary_graph.add_edge(start, end, **data)

        # Export graph
        nx.write_graphml(temporary_graph, out_xml)

    def compute_closeness_centrality(self, **kwargs):
        return nx.closeness_centrality(self.total_graph, **kwargs)

    def compute_betweeness_centrality(self, **kwargs):
        return nx.betweenness_centrality(self.total_graph, **kwargs)


class Evenement(ogm.GraphObject):
    """
    Main node class, direct linked to the database.

    :var unique_id: Unique ID of the node.
    :var title: Title of the node.
    :var start_time: Start time of the node.
    :var end_time: End time of the node.
    :var node_group: Group of the node.
    :var description: Description of the node.
    :var attachment_list: List of nodes
    :var d_posx: X position in the graph.
    :var d_posy: Y position in the graph.
    :var d_color: Node drawing color (future).
    :var d_size: Size of the node (future).
    :var d_border: Border style (future).
    :var consequence: Represents the links between nodes.
    :var groupWith: Represents the association of nodes.

    """

    __primarykey__ = "unique_id"

    # Essential properties
    unique_id = ogm.Property()
    title = ogm.Property()
    start_time = ogm.Property()
    end_time = ogm.Property()
    node_group = ogm.Property()
    description = ogm.Property()
    attachment_list = ogm.Property()

    # Drawing properties
    # Node view
    d_posx = ogm.Property()
    d_posy = ogm.Property()
    d_color = ogm.Property()
    d_size = ogm.Property()
    d_border = ogm.Property()
    # Chronographic view
    d_order = ogm.Property()

    consequence = ogm.RelatedTo("Evenement")
    groupWith = ogm.RelatedTo("Evenement")

    def __repr__(self):
        return ("< " + str(type(self)) + " id = " +
                str(self.unique_id) + " title = " +
                str(self.title) + " >")


class UniqueID(ogm.GraphObject):
    """
    Gives IDs to nodes
    .. warning:: Manually editing the UID is a bad idea.

    """
    uuid_label = ogm.Label("UniqueID")
    actual_id = ogm.Property()
