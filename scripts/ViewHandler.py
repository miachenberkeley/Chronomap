import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import networkx as nx
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
from matplotlib.widgets import SubplotTool
from matplotlib.figure import Figure




class ViewHandler():

    def __init__(self, ViewConnection):
        #Global variable
        self.View = ViewConnection
        self.file_name = None
        self.graph_name = None
        self.file_name_activate = False
        self.charge_graph_activate = False
        self.selection = None
        self.click_coordinates = None
        self.copied_node = None
        self.export_graph_activate = False

        #connect events
        self.connect_events()


    def resetplot(self):
        self.View.axCarto.cla()
        self.View.axCarto.set_xlim(0,10)
        self.View.axCarto.set_ylim(0,10)
        self.View.axCarto.grid(True)

        self.View.axChrono.cla()
        self.View.axChrono.set_xlim(0,10)
        self.View.axChrono.set_ylim(0,10)
        self.View.axChrono.grid(True)

    def connect_events(self):
        # Callback - Recieve actions from Carto
        # Connect to delete evenement event
        self.View.FdessinCarto.connect('delete_evenement', self.on_delete_evenement)
        # Connect to the rclick_canvas event
        self.View.FdessinCarto.connect('rclick_canvas', self.on_right_click_carto)


        #Connect to the gclikc_canvas event
        self.View.FdessinCarto.connect('lrelease_canvas', self.on_left_release_carto)
        # Connect to the rclick_canvas event for chrono
        self.View.FdessinChrono.connect('rclick_canvas', self.on_right_click_chrono)





        '''MainWindows'''
    # All button signals of GTK

    #Signal for the filter liststore

    def on_entryComboBox_changed(self,widget):
        entryComboBox = self.View.interface.get_object('entryComboBox').get_text()
        textComboFilter = self.View.combo_filter.get_active_text()
        print("acitivate")
        if textComboFilter == "Filter by node's beginning date":
            #print("%s language selected!" % textComboFilter)
            self.View.current_filter = entryComboBox
            self.View.node_beginning_date_filter.refilter()

        if textComboFilter == "Filter by node's end date":
            #print("%s language selected!" % textComboFilter)
            self.View.current_filter = entryComboBox
            self.View.node_end_date_filter.refilter()

        if textComboFilter == "Filter by type of node":
            print("%s filter selected!" % textComboFilter)
            print("textComboFilter %s" % entryComboBox)
            self.View.current_filter = entryComboBox
            self.View.node_type_filter.refilter()


    #Signal to show the  popup display settings
    #Windows Disply settings
    def on_Display_settings_clicked(self,widget):
        self.View.display_settings.show_all()


    #Signal to hide Grid
    def on_Hide_grid_clicked(self,widget):
        self.View.FdessinChrono.hide_grid()
        self.View.FdessinCarto.hide_grid()
        self.View.canvasCarto.draw()
        self.View.canvasChrono.draw()
        self.View.sw.show_all()



    #Signal to display Grid
    def on_Display_grid_clicked(self,widget):
        self.View.FdessinChrono.display_grid()
        self.View.FdessinCarto.display_grid()
        self.View.canvasCarto.draw()
        self.View.canvasChrono.draw()
        self.View.sw.show_all()


    #Signal to hide cursor
    def on_hide_cursor_clicked(self,widget):
        #self.View.FdessinChrono.draw_chronograph()
        self.View.FdessinChrono.ly.set_visible(False)
        self.View.canvasChrono.draw()
        self.View.sw.show_all()

    #Signal to display cursor
    def on_Display_cursor_clicked(self,widget):
        self.View.FdessinChrono.ly.set_visible(True)
        #self.View.FdessinChrono.cursor()
        self.View.canvasChrono.draw()
        self.View.sw.show_all()

    #Signal to open window "creation of link"
    def create_link_button_press_event(self,widget):
        print("right")
        self.View.add_edge_window.run()

        '''add_node_Windows'''

    #Signal related to add node windows
    def on_add_files_node_clicked(self,widget):
        self.View.fichierdialogue.run()

    def on_create_node_ok_clicked(self,widget):
        if not self.file_name_activate:
            self.file_name= "HTTP://"
        print(self.file_name_activate,self.file_name)

        #self.resetplot()
        nom=self.View.interface.get_object('node_name_add').get_text()
        node_type=self.View.interface.get_object('node_type_add').get_text()
        start_time_node=self.View.interface.get_object('node_start_add').get_text()
        end_time_node=self.View.interface.get_object('node_end_add').get_text()
        node_description = self.View.interface.get_object('node_description_add').get_text()
        #print(nom,node_type,start_time_node,end_time_node)

        self.View.node_liststore.append([nom, start_time_node, end_time_node, node_type, node_description, self.file_name])
        self.View.controller.create_evenement(nom, start_time_node, end_time_node, node_type, node_description, self.file_name)

        self.View.FdessinCarto.draw_cartograph()
        self.View.FdessinChrono.clear_all()
        self.View.connect_functions_Chrono()
        self.View.FdessinChrono.draw_chronograph()

        self.View.canvasCarto.draw()
        self.View.canvasChrono.draw()
        self.View.sw.show_all()
        self.View.SWViewListStore.show_all()
        self.View.add_node_window.hide()

        #reupdate data
        self.file_name = None
        self.file_name_activate = False

    def on_cancel_create_node_clicked(self,widget):
        self.View.add_node_window.hide()
        return True

    '''create_edge_windows'''
    #Signal related to Edge

    def on_add_files_edge_button_clicked(self,widget):
        self.View.fichierdialogue.run()

    def on_create_edge_clicked(self,widget):
        if not self.file_name_activate:
            self.file_name= "HTTP://"

        name = self.View.interface.get_object('edge_name_add').get_text()
        edge_description = self.View.interface.get_object('edge_type').get_text()
        node1_edge_name = self.View.interface.get_object('edge_node1').get_text()
        node2_edge_name = self.View.interface.get_object('edge_node2').get_text()
        node1_edge = None
        node2_edge = None
        #create signal with liststore
        self.View.edge_liststore.append([name,node1_edge_name,node2_edge_name, edge_description, self.file_name])
        #update nodelist
        self.View.nodelist = self.View.controller.get_node_list()
        #lookup the nodes which link selected edge
        for i in range(len(self.View.nodelist)):
            #print(self.View.nodelist[i].title, node1_edge_name, node2_edge_name)
            if self.View.nodelist[i].title == node1_edge_name:
                node1_edge = self.View.nodelist[i]
                #print(node1_edge, type(node1_edge))
            if self.View.nodelist[i].title == node2_edge_name:
                node2_edge = self.View.nodelist[i]
                #print(node2_edge, type(node2_edge))


        self.View.controller.create_edge(node1_edge,node2_edge, name, edge_description, self.file_name)

        #for edge in self.View.edgelist:
            #print("before update %s" %edge)
        #update edgelist
        self.View.edgelist = self.View.controller.get_edge_list()
        for i in self.View.edgelist:
            #print (i)
            pos = self.View.FdessinCarto.controller.get_position()
            self.View.FdessinCarto.nodecollection = nx.draw_networkx_nodes(self.View.FdessinCarto.G, pos,ax=self.View.FdessinCarto.ax)
            self.View.FdessinCarto.datanode = self.View.FdessinCarto.nodecollection.get_offsets()

        self.View.FdessinCarto.draw_cartograph()

        self.View.canvasCarto.draw()

        self.View.sw.show_all()
        self.View.SWViewListStore.show_all()
        self.View.add_edge_window.hide()

        #reupdate data
        self.file_name = None
        self.file_name_activate = False

    def on_cancel_create_edge_clicked(self,widget):
        self.View.add_edge_window.hide()
        return True


        '''modify_node_Windows'''
    #Signal related to modify_node_windows
    def on_add_files2_clicked(self,widget):
        self.View.fichierdialogue.run()


    def on_ok_node_edit_clicked(self,widget):

        if not self.file_name_activate:
            self.file_name= "HTTP://"

        print("self.selection %s " %self.selection)

        if self.View.display_Mode == "carto":
            node2modify = self.View.FdessinCarto.selection[1][0]
        elif self.View.display_Mode == "chrono":
            node2modify = self.View.FdessinChrono.selection[1][0]


        dict_changedata = {}
        nom = self.View.interface.get_object('node_name_edit').get_text()
        node_type = self.View.interface.get_object('node_type_edit').get_text()
        start_time_node = self.View.interface.get_object('node_start_edit').get_text()
        end_time_node = self.View.interface.get_object('node_end_edit').get_text()
        description_node = self.View.interface.get_object('edit_node_description').get_text()


        dict_changedata['title'] = nom
        dict_changedata['description'] = description_node
        dict_changedata['start_time'] = start_time_node
        dict_changedata['end_time'] = end_time_node
        dict_changedata['node_group'] = node_type
        dict_changedata['attachment_list'] = self.file_name

        # change the liststore
        for i in self.View.node_liststore:
            print(i[0], node2modify.title)
            if i[0] == node2modify.title:
                i[0] = nom
                i[1] = start_time_node
                i[2] = end_time_node
                i[3] = node_type
                i[4] = description_node
                i[5] = self.file_name

        #change the nodelist
        print("I change ie")
        self.View.controller.modify_evemenement(node2modify,**dict_changedata)

        #Redraw
        self.View.redraw()

        self.View.sw.show_all()
        self.View.SWViewListStore.show_all()
        self.View.modify_node_window.hide()

        #reupdate data
        self.file_name = None
        self.file_name_activate = False

    def on_add_files_node_button_edit_clicked(self,widget):
        self.View.fichierdialogue.run()

    def on_cancel_node_edit_clicked(self,widget):
        self.View.modify_node_window.show_all()
        return True

        '''modify_edge_Windows'''
    def on_add_files_edge_edit_button_clicked(self,widget):
        self.View.fichierdialogue.run()

    #Signal related to modify_edge_windows
    def on_edite_edge_ok_clicked(self,widget):
        edge2modify = self.View.FdessinCarto.selection[1]
        if not self.file_name_activate:
            self.file_name= "HTTP://"
        dict_changedata = {}
        name = self.View.interface.get_object('edge_edit_name').get_text()
        edge_description = self.View.interface.get_object('edge_edit_type').get_text()
        former_node1_edge = edge2modify[0]
        former_node2_edge = edge2modify[1]



        dict_changedata['title'] = name
        dict_changedata['description'] = edge_description
        dict_changedata['attachment_list'] = self.file_name
        print(dict_changedata, former_node1_edge, former_node2_edge)
        #print(node1_edge_name,node1_edge,node2_edge_name,node2_edge, self.file_name)
        if former_node1_edge:
            #change the GTK's edge liststore
            for i in self.View.edge_liststore:
                if (i[1] == former_node1_edge.title) and (i[2] == former_node2_edge.title):
                    print('change edge_liststore')
                    print(i[0],i[3])
                    i[0] = name
                    i[3] = edge_description
                    i[4] = self.file_name

            #change the dataset liststore
            self.View.controller.modify_edge(former_node1_edge, former_node2_edge, **dict_changedata)
        else :
            dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, "This node does not exist")
            # set_transient parent for dialog
            dialog.set_transient_for(self.View.mainWindow)
            dialog.run()

        self.View.initCarto()
        self.View.initChrono()
        self.connect_events()
        self.View.sw.show_all()
        self.View.SWViewListStore.show_all()
        self.View.modify_edge_window.hide()

        #reupdate data
        self.file_name = None
        self.file_name_activate = False

    def on_cancel_node_edit_clicked(self,widget):
        self.View.modify_edge_window.hide()
        return True



    #Signal of menubars
    def on_New_activate(self,widget):

        self.View.new_graph.show_all()

    def on_Open_button_press_event(self,widget,event):
        self.charge_graph_activate = True
        print("charge_graph_activate_cb %s" % self.charge_graph_activate)
        self.View.fichierdialogue.run()

     #signal of about
    def on_gtk_about_button_release_event(self,widget,event):
        self.View.aboutchronomap.show_all()

    def on_quit_button_press_event (self,widget,event):
    #pop up menu
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,Gtk.ButtonsType.OK_CANCEL, "Vous partez?")
        dialog.format_secondary_text("Voulez vous toujours partir?")
        response=dialog.run()
        if response == Gtk.ResponseType.OK:
            Gtk.main_quit()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.hide()
        dialog.hide()
        return True


