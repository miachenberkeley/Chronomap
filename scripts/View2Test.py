""" Manages user input and interface drawing"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from matplotlib.figure import Figure
import Controller as CT
import numpy as np
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
import Draw as D
import MouseFunctionChronologique as MF
import MouseFunctionsCartographie as MFCarto

        
class ViewHandler():
    def __init__(self):
        
        #Chrono canvas
        
        self.GChrono=D.DrawChronoMap(figChrono,canvasChrono,axChrono) #canvas for gantt Digramm 
        self.GCarto=D.DrawCartoMap(figCarto,canvasCarto,axCarto) #canvas for cartographie
        
        #data
        
        nodeAchrono=self.GChrono.controller.create_evenement("outdated research material", "01-01-2016 00:00:00", "01-02-2016 00:00:00", 1, "BLAH BLAH BLAH", "http://")
        
        nodeBchrono=self.GChrono.controller.create_evenement("Projected tsunami frequency too low", "08-08-2016 00:00:00", "09-10-2016 00:00:00", 1, "OK", "http://")
        
        self.GChrono.controller.create_evenement("EV C", "08-07-2016 00:00:00", "09-08-2016 00:00:00", 1, "HOOOOO", "http://")
        
        self.GChrono.controller.create_evenement("Accident", "08-10-2016 00:00:00", "09-11-2016 00:00:00", 1, "HOOOOO", "http://")
        
        self.GChrono.controller.create_edge(nodeAchrono,nodeBchrono, "LeLien", "Une mega explosion", "[]")
        self.GChrono.controller.create_edge(nodeBchrono,nodeAchrono, "InverseLien", "Une giga explosion", "[]")        

        #Carto Canvas
        nodeAcarto=self.GCarto.controller.create_evenement("outdated research material", "01-01-2016 00:00:00", "01-02-2016 00:00:00", 1, "BLAH BLAH BLAH", "http://")
        
        nodeBcarto=self.GCarto.controller.create_evenement("Projected tsunami frequency too low", "08-08-2016 00:00:00", "09-10-2016 00:00:00", 1, "OK", "http://")
        
        nodeCcarto=self.GCarto.controller.create_evenement("EV C", "08-07-2016 00:00:00", "09-08-2016 00:00:00", 1, "HOOOOO", "http://")
        
        nodeDcarto=self.GCarto.controller.create_evenement("Accident", "08-10-2016 00:00:00", "09-11-2016 00:00:00", 1, "HOOOOO", "http://")
        
        self.GCarto.controller.create_edge(nodeAcarto,nodeBcarto, "LeLien", "Une mega explosion", "[]")
        self.GCarto.controller.create_edge(nodeBcarto,nodeAcarto, "InverseLien", "Une giga explosion", "[]")   
        
        '''
        #event data       
        self.xdataChrono=MF.MouseFunctionC(self.GChrono).xdata
        self.ydataChrono=MF.MouseFunctionC(self.GChrono).ydata
        self.xdataCarto=MFCarto.MouseFunctionsCartographie(axCarto,self.GCarto).xdata
        self.ydataCarto=MFCarto.MouseFunctionsCartographie(axCarto,self.GCarto).ydata       ''' 
        
        '''
        #MouseFunction
        self.MouseChrono=MF.MouseFunctionC(self.GChrono)
        self.MouseCarto=MFCarto.MouseFunctionsCartographie(axCarto,self.GCarto)        '''
        
        #Creating the ListStore model
        
        #node_liststore
        self.node_liststore = Gtk.ListStore(str, str, str,str,str,str)
        '''
        for i , node in enumerate(self.MouseCarto.datanode):
            print(i,node)'''
        
        
        
        #edge_liststore
        self.edge_liststore = Gtk.ListStore(str, str, str,str,str)
        
        
        #creating the filtre
        self.node_filter = self.node_liststore.filter_new()
        self.edge_filter = self.edge_liststore.filter_new()
        
        #setting the filter function, note that we're not using the
        self.node_filter.set_visible_func(self.node_filter_func)   
        self.edge_filter.set_visible_func(self.edge_filter_func)
    
        #creating the treeview for Node, making it use the filter as a model, and adding the columns
        self.treeviewNode = Gtk.TreeView.new_with_model(self.node_filter)
        for i, column_title in enumerate(["Nom", "Date début", "Date fin", "Type de noeud", "Description du noeud","fichier"]):
            self.Noderenderer = Gtk.CellRendererText()
            self.Noderenderer.set_property("editable", True)
            column = Gtk.TreeViewColumn(column_title, self.Noderenderer, text=i)
            self.treeviewNode.append_column(column) 
            self.Noderenderer.connect("edited", self.onButtonCreateNode)
            
        #creating the treeview for edge
        self.treeviewEdge = Gtk.TreeView.new_with_model(self.node_filter)
        for i, column_title in enumerate(["Nom", "Noeud 1", "Noeud 2", "Type de noeud", "Description du lien","fichier"]):
            self.Edgerenderer = Gtk.CellRendererText()
            self.Edgerenderer.set_property("editable", True)
            column = Gtk.TreeViewColumn(column_title, self.Edgerenderer, text=i)
            self.treeviewEdge.append_column(column)     
            self.Edgerenderer.connect("edited", self.EdgeEdited)
        
        
        
        #setting up the layout, putting the treeview in a scrollwindow
        sw3.add(self.treeviewNode)      
        sw4.add(self.treeviewEdge) 
        
        sw3.show_all()
        sw4.show_all()     
        
    #function related to display information on column
    
    def EdgeEdited(self,widget):
        canvasCarto.draw()
        canvasChrono.draw()
    
    def NodeEdited(self,widget):
        canvasCarto.draw()   
        canvasChrono.draw() 

    def resetplot(self):
        axCarto.cla()
        axCarto.set_xlim(0,10)
        axCarto.set_ylim(0,10)
        axCarto.grid(True) 
        
        axChrono.cla()
        axChrono.set_xlim(0,10)
        axChrono.set_ylim(0,10)
        axChrono.grid(True)             
   
    def node_filter_func(self, model, iter, data):
        pass
            
    def edge_filter_func(self, model, iter, data):   
        pass
    
   
    # All button signals of GTK
        
    #Signal to open windows "creation of node"
    def create_node_button_press_event(self,widget):
        add_node_window.show_all()
        
        
    #Signal to open window "creation of link"    
    def create_link_button_press_event(self,widget):
        add_edge_window.show_all() 
        
    
    def onButtonAddFileNode(self,widget):
        pass
    
    def onButtonCreateNode(self,widget):
        self.resetplot()
        nom=interface.get_object('name_node1').get_text()
        node_type=interface.get_object('node_type1').get_text()
        start_time_node=interface.get_object('start_time_node1').get_text()
        end_time_node=interface.get_object('end_time_node1').get_text()
        #print(nom,node_type,start_time_node,end_time_node)
        
        self.node_liststore.append([nom, start_time_node, end_time_node, node_type, "BLAH BLAH BLAH", "http://"])      
        self.GCarto.controller.create_evenement(nom, start_time_node, end_time_node, node_type, "BLAH BLAH BLAH", "http://") 
        self.GChrono.controller.create_evenement(nom, start_time_node, end_time_node, node_type, "BLAH BLAH BLAH", "http://")
        for i in self.node_liststore:
            print(i)
        canvasCarto.draw()
        canvasChrono.draw()
        
        add_node_window.destroy()
        sw.show_all()
        sw3.show_all()
        
    def onButtonAddFileEdge(self,widget):
        pass
    
    def onButtonCreateEdge(self,widget):
        nom=interface.get_object('name_edge2').get_text()
        edge_description=interface.get_object('edge_type2').get_text()
        node1_edge=interface.get_object('node1_edge_entry').get_text()
        node2_edge=interface.get_object('node2_edge_entry2').get_text()  
        
        #create signal with liststore
        self.edge_liststore.append([node1_edge,node2_edge, nom, edge_description, "[]"])      
        #create link with canvas
        self.GCarto.controller.create_edge(node1_edge,node2_edge, nom, edge_description, "[]")  
        self.GChrono.controller.create_edge(node1_edge,node2_edge, nom, edge_description, "[]")  
        canvasCarto.draw()
        canvasChrono.draw()
        StackWindow.show_all()        
        add_edge_window.destroy()       
        
            
    #Signal to contextual menu
    def onMainFigurePressed(self,widget):
        menu_contextuel.show_all()
    
            
    #Signal of menubars        
    def on_node_file_button_press_event(self,widget):
        add_node_window.show_all()

    def on_create_edge_button_press_event(self,widget):
        add_edge_window.show_all()
    
     
    
    def on_Open_button_press_event(self,widget,event):
        fichierdialogue.show_all()
   
     #signal of about  
    def on_gtk_about_button_release_event(self,widget,event):
        aboutchronomap.show_all()    

    
   
    # close window    
    def on_close_button_press_event(self,widget,event):
        on_quit_button_press_event (widget,event) 
           
    def on_quit_button_press_event (self,widget,event):
    #pop up menu
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,Gtk.ButtonsType.OK_CANCEL, "Vous partez?")
        dialog.format_secondary_text("Voulez vous toujours partir?")
        response=dialog.run()
        if response == Gtk.ResponseType.OK:
            Gtk.main_quit()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
        dialog.destroy()
        return True
    
    def on_mainWindow_destroy(self, widget):
        Gtk.main_quit()    

    def on_carto_display_button_press_event(self,widget,event): 
        '''
        child=StackWindow.get_child()
        
        if child != None:
            StackWindow.remove(child)
        
        self.GCarto.draw_cartograph()
        self.MFCarto=MFCarto.MouseFunctionsCartographie(axCarto,self.GCarto)
        sw.add(canvasCarto)
        sw.show_all()    '''
        
    def on_chrono_display_button_press_event(self,widget,event):
        '''
        child=sw.get_child()
        if child != None:
            sw.remove(child)   
                
        self.GChrono.draw_chronograph()
        self.MFChrono=MF.MouseFunctionC(self.GChrono)
        sw.add(canvasChrono)
        sw.show_all()    '''
   
      



#model using GTK
window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)
window.set_default_size(1500, 1500)
window.set_title('ChronoMap')

vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
self.add(vbox)

stack = Gtk.Stack()
stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
stack.set_transition_duration(1000)

stack_switcher = Gtk.StackSwitcher()
stack_switcher.set_stack(stack)
vbox.pack_start(stack_switcher, True, True, 0)
vbox.pack_start(stack, True, True, 0)

# Init ChronoCanvas
figChrono = Figure(figsize=(20,20), dpi=80)
axChrono = figChrono.add_subplot(111)
canvasChrono = FigureCanvas(figChrono) 


#Init CartoCanvas
figCarto = Figure(figsize=(20,20), dpi=80)
axCarto = figCarto.add_subplot(111)
canvasCarto = FigureCanvas(figCarto) 

        
# List windows
interface = Gtk.Builder()
interface.add_from_file("interface1.glade")
mainWindow=interface.get_object("mainWindow")
aboutchronomap=interface.get_object("aboutchronomap")
fichierdialogue=interface.get_object("fichierdialogue")
StackWindow=interface.get_object("mainFigure")
sw2=interface.get_object("MatplotlibToolbar")
sw3=interface.get_object("scrolledwindow1")
sw4=interface.get_object("scrolledwindow2")
add_node_window=interface.get_object("add_node_window")
add_edge_window=interface.get_object("add_edge_window")
modify_edge_window=interface.get_object("modify_edge_window")
modify_node_window=interface.get_object("modify_node_window")
add_reference_node_edge=interface.get_object("add_reference_node_edge")
popupmenu=interface.get_object("menu_contextuel")
popupmenuCartoNode=interface.get_object("popupmenuCartoNode")
popupmenuCartoEdge=interface.get_object("popupmenuCartoEdge")
popupmenuCartoOtherplace=interface.get_object("popupmenuOtherplace")
popupmenuChronoNode=interface.get_object("popupmenuChronoNode")
popupmenuChronoZoneBC=interface.get_object("popupmenuChronoZoneBC")
popupmenuChoronoZoneA=interface.get_object("popupmenuChronoZoneA")
popupmenuChronoCursor=interface.get_object("popupmenuChronoCursor")


#vbox
vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

#add scrolled window
window.add(StackWindow)



# interface.connect("delete-event", Gtk.main_quit)
interface.connect_signals(ViewHandler())


StackWindow.show_all() 





# All ready - open interface
Gtk.main()

