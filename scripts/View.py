# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import draw_cartograph as Draw_cartograph
import draw_chronograph as Draw_chrono
import ViewHandler as V

import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')

class View():
    def __init__(self, MainController, ViewHandler):

        #set windows
        self.window = Gtk.Window()
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.set_default_size(10000, 10000)
        self.window.set_title('ChronoMap')
        self.ViewHandler = ViewHandler

        #Init Glade file # Get windows from glade
        self.interface = Gtk.Builder()
        self.interface.add_from_file("interface1.glade")
        self.mainWindow = self.interface.get_object("mainWindow")
        self.aboutchronomap = self.interface.get_object("aboutchronomap")
        self.importfile = self.interface.get_object("import")
        self.fichierdialogue = self.interface.get_object("fichierdialogue")
        self.sw = self.interface.get_object("mainFigure")
        self.toolbar = self.interface.get_object("MatplotlibToolbar")
        self.SWViewListStore = self.interface.get_object("scrolledwindow1")
        self.SWEdgeStore = self.interface.get_object("SWEdgeFilter")
        self.entryComboBox = self.interface.get_object("entry5")
        self.new_graph = self.interface.get_object("new_graph")
        self.new_graph_name = self.interface.get_object("new_graph_name")
        self.combo_filter = self.interface.get_object("combo_filter")
        self.EdgeComboBox = self.interface.get_object("EdgeComboBox")
        self.NodeComboBox = self.interface.get_object("NodeComboBox")
        self.display_settings = self.interface.get_object("Display_setting")
        self.add_node_window = self.interface.get_object("add_node_window")
        self.add_edge_window = self.interface.get_object("add_edge_window")
        self.modify_edge_window = self.interface.get_object("modify_edge_window")
        self.modify_node_window = self.interface.get_object("modify_node_window")
        self.add_reference_node_edge = self.interface.get_object("add_reference_node_edge")
        self.setting_cursor = self.interface.get_object("setting_cursor")
        self.date_cursor = self.interface.get_object("date_cursor")
        self.edge_add_weak_link = self.interface.get_object("edge_add_weak_link")
        self.node_add_weak_link_with_an_edge = self.interface.get_object("add_weak_link_with_an_edge")
        self.export_dialog = self.interface.get_object("export_dialog")


        # Context Menus
        self.node_menu = self.interface.get_object("node_menu")
        self.edge_menu = self.interface.get_object("edge_menu")
        self.empty_menu = self.interface.get_object("empty_menu")
        self.cursor_menu = self.interface.get_object("cursor_menu")
        self.graduation_menu = self.interface.get_object("graduation_menu")


        #ListStore
        self.mainFigure = self.interface.get_object("mainFigure")
        self.graphliststoreView = self.interface.get_object("graphliststore")

        #Add transient parent
        self.fichierdialogue.set_transient_for(self.mainWindow)
        self.new_graph.set_transient_for(self.mainWindow)
        self.importfile.set_transient_for(self.mainWindow)
        self.modify_edge_window.set_transient_for(self.mainWindow)
        self.modify_node_window.set_transient_for(self.mainWindow)
        self.add_node_window.set_transient_for(self.mainWindow)
        self.add_edge_window.set_transient_for(self.mainWindow)

        #self.display_settings.set_transient_for(self.mainWindow)
        self.mainWindow.add(self.display_settings)

        #Global controller
        self.controller=MainController

        # Global model
        self.model = self.controller.model

        # Global node list
        self.nodelist = self.controller.get_node_list()

        #Gloabl edge list
        self.edgelist = self.controller.get_edge_list()

        # Create a graph with test data
        self.create_test_data()

        # Initialize Carto
        self.initCarto()

        # Initialize Chrono
        self.initChrono()
        #Display Mode
        self.display_Mode = None


        #Creating the ListStore model
        #Combo box
        self.textComboBox = None

        #node_liststore
        self.node_liststore = Gtk.ListStore(str, str, str,str,str,str)
        #edge_liststore
        self.edge_liststore = Gtk.ListStore(str, str, str,str,str,str)

        #graph_liststore
        self.graph_liststore = Gtk.ListStore(str)

        #creating the filtre
        self.node_type_filter = self.node_liststore.filter_new()
        self.current_filter = None


        #setting the filter function, note that we're not using the
        self.node_type_filter.set_visible_func(self.node_type_filter_func)

        self.create_liststore()
        self.create_graph_list_store()

        #selection on graphliststore
        select = self.treeviewGraph.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        # Connect with signals
        self.interface.connect_signals(V.ViewHandler(self))

        #setting up the layout, putting the treeview in a scrollwindow

        self.window.add(self.sw)
        self.sw.show_all()

        # All ready - open interface
        Gtk.main()

    def create_liststore(self):
        #update nodelist
        self.nodelist = self.controller.get_node_list()

        if len(self.FdessinCarto.pos) != 0:
            for i,node in enumerate(self.FdessinCarto.pos):
                self.node_liststore.append([str(node.title),self.controller.model.string_from_numdate(int(node.start_time)),self.controller.model.string_from_numdate(int(node.end_time)),str(node.node_group),str(node.description),str(node.attachment_list)])


        self.edgelist = self.controller.get_edge_list()

        if len(self.edgelist) !=0:
            for i in self.edgelist:
                edge_prop=self.controller.edge_data(i[0],i[1])

                self.edge_liststore.append([edge_prop['label'],str(i[0].title),str(i[1].title),edge_prop['description'],edge_prop['attachment_list'],str(edge_prop['weak_link'])])

        #creating the treeview for Node, making it use the filter as a model, and adding the columns
        self.treeviewNode = Gtk.TreeView.new_with_model(self.node_type_filter)

        for i, column_title in enumerate(["Name", "Beginning date", "End date", "Type of node", "Description of node","files"]):
            self.Noderenderer = Gtk.CellRendererText()
            self.Noderenderer.set_property("editable", True)
            column = Gtk.TreeViewColumn(column_title, self.Noderenderer, text=i)
            column.set_sort_column_id(0)
            self.treeviewNode.append_column(column)


        #creating the treeview for edge
        self.treeviewEdge = Gtk.TreeView.new_with_model(self.edge_liststore)

        for i, column_title in enumerate(["Name", "Node 1", "Node 2", "Description of edge","file","weak-link"]):
            self.Edgerenderer = Gtk.CellRendererText()
            self.Edgerenderer.set_property("editable", True)
            column = Gtk.TreeViewColumn(column_title, self.Edgerenderer, text=i)
            column.set_sort_column_id(0)
            self.treeviewEdge.append_column(column)

        self.SWViewListStore.add(self.treeviewNode)
        self.SWEdgeStore.add(self.treeviewEdge)
        self.SWViewListStore.show_all()
        self.SWEdgeStore.show_all()

    def create_graph_list_store(self):
        #add on liststore
        if len(self.controller.list_available_graphs()) != 0:
           for i in self.controller.list_available_graphs():
               self.graph_liststore.append([i])

        #create the treewiew for the graphliststore
        self.treeviewGraph = Gtk.TreeView.new_with_model(self.graph_liststore)
        for i, column_title in enumerate(["graph name"]):
            self.Graphrenderer = Gtk.CellRendererText()
            self.Graphrenderer.set_property("editable", True)
            column = Gtk.TreeViewColumn(column_title, self.Graphrenderer, text=i)
            column.set_sort_column_id(0)
            self.treeviewGraph.append_column(column)

        self.graphliststoreView.add(self.treeviewGraph)
        self.graphliststoreView.show_all()

    def clear_liststore(self):
        nodetreeiter = self.node_liststore.get_iter_first()
        edgetreeiter = self.edge_liststore.get_iter_first()

        #print"avant",len(self.node_liststore),len(self.edge_liststore)


        while len(self.node_liststore) != 0:
            if nodetreeiter != None :
                self.node_liststore.remove(nodetreeiter)
            else :
                nodetreeiter = self.node_liststore.iter_next(nodetreeiter)

        while len(self.edge_liststore) != 0:
            if edgetreeiter != 0 :
                self.edge_liststore.remove(edgetreeiter)
            else :
                self.edge_liststore.iter_next(edgetreeiter)
            #print(self.edge_liststore[edgetreeiter][0])
        #print "apres", len(self.node_liststore), len(self.edge_liststore)



    def on_tree_selection_changed(self,selection):
        self.model, self.treeiter = selection.get_selected()
        #if self.treeiter != None:
         #   print("You selected", self.model[self.treeiter][0])
        #else:
         #   return True



    def node_type_filter_func(self, model,iter, data):
         # Test if the node type is the one in the filter

        #print (self.textComboBox,model[iter][3])
        if self.current_filter is None or self.current_filter == "None":
            return True
        else:
            #print("activate filtre")
            return model[iter][3] == self.current_filter

    def update_data(self):
        self.CartoEvent = self.FdessinCarto.Detect()
        self.ChronoEvent = self.FdessinChrono.Detect()

        #print(self.CartoEvent,self.ChronoEvent)

    def connect_functions_Chrono(self):
        #MouseFunction Chrono
        self.FdessinChrono.zoom_wheel(1.2)
        self.FdessinChrono.popup = self.FdessinChrono.ax.text(0, 0, '', style='italic',bbox = {'facecolor':'y', 'alpha':0.5, 'pad':10})
        self.FdessinChrono.ly = self.FdessinChrono.ax.axvline(color='k')  # the vert line
        self.FdessinChrono.txt = self.FdessinChrono.ax.text(0.7, 0.9, '', transform=self.FdessinChrono.ax.transAxes)
        self.FdessinChrono.cursor()
        self.FdessinChrono.node_popup_mouse_over()
        self.FdessinChrono.pan_keyboard()


    def connect_functions_Carto(self):
        # MouseFunction carto
        self.CartoEvent = self.FdessinCarto.Detect()
        self.FdessinCarto.pan_drag()
        self.FdessinCarto.pan_keyboard()
        self.FdessinCarto.drag_node()
        self.FdessinCarto.drag_create_edge()
        self.FdessinCarto.node_popup_mouse_over()
        self.FdessinCarto.edge_popup_mouse_over()

    def on_carto_node_position_change(self, caller, node, pos):

        dict_changedata = {}
        dict_changedata['drawing'] = {}

        dict_changedata['drawing']['x'] = pos[0]
        dict_changedata['drawing']['y'] = pos[1]

        self.controller.modify_evemenement(node, **dict_changedata)

        caller.clear_all();
        caller.draw_cartograph(True);
        #caller.connect_functions_Carto()

    def on_chrono_node_position_change(self, caller, node, pos):

        dict_changedata = {}


        if pos[0]:
            dict_changedata['start_time'] = self.model.string_from_numdate(pos[0])
        if pos[1]:
            dict_changedata['end_time'] = self.model.string_from_numdate(pos[1])
        if len(pos) > 2:
            if pos[3]:
                dict_changedata['drawing'] = {}
                dict_changedata['drawing']['order'] = pos[3]

        if dict_changedata:
            self.controller.modify_evemenement(node, **dict_changedata)

        caller.full_redraw();

        #change the liststore
        for i in self.node_liststore:
            print(i[0], node.title)
            if i[0] == node.title:
                if pos[0]:
                    i[1] = self.model.string_from_numdate(pos[0])
                if pos[1]:
                    i[2] = self.model.string_from_numdate(pos[1])

        self.SWViewListStore.show_all()

    def create_test_data(self):
        #Create a New graph on the controller
        self.controller.create_new_graph("CartoChronomap")

        #add node & edges
        nodeA=self.controller.create_evenement("test", "01-01-2016 00:00:00", "01-02-2016 00:00:00", "3", "BLAH BLAH BLAH", "http://")
        nodeB= self.controller.create_evenement("Projected tsunami frequency too low", "08-08-2016 00:00:00", "09-10-2016 00:00:00", "1", "OK", "http://")
        nodeC=self.controller.create_evenement("EV C", "08-07-2016 00:00:00", "09-08-2016 00:00:00", "1", "HOOOOO", "http://")
        nodeD=self.controller.create_evenement("Accident", "08-10-2016 00:00:00", "09-11-2016 00:00:00", "2", "HOOOOO", "http://")

        self.controller.create_edge(nodeA,nodeB, "LeLien", "Une mega explosion", "[]")
        self.controller.create_edge(nodeB,nodeA, "InverseLien", "Une giga explosion", "[]")
        self.controller.create_edge(nodeA,nodeD, "LienTest", "Ceci est un lien test", "[]")
        self.controller.calculate_position('spring_layout');

    def initCarto(self):
        #Init CartoCanvas
        self.figCarto = Figure(figsize=(20,20), dpi=80)
        self.axCarto = self.figCarto.add_subplot(111)
        self.canvasCarto = FigureCanvas(self.figCarto)

        #Connect to draw Cartograph
        self.FdessinCarto = Draw_cartograph.DrawCartoMap(self.axCarto, self.controller)

        # Draw carto
        self.FdessinCarto.draw_cartograph()

        # MouseFunction carto
        self.CartoEvent = self.FdessinCarto.Detect()
        self.FdessinCarto.pan_drag()
        self.FdessinCarto.pan_keyboard()
        self.FdessinCarto.drag_node()
        self.FdessinCarto.drag_create_edge()
        self.FdessinCarto.node_popup_mouse_over()
        self.FdessinCarto.edge_popup_mouse_over()
        # self.FdessinCarto.DrawLines()

        # Connect to ACTIONS
        self.FdessinCarto.connect("node_position_change", self.on_carto_node_position_change)

    def initChrono(self):
        # Init ChronoCanvas
        self.figChrono = Figure(figsize=(20,20), dpi=80)
        self.axChrono = self.figChrono.add_subplot(111)
        self.canvasChrono = FigureCanvas(self.figChrono)

        # Connect to draw chronograph
        self.FdessinChrono = Draw_chrono.DrawChronoMap(self.axChrono,self.controller)

        # Draw Chrono
        self.FdessinChrono.draw_chronograph()

        #MouseFunction Chrono
        #self.FdessinChrono.zoom_wheel(1.2)
        self.ChronoEvent = self.FdessinChrono.Detect()
        self.FdessinChrono.cursor()
        self.FdessinChrono.node_popup_mouse_over()
        self.FdessinChrono.pan_keyboard()
        self.FdessinChrono.drag_rectangle()

        self.FdessinChrono.connect("node_position_change", self.on_chrono_node_position_change)

    def redraw(self):
        self.FdessinChrono.full_redraw()
        self.FdessinCarto.full_redraw()