#Dispay carto mode or chrono graph

    def on_carto_display_button_press_event(self,widget,event):
        if self.View.display_Mode != "carto":
            self.View.display_Mode = "carto"
            child=self.View.sw.get_child()
            child1 = self.View.toolbar.get_child()
            #print(child1)

            if child != None:
                self.View.toolbar.remove(child1)
                self.View.sw.remove(child)
                self.box.remove(self.View.canvasChrono)

            self.box=Gtk.Box()
            self.View.sw.add(self.box)
            self.box.pack_start(self.View.canvasCarto, True, True, 0)
            #Add toolbar
            toolbar = NavigationToolbar(self.View.canvasCarto, self.View.window)
            self.View.toolbar.add_with_viewport(toolbar)
            child1 = self.View.toolbar.get_child()
            #print(child1)
            self.View.sw.show_all()
            #self.View.toolbar.show_all()

    def on_chrono_display_button_press_event(self,widget,event):
        if self.View.display_Mode != "chrono":
            self.View.display_Mode= "chrono"

            child = self.View.sw.get_child()
            child1 = self.View.toolbar.get_child()

            if child != None:
                self.View.toolbar.remove(child1)
                self.View.sw.remove(child)
                self.box.remove(self.View.canvasCarto)

            self.box=Gtk.Box()
            self.View.sw.add(self.box)
            self.box.pack_start(self.View.canvasChrono, True, True, 0)

            #Add toolbar
            toolbar = NavigationToolbar(self.View.canvasChrono, self.View.window)
            self.View.toolbar.add_with_viewport(toolbar)

            self.View.sw.show_all()

    # Add destroy signals for all windows
    def on_aboutchronomap_destroy(self,widget):
        self.View.aboutchronomap.hide()
        return True

    def on_mainWindow_destroy(self, widget):
        Gtk.main_quit()

    def on_Display_setting_delete_event(self,widget,event):
        self.View.display_settings.hide()
        return True

    def on_aboutdialog_chronograph_delete_event(self,widget,event):
        self.View.aboutchronomap.hide()
        return True

    def on_add_edge_window_delete_event(self,widget,event):
        self.View.add_edge_window.hide()
        return True

    def on_add_node_window_delete_event(self,widget,event):
        self.View.add_node_window.hide()
        return True

    def on_fichierdialogue_destroy(self,widget,event):
        self.View.fichierdialogue.hide()
        return True

    def on_modify_node_window_delete_event(self,widget,event):
        self.View.modify_node_window.hide()
        return True

    def on_modify_edge_window_delete_event(self,widget,event):
        self.View.modify_edge_window.hide()
        return True

    def on_aboutdialog_chronograph_destroy(self,widget,event):
        self.View.aboutchronomap.hide()
        return True

    def on_new_graph_delete_event(self,widget,event):
        self.View.new_graph.hide()
        return True

    def on_import_delete_event(self,widget,event):
        self.View.importfile.hide()
        return True

    def on_setting_cursor_destroy(self,widget,event):
        self.View.setting_cursor.hide()
        return True

    def on_date_cursor_destroy(self,widget, event):
        self.View.date_cursor.hide()
        return True

    def on_node_add_weak_link_with_an_edge_destroy(self,widget,event):
        self.View.node_add_weak_link_with_an_edge.hide()
        return True

    def on_weak_link_add_edg_destroy(self,widget,event):
        self.View.edge_add_weak_link.hide()
        return True

    # close window
    def on_close_button_press_event(self,widget,event):
        self.View.on_quit_button_press_event (widget,event)

    def on_right_click_carto(self, caller, click_area, click_position):
        # Close all open Menus

        if click_area == "Node":
            # Open Popup Node
            self.View.node_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
            # print(self.View.popupmenu.is_visible())
        elif click_area == "Edge":
            # Open Popup Edge
            if not self.View.node_menu.is_visible():
                self.View.edge_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
        elif click_area == "Graduation" :
            print("open graduation menu")
            # Open Popup graduation
            self.View.empty_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

        elif click_area == "Empty":
            # Open Popup Empty
            self.View.empty_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

        self.click_coordinates = click_position;

    def on_left_release_carto(self, caller, click_area):

        if click_area == "Drag_Edge_windows":
            print("drag_edga windows")


        elif click_area == "Drag_Node_windows":
            print("Drag_Node_windows")
            #self.View.add_node_window.show_all()

        elif click_area == "Empty":
            print("empty")


    def on_right_click_chrono(self, caller, click_area):
            # Close all open Menus
            if click_area == "Node":
            # Open popup node
                self.View.node_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
            elif click_area == "Empty":
                # open empty menu
                self.View.empty_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
            elif click_area == "Cursor":
                self.View.cursor_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    # Actions Node Menu

    def on_popup_menu_copy_node_activate(self, widget):
        print(self.View.display_Mode)
        if self.View.display_Mode == "carto":
            self.selection = self.View.FdessinCarto.selection[1][0]
            self.copied_node = self.View.FdessinCarto.selection[1][0]
            # self.View.FdessinCarto.copy_node(self.selection)
        else:
            self.selection = self.View.FdessinChrono.selection[1][0]
            self.copied_node = self.View.FdessinChrono.selection[1][0]



    def on_popup_menu_edit_node_activate(self, widget):
        if self.View.FdessinCarto.selection == (None,None) and self.View.FdessinChrono.selection:
            print("on edite node activate Editing Chrono node")
            print(self.View.FdessinChrono.selection[1][0])
            self.View.modify_node_window.show_all()

            # reinit variable
            self.View.FdessinChrono.selection = (None, None)

        elif self.View.FdessinCarto.selection:
            print("on edite node activate Edite Carto node")
            print(self.View.FdessinCarto.selection)
            print(self.View.FdessinCarto.selection[1][0])
            self.View.modify_node_window.show_all()



    def on_popup_menu_delete_node_activate(self,widget):
        '''a corriger'''

        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK_CANCEL,
                                   "Delete nodes?")
        #set_transient parent for dialog
        dialog.set_transient_for(self.View.mainWindow)

        dialog.format_secondary_text("Do you really want to delete this node? This node will also be both deleted on the display chronology and cartography.")
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            dialog.hide()

            if self.View.display_Mode == "carto":
                node2remove = self.View.FdessinCarto.selection[1][0]
            elif self.View.display_Mode == "chrono":
                node2remove = self.View.FdessinChrono.selection[1][0]

            # Deletes the node from the controller
            self.View.controller.delete_evenement(node2remove)


            # Update
            self.View.redraw()

            #update listsore
            self.View.clear_liststore()
            self.View.create_liststore()
            self.View.SWViewListStore.show_all()


        elif response == Gtk.ResponseType.CANCEL:
            dialog.hide()


    def on_weak_link_node1_activate(self,widget):
        self.View.node_add_weak_link_with_an_edge.show_all()

# Actions Edge Menu

    def on_edit_edge_activate(self, widget):
        self.View.modify_edge_window.show_all()
        #a modifier

    def on_delete_edge_activate(self, widget):
        #print(self.View.FdessinCarto.selection[1])
        edgetreeiter = self.View.edge_liststore.get_iter_first()
        edge2remove = self.View.FdessinCarto.selection[1]

        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK_CANCEL,
                                   "Delete edges?")
        # set_transient parent for dialog
        dialog.set_transient_for(self.View.mainWindow)

        dialog.format_secondary_text("Do you really want to delete this edge?")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dialog.hide()
            self.View.FdessinCarto.delete_edge_on_click(edge2remove)
            self.View.canvasCarto.draw()
            self.View.canvasChrono.draw()
            self.View.sw.show_all()



            while self.View.edge_liststore[edgetreeiter][1] != edge2remove[0].title :
                if edgetreeiter == None:
                    return True
                else:
                    edgetreeiter = self.View.edge_liststore.iter_next(edgetreeiter)
            self.View.edge_liststore.remove(edgetreeiter)

        elif response == Gtk.ResponseType.CANCEL:
            dialog.hide()





    def on_weak_link_edge_activate(self, dwidget):
        self.View.edge_add_weak_link.show_all()

# Actions Empty Menu

    def on_paste_node_activate(self, widget):
        if not self.copied_node:
            dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                                       "You have to copy a node before")
            dialog.set_transient_for(self.View.mainWindow)
            dialog.run()
        else :
            node = self.copied_node
            #create node
            new_node = self.View.controller.create_evenement(str(self.copied_node.title),
                                             self.View.model.string_from_numdate(int(self.copied_node.start_time)),
                                             self.View.model.string_from_numdate(int(self.copied_node.end_time)),
                                             str(self.copied_node.node_group),
                                             str(self.copied_node.description),
                                             str(self.copied_node.attachment_list))

            # Updates position of the new node
            dict_changedata = {}
            dict_changedata['drawing'] = {}
            dict_changedata['drawing']['x'] = self.click_coordinates[0]
            dict_changedata['drawing']['y'] = self.click_coordinates[1]

            self.View.controller.modify_evemenement(new_node,**dict_changedata)

            self.View.node_liststore.append([str(node.title),
                                             self.View.model.string_from_numdate(int(node.start_time)),
                                             self.View.model.string_from_numdate(int(node.end_time)),
                                             str(node.node_group),
                                             str(node.description),
                                             str(node.attachment_list)])
            self.View.SWViewListStore.show_all()

        self.View.redraw()
        self.selection = None



    def on_create_node_activate(self, widget):
        self.View.add_node_window.show_all()

    def on_display_setting_activate(self, widget):
        #print("show")
        self.View.display_settings.show_all()

    def on_subplot_configure_clicked (self,widget):
        print(self.View.display_Mode)
        if self.View.display_Mode == "carto":
            self.configure_subplots()
        elif self.View.display_Mode == "chrono":
            self.configure_subplots_chrono()

    def configure_subplots(self):
        '''
        Configure subplots
        '''

        toolfig = Figure(figsize=(6,3))
        canvas = self._get_canvas(toolfig)
        toolfig.subplots_adjust(top=0.9)
        tool =  SubplotTool(self.View.FdessinCarto.canvas.figure, toolfig)

        w = int (toolfig.bbox.width)
        h = int (toolfig.bbox.height)


        window = Gtk.Window()
        try:
            window.set_icon_from_file(window_icon)
        except (SystemExit, KeyboardInterrupt):
            # re-raise exit type Exceptions
            raise
        except:
            # we presumably already logged a message on the
            # failure of the main plot, don't keep reporting
            pass
        window.set_title("Subplot Configuration Tool")
        window.set_default_size(w, h)
        vbox = Gtk.Box()
        vbox.set_property("orientation", Gtk.Orientation.VERTICAL)
        window.add(vbox)
        vbox.show()

        canvas.show()
        vbox.pack_start(canvas, True, True, 0)
        window.show()

    def _get_canvas(self, fig):
        return self.View.FdessinCarto.canvas.__class__(fig)

# Actions cursor menu

    def on_hide_cursor_cursormenu_activate(self,widget):
        self.View.FdessinChrono.ly.set_visible(False)
        self.View.canvasChrono.draw()
        self.View.sw.show_all()

    def on_place_cursor_activate(self,widget):
        pass

#Actions graduation menu

    def on_place_cursor_here_activate(self):
        pass

    def on_subplot_configure1_activate(self):
        self.configure_subplots_chrono()

    def configure_subplots_chrono(self):
        '''
        Configure subplots
        '''

        toolfig = Figure(figsize=(6,3))
        canvas = self._get_canvas_chrono(toolfig)
        toolfig.subplots_adjust(top=0.9)
        tool =  SubplotTool(self.View.FdessinChrono.canvas.figure, toolfig)

        w = int (toolfig.bbox.width)
        h = int (toolfig.bbox.height)


        window = Gtk.Window()
        try:
            window.set_icon_from_file(window_icon)
        except (SystemExit, KeyboardInterrupt):
            # re-raise exit type Exceptions
            raise
        except:
            # we presumably already logged a message on the
            # failure of the main plot, don't keep reporting
            pass
        window.set_title("Subplot Configuration Tool")
        window.set_default_size(w, h)
        vbox = Gtk.Box()
        vbox.set_property("orientation", Gtk.Orientation.VERTICAL)
        window.add(vbox)
        vbox.show()

        canvas.show()
        vbox.pack_start(canvas, True, True, 0)
        window.show()

    def _get_canvas_chrono(self, fig):
        return self.View.FdessinChrono.canvas.__class__(fig)

    def on_hide_cursor_activate(self):
        self.View.FdessinChrono.ly.set_visible(False)
        self.View.canvasChrono.draw()
        self.View.sw.show_all()

    def on_display_cursor_activate(self):
        self.View.FdessinChrono.ly.set_visible(True)
        self.View.canvasChrono.draw()
        self.View.sw.show_all()



    # Signal of fichierdialogue

    def on_select_file_clicked(self,widget):
        self.file_name_activate = True
        self.file_name = self.View.fichierdialogue.get_filename()
        #print(self.charge_graph_activate)
        if self.charge_graph_activate == True :
            self.View.new_graph.show_all()
        self.View.fichierdialogue.hide()

    def on_close_file_clicked(self,widget):
        self.View.fichierdialogue.hide()
        return True

    def on_mainFigure_button_press_event(self,widget,event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            #if self.View.display_mode == "Carto":
                # Ask to FdessinCarto si c'est un noeud
                # Elif ask to FdessinCarto si c'est un edge
                # Else Empty area
            #self.View.popupmenu.popup(None, None, None, None, event.button, event.time)
            return True # event has been handled

# Signal create new graph

    def on_ok_clicked(self,widget):
        print("activate on ok")
        self.graph_name = self.View.new_graph_name.get_text()
        self.View.new_graph.hide()
        if self.charge_graph_activate == True:
            self.View.controller.import_graph_xml(self.file_name,self.graph_name)
            self.View.redraw()
            self.charge_graph_activate = False
        elif self.export_graph_activate == True:
            self.View.controller.export_loaded_graph_xml(self.graph_name + ".xml")
            self.View.redraw()
        else:
            self.View.controller.create_new_graph(self.graph_name)
            self.View.redraw()

        #refresh window
        self.View.sw.show_all()

        #reinit file
        self.graph_name = None
        self.file_name = None
        self.file_name = None

    def on_cancel_clicked(self,widget):
        self.View.new_graph.hide()
        return True

#Signal for charging a graph

    def charge_graph_activate_cb(self,widget):
        self.View.importfile.show_all()

    def on_new_clicked(self,widget):
        self.View.importfile.hide()
        self.View.new_graph.show_all()


    def on_change_clicked(self,widget):
        #print(self.View.model[self.View.treeiter][0])
        # type string
        self.file_name = self.View.model[self.View.treeiter][0]
        self.View.clear_liststore()
        self.View.controller.load_graph(self.file_name)
        self.View.redraw()

        #change list store

        self.View.create_liststore()


        #renew windows
        self.View.SWViewListStore.show_all()
        self.View.sw.show_all()
        self.View.importfile.hide()

        #reinit self.file_name
        self.file_name = None

#signal for export graph
    def on_export_activate(self,widget):
        self.export_graph_activate = True
        self.View.new_graph.show_all()


    def on_delete_evenement(self, caller, node):
        print("deleted %s" %node)
        print(caller)
        print(node.title,node.start_time,node.end_time,
                                                  node.node_group,
                                                  node.description,
                                                  node.attachment_list)

        #init
        treeiter = self.View.node_liststore.get_iter_first()

        while self.View.node_liststore[treeiter][0] != node.title :
            if treeiter == None:
                return True
            else:
                treeiter = self.View.node_liststore.iter_next(treeiter)

        if not treeiter :
            return True
        else :
            self.View.node_liststore.remove(treeiter)


    def on_delete_graph_clicked(self,widget):
        self.file_name = self.View.model[self.View.treeiter][0]
        #print(self.file_name)
        self.View.controller.delete_graph(self.file_name)
        self.View.graph_liststore.remove(self.View.treeiter)
        self.View.create_graph_list_store()
        self.View.graphliststoreView.show_all()
        self.View.sw.show_all()


        # reinit self.file_name
        self.file_name = None

#signal for cursor settings
    def on_setting_validation_clicked(self):
        '''Display cusrsor setting :return: None '''
        cursor_step = self.View.interface.get_object('cursor_step').get_text()
        cursor_granularity = self.View.interface.get_object('cursor_granularity').get_text()

    def on_cancel_cursor_clicked(self):
        self.View.setting_cursor.hide()
        return True

#Signal for the window place the cursor

    def on_cancel_windows_place_cursor_clicked(self):
        self.View.date_cursor.hide()
        return True

    def on_validate_place_cursor_clicked(self):
        '''Place the cursor on the selection of the event'''
        date_place_cursor = self.View.interface.get_object("date_place_cursor").get_text()

#signal for weak link add node
    def on_validate_weak_link_node_clicked(self,widget):
        edge = None
        name_edge_to_strengthen = self.View.interface.get_object('name_edge_to_strengthen').get_text()
        entry_description_weak_link_node = self.View.interface.get_object('entry_description_weak_link_node').get_text()
        #print(self.View.FdessinCarto.selection[1][0])
        self.View.edgelist = self.View.controller.get_edge_list()


        for i in self.View.edgelist:
            edge_prop = self.View.controller.edge_data(i[0], i[1])
            if edge_prop['label'] == name_edge_to_strengthen:
                edge = i
                print(self.View.FdessinChrono.selection[1])
                if self.View.display_Mode == "carto" :
                    self.View.controller.create_weak_link( i[0], i[1], self.View.FdessinCarto.selection[1][0])
                else :
                    self.View.controller.create_weak_link(i[0], i[1], self.View.FdessinChrono.selection[1][0])
                break
        for i in self.View.edge_liststore:
            if (i[1] == edge[0].title) and (i[2] == edge[1].title):
                i[5] = entry_description_weak_link_node


        self.View.node_add_weak_link_with_an_edge.hide()
        self.View.SWViewListStore.show_all()

    def on_cancel_weak_link_node_clicked(self,widget):
        self.View.node_add_weak_link_with_an_edge.hide()
        return True

#signal for weak link add edge
    def on_validate_weak_link_edge_clicked(self,widget):

        node_entrance_weak_link = self.View.interface.get_object('node_entrance_weak_link').get_text()
        description_entrance_weak_link_edge = self.View.interface.get_object('description_entrance_weak_link_edge').get_text()
        #print("selection %s" %self.View.FdessinCarto.selection[1])
        # update nodelist
        self.View.nodelist = self.View.controller.get_node_list()

        for node in self.View.nodelist:
            if node.title == node_entrance_weak_link:
                self.View.controller.create_weak_link(self.View.FdessinCarto.selection[1][0],self.View.FdessinCarto.selection[1][1],node )
                break
        for i in self.View.edge_liststore:
            if (i[1] == self.View.FdessinCarto.selection[1][0].title) and (i[2] == self.View.FdessinCarto.selection[1][1].title):
                i[5] = description_entrance_weak_link_edge

        self.View.edge_add_weak_link.hide()
        self.View.SWViewListStore.show_all()

    def on_cancel_weak_link_edge_clicked(self,widget):
        self.View.edge_add_weak_link.hide()
        return True

#Signal for fichier dialogue
    def on_export_cancel_activate(self,widget):
        self.View.export_dialog.hide()
