import gi
gi.require_version('Gtk', '3.0')

from gi.repository import GObject

import matplotlib.lines as lines
from pylab import *
import networkx as nx
import numpy as np
import time



class DrawCartoMap(GObject.GObject):

    __gsignals__ = {
        'delete_evenement': (GObject.SIGNAL_RUN_FIRST, None,
                      (object,)),
        'rclick_canvas': (GObject.SIGNAL_RUN_FIRST, None,
                      (str, object,)),
        'lrelease_canvas': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'selection_change': (GObject.SIGNAL_RUN_FIRST, None,
                             (object,)),
        'node_position_change': (GObject.SIGNAL_RUN_FIRST, None,
                              (object, object,))
    }

    def __init__(self, ax, controller, node = None):
        # Init GObject Connection
        GObject.GObject.__init__(self)

        # Global View

        # Global event
        self.event = None

        # Global controller
        self.controller = controller

        # Global model
        self.model = self.controller.model

        # Global Graph
        self.G = self.controller.total_graph()

        # Global Axis
        self.ax = ax

        # Global figure
        self.fig = self.ax.get_figure()

        # Gloal canvas
        self.canvas = self.ax.get_figure().canvas

        # Global position of nodes
        self.pos = None

        # Global node list
        self.nodelist = self.controller.get_node_list()

        # Gloabl edge list
        self.edgelist = self.controller.get_edge_list()

        # Global nodecollection
        self.nodecollection = None

        # Global edgecollection
        self.edgecollection = None

        # Global datanode
        self.datanode = None

        # Global dataedge
        self.dataedge = None

        # Global colorlistnode
        self.colorlistnode = []

        # Global colorlistedge
        self.colorlistedge = []

        #Global selection
        self.temp_selection = (None, None)
        self.selection = (None, None)


        # variable related to Drag_actions
        self.drag_time = 0

        self.press = []

        self.drag_press = []

        self.xdrag = 0
        self.ydrag = 0

        # event data
        self.xdata = 0
        self.ydata = 0

        # select event
        self.node1 = None
        self.node2 = None
        self.event = None
        self.node2remove = node

        # copy transference area
        self.copy_node_selection = None

        # Global mpl functions
        self.nodepress = None
        self.noderelease = None
        self.nodemotion = None
        self.deletenodepress = None
        self.deletenoderelease = None
        self.copynode_onpress = None
        self.copynode_onrelease = None
        self.deleteedge_press = None
        self.deleteedge_release = None
        self.ChangeEdgeColor_press = None
        self.ChangeEdgeColor_release = None
        self.deletenodepress_node2remove = None
        self.deletenoderelease_node2remove = None

        self.pan_active = False
        self.drag_active = False

        self.build_popups()
        # self.canvas.mpl_connect('button_press_event', event)


################################# ACTIONS ######################################

    # Detect - Select Element
    def Detect(self):
        '''
        Picks an object to determine the element that was selected
        self.event holds the actual clicked object
        self.selected holds the last selected object
        '''
        def on_click(event):
            # Global node list update
            self.nodelist = self.controller.get_node_list()
            # Gloabl edge list update
            self.edgelist = self.controller.get_edge_list()

            x = event.xdata
            y = event.ydata

            self.node1 = None
            self.node2 = None

            # Erase actual data
            self.event = None
            self.temp_selection = (None,None)


            # if we click on a node
            for node in self.pos:
                if (self.pos[node][0] - 0.05 <= event.xdata <= self.pos[node][0] + 0.05) and (
                            self.pos[node][1] - 0.05 <= event.ydata <= self.pos[node][1] + 0.05):
                    self.event = [node]

                    self.temp_selection = ("node", self.event)

                    if (event.button == 3):
                        self.selection = self.temp_selection
                        self.emit('selection_change', self.selection)
                        self.emit("rclick_canvas", "Node", (x,y))
            if self.temp_selection[0] == None:
                for edge in self.edgelist:
                    # print(self.controller.edge_data(edge[0],edge[1]))
                    a = (edge[0].y - edge[1].y) / (edge[0].x - edge[1].x)
                    b = edge[0].y - a * edge[0].x
                    b1 = b + 0.1
                    b2 = b - 0.1
                    infx = min(edge[0].x, edge[1].x)
                    supx = max(edge[0].x, edge[1].x)
                    infy = min(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)
                    supy = max(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)

                    # get function a and b : y = ax + b
                    # we create a rectangle around the edge
                    if (infx < event.xdata < supx) and (infy < event.ydata < supy):
                        self.node1 = edge[0]
                        self.node2 = edge[1]
                        self.event = [self.node1, self.node2]

                        self.temp_selection = ("edge", self.event)

                        if (event.button == 3):
                            self.selection = self.temp_selection
                            self.emit('selection_change', self.selection)
                            self.emit("rclick_canvas", "Edge", (x,y))

            if (event.button == 3) and self.event == None:
                #print(self.event,self.selection)
                click_data = [event.xdata, event.ydata]
                #self.temp_selection = ("empty",event)

                # self.emit('selection_change',))
                self.emit("rclick_canvas", "Empty", (x,y))

        def on_release(event):
            self.selection = self.temp_selection
            self.emit('selection_change', self.selection)

        self.canvas.mpl_connect('button_press_event', on_click)
        self.canvas.mpl_connect('button_release_event', on_release)



    # Pan View
    def pan_drag(self):

        def pan_press(event):
            # update self.datanode
            self.datanode = self.nodecollection.get_offsets()
            x0, y0 = event.xdata, event.ydata
            self.press = [x0, y0]
            self.pan_active = True


        def pan_motion(event):
            '''
            Pan canvas if not on a node
            '''
            # Press failed
            if not self.press:
                return None

            # Click on something different
            if self.temp_selection[0] != None:
                return None

            # Out of bounds
            if not event.xdata or not event.ydata:
                return None

            # Left click
            if event.button != 1:
                return None

            xpress, ypress = self.press
            print(self.press)

            dx = event.xdata - xpress
            dy = event.ydata - ypress


            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Variation
            nX = dx / 2
            nY = dy / 2

            self.ax.set_xlim([- nX + cur_xlim[0],
                              - nX + cur_xlim[1]])
            self.ax.set_ylim([- nY + cur_ylim[0],
                              - nY + cur_ylim[1]])

            self.canvas.draw()

        def pan_release(event):
            self.press = []
            self.pan_active = False
            self.canvas.draw()

        self.canvas.mpl_connect('button_press_event', pan_press)
        self.canvas.mpl_connect('motion_notify_event', pan_motion)
        self.canvas.mpl_connect('button_release_event', pan_release)


    # Pan View Keyboard
    def pan_keyboard(self):
        '''
        Moves the plot around with the keyboard arrows
        '''

        pan_multiplier = 0.05

        def pan_keypress(event):
            #print(event.key)
            # TODO Si aucun noeud est selectionne
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            if event.key == 'a':
                left_movement = (cur_xlim[1] - cur_xlim[0]) * pan_multiplier
                self.ax.set_xlim([left_movement + cur_xlim[0],
                                  left_movement + cur_xlim[1]])

            if event.key == 'z':
                right_movement = (cur_xlim[1] - cur_xlim[0]) * pan_multiplier
                self.ax.set_xlim([- right_movement + cur_xlim[0],
                                  - right_movement + cur_xlim[1]])

            if event.key == 'e':
                up_movement = (cur_ylim[1] - cur_ylim[0]) * pan_multiplier
                self.ax.set_ylim([- up_movement + cur_ylim[0],
                                  - up_movement + cur_ylim[1]])

            if event.key == 'r':
                down_movement = (cur_ylim[1] - cur_ylim[0]) * pan_multiplier
                self.ax.set_ylim([+ down_movement + cur_ylim[0],
                                  + down_movement + cur_ylim[1]])
            self.canvas.draw()

        self.canvas.mpl_connect('key_press_event', pan_keypress)

    # Drag node
    def drag_node(self):

        # nodeoffsets = 0
        # edgeoffsets = 0
        # edge_index_list = []
        # node_index = 0

        def drag_press(event):

            self.drag_press = [event.xdata, event.ydata]
            # self.edgeoffsets = self.edgecollection.get_segments()
            # self.nodeoffsets = self.nodecollection.get_offsets()
            # self.node_b = False
            # self.edge_index_list = False
            self.position_changed = False
            self.dragged_node = None
            self.defX = None
            self.defY = None
            self.drag_active = True

        def drag_motion(event):

            #global nodeoffsets, edgeoffsets, node_index, edge_index_list

            if not self.drag_press:
                return None

            # Aucun noeud selected
            if not self.temp_selection[0] == 'node':
                return None

            if not event.button == 1:
                return None

            # if not (self.node_b and self.edge_index_list):
            #     # Node index
            #     self.node_b = self.nodelist.index(self.temp_selection[1][0])
            #     # All edges that have this node
            #     self.edge_index_list = []
            #     for edge_index, edge in enumerate(self.edgelist):
            #         a = False
            #         b = False
            #         if edge[0] == self.temp_selection[1][0]:
            #             a = True
            #         if edge[1] == self.temp_selection[1][0]:
            #             b = True
            #         self.edge_index_list.append((edge_index, a, b))

            xpress, ypress = self.drag_press

            dx = event.xdata - xpress
            dy = event.ydata - ypress

            self.dragged_node = self.temp_selection[1][0]

            self.drag_index = self.nodelist.index(self.dragged_node)

            nX = self.dragged_node.d_posx + dx
            nY = self.dragged_node.d_posy + dy

            # self.nodeoffsets[self.drag_index] = array([nX, nY])

            # for edge_tuple in self.edge_index_list:
            #     if edge_tuple[1]:
            #         self.edgeoffsets[edge_tuple[0]] = array( [[nX, nY], self.edgeoffsets[edge_tuple[0]][1]])
            #     if edge_tuple[2]:
            #         self.edgeoffsets[edge_tuple[0]] = array( [ self.edgeoffsets[edge_tuple[0]][0] , [nX, nY]])
            #
            # self.nodecollection.set_offsets(self.nodeoffsets)
            # self.edgecollection.set_segments(self.edgeoffsets)


            self.pos[self.dragged_node][0] = nX
            self.pos[self.dragged_node][1] = nY
            self.defX = nX
            self.defY = nY


            # dict_changedata = {}
            # dict_changedata['drawing'] = {}
            #
            # dict_changedata['drawing']['x'] = nX
            # dict_changedata['drawing']['y'] = nY
            #
            #
            # self.controller.modify_evemenement(node_index, **dict_changedata)

            self.canvas.draw()
            self.clear_all()
            self.draw_cartograph(False)
            self.position_changed = True


        def drag_release(event):
            # Send signal to view to update position
            if self.position_changed:
                self.emit('node_position_change', self.dragged_node, [self.defX, self.defY])
                self.full_redraw()
                self.position_changed = False;
            self.drag_press = []
            self.dragged_node = None
            self.drag_active = False


        self.nodepress = self.canvas.mpl_connect('button_press_event', drag_press)
        self.noderelease = self.canvas.mpl_connect('button_release_event', drag_release)
        self.nodemotion = self.canvas.mpl_connect('motion_notify_event', drag_motion)

    # Draw on drag
    def drag_create_edge(self):
        # TODO All
        # OnClick - Detects if the click was in a circle outside a node
        # OnMotion - Create a line between the node and the click
        # OnRelease - Detect the area of the release
        #     If node - emit - Create edge
        #     If edge - emit - Create weak link
        #     If empty - Do nothing.
        pass

    # Popup edge
    def edge_popup_mouse_over(self):

        def on_motion(event):
            # Node gets priority over edges
            if self.pan_active:
                return None

            if self.popup.get_visible():
                self.popupedge.set_visible(False)
                return None

            if not self.popup.get_visible():

                x = event.xdata
                y = event.ydata

                visibility_changed = False
                should_be_visible = None
                self.popupedge.set_visible(False)
                node1 = None

                for edge in self.edgelist:
                    a = (edge[0].y - edge[1].y) / (edge[0].x - edge[1].x)
                    b = edge[0].y - a * edge[0].x
                    b1 = b + 0.01
                    b2 = b - 0.01
                    infx = min(edge[0].x, edge[1].x)
                    supx = max(edge[0].x, edge[1].x)
                    infy = min(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)
                    supy = max(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)

                    if (infx < event.xdata < supx) and (infy < event.ydata < supy):
                        should_be_visible = True
                        node1 = edge[0]
                        node2 = edge[1]
                        break

                if should_be_visible != self.popupedge.get_visible():
                    visibility_changed = True
                    # print(should_be_visible,self.popupedge.get_visible(),node1)
                    if node1:
                        # print('jaffiche le popup')
                        self.popupedge.set_text('Titre : %s\nDescription: %s \nFichier attache: %s ' % (
                        self.controller.edge_data(node1, node2)['label'],
                        self.controller.edge_data(node1, node2)['description'],
                        self.controller.edge_data(node1, node2)['attachment_list']))
                        self.popupedge.set_position((x, y))

                        # TODO: Verify if the box goes out of the canvas and re

                    self.popupedge.set_visible(should_be_visible)

                if visibility_changed:
                    #time.sleep(1)
                    self.canvas.draw()

        self.canvas.mpl_connect('motion_notify_event', on_motion)

    # Popup node
    def node_popup_mouse_over(self):

        def on_motion(event):
            if self.pan_active:
                return None

            if self.drag_active:
                return None
            #print(time.time())

            x = event.xdata
            y = event.ydata

            visibility_changed = False
            should_be_visible = None
            self.popup.set_visible(False)
            actual_node = None
            #print("Hello world")
            # update self.pos
            self.pos = self.controller.get_position()

            # print(self.pos)
            for node in self.pos:

                if ((self.pos[node][0] - 0.05 <= event.xdata <= self.pos[node][0] + 0.05) and
                        (self.pos[node][1] - 0.05 <= event.ydata <= self.pos[node][1] + 0.05)):
                    should_be_visible = True
                    # print("non")
                    # print(should_be_visible,popup.get_visible())
                    actual_node = node
                    break

            if should_be_visible != self.popup.get_visible():
                visibility_changed = True

                # print(should_be_visible,self.popup.get_visible(),actual_node)
                if actual_node:
                    # print("yes")
                    self.popup.set_text(
                        'Titre : %s\ndate du debut: %s -date de fin : %s \ngroupe du noeud: %s, description: %s, fichier attache: %s ' % (
                        actual_node.title, self.model.string_from_numdate(int(actual_node.start_time)), self.model.string_from_numdate(int(actual_node.end_time)), actual_node.node_group,
                        actual_node.description, actual_node.attachment_list))
                    self.popup.set_position((x, y))

                self.popup.set_visible(should_be_visible)

            if visibility_changed:
                #time.sleep(1)
                self.canvas.draw()

        self.canvas.mpl_connect('motion_notify_event', on_motion)

    # Change stuff on selection
    def do_selection_change(self, selection):

        if selection[0] == "edge":
            # Change edge color
            self.change_node_color(None)
            self.change_edge_color(selection[1][0], selection[1][1])

        elif selection[0] == "node":
            # Change color node
            self.change_edge_color(None)
            self.change_node_color(selection[1][0])

        else:
            # Erase all colors
            self.change_edge_color(None)
            self.change_node_color(None)


    def change_node_color(self, node):

        # Colors definition
        red = [1, 0, 0, 1]
        dark = [0, 0, 0, 1]
        blue = [0, 0.74, 1, 1]

        self.colorlistnode = []

        # update self.datanode
        if self.datanode is None:
            # draw nodes return nodecollection
            self.nodecollection = nx.draw_networkx_nodes(self.controller.total_graph(), self.pos, ax=self.ax)
            # get nodes position
            self.datanode = self.nodecollection.get_offsets()

        if len(self.datanode) == 0:  # no nodes!
            return None

        if node == None:
            for i, node_pos in enumerate(self.datanode):
                self.colorlistnode.append(red)
        else:
            for node_pos in self.datanode:
                if node_pos[0] == node.d_posx and node_pos[1] == node.d_posy:
                    self.colorlistnode.append(blue)
                else:
                    self.colorlistnode.append(red)

        self.nodecollection.set_facecolors(self.colorlistnode)

        # Colors changed redraw canvas
        self.canvas.draw()

    def change_edge_color(self, node1, node2 = None):

        yellow = np.array([1, 1, 0, 1])
        black = np.array([0, 0, 0, 1])

        self.colorlistedge = []

        # update self.edgenode
        if self.edgecollection is None:
            # draw edges return edgecollection
            self.edgecollection = nx.draw_networkx_edges(self.controller.total_graph(), self.pos, ax=self.ax)

        if len(self.edgelist) == 0:  # no nodes!
            return None

        if node1 == None or node2 == None:
            for edge in self.edgelist:
                self.colorlistedge.append(black)
        else:
            for edge in self.edgelist:
                if edge[0] == node1 and edge[1] == node2:
                    self.colorlistedge.append(yellow)
                else:
                    self.colorlistedge.append(black)

        self.edgecollection.set_edgecolors(self.colorlistedge)
        self.canvas.draw()

    # Settings
    def display_grid(self):
        '''
        Shows a grid.
        '''
        self.ax.grid(True)

    def hide_grid(self):
        '''
        hide grid
         '''

        self.ax.grid(False)

    def resetplot(self):
        self.ax.cla()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.grid(True)
        self.canvas.draw()


    # General functions
    def draw_cartograph(self, fullOperation = True):
        '''
        Redraws the plot completly. It is computer intensive.

        :arg fullOperation: Optional. If false, doesnt update the pos and node
        values.

        '''

        # update graph
        self.G = self.controller.total_graph()

        if fullOperation:
        # update position
            self.pos = self.controller.get_position()
            for node in self.pos:
                node.x = self.pos[node][0]
                node.y = self.pos[node][1]

            # update data of node
            self.nodelist = self.controller.get_node_list()

            # update data edge
            self.edgelist = self.controller.get_edge_list()

            self.build_popups()

        # draw nodes return nodecollection
        self.nodecollection = nx.draw_networkx_nodes(self.controller.total_graph(), self.pos, ax=self.ax)

        if self.nodecollection is None:
            self.datanode = []
        # get nodes position
        if self.datanode is None:
            self.datanode = self.nodecollection.get_offsets()

        # draw edges return edgecollection
        self.edgecollection = nx.draw_networkx_edges(self.controller.total_graph(), self.pos, ax=self.ax)

        if self.edgecollection is None:
            self.dataedge = []

        # get edges position
        if self.dataedge is None:
            self.dataedge = self.edgecollection.get_offsets()

        # display canvas
        self.canvas.draw()


    def clear_all(self):
        '''
        Clear the screen and resets the plot to the same axes
        '''
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        self.ax.cla()
        self.ax.set_xlim(cur_xlim)
        self.ax.set_ylim(cur_ylim)

        # self.connect_functions_Carto()


    def full_redraw(self):
         self.clear_all()
         self.draw_cartograph()

    # OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################
# OLD FUNCTIONS ##################################################################################


    '''attente'''

    # def wait(self):
    #
    #     def on_motion(event):
    #         x = event.xdata
    #         y = event.ydata
    #         popup = self.ax.text(x, y, '', style='italic', bbox={'facecolor': 'y', 'alpha': 0.5, 'pad': 10})
    #         visibility_changed = False
    #         popup.set_visible(visibility_changed)
    #         # update local position
    #         self.pos = self.controller.get_position()
    #
    #         for node in self.pos:
    #             if (self.pos[node][0] - 0.05 <= event.xdata <= self.pos[node][0] + 0.05) and (
    #                         self.pos[node][1] - 0.05 <= event.ydata <= self.pos[node][1] + 0.05):
    #                 # print(str(node.title),str(node.start_time),str(node.end_time),str(node.node_group),str(node.description),str(node.attachment_list))
    #
    #                 popup.set_text(
    #                     'Titre : %s, Date du debut: %s, date de fin : %s, groupe du noeud: %s, description: %s, fichier attache: %s ' % (
    #                     node.title, node.start_time, node.end_time, node.node_group, node.description,
    #                     node.attachment_list))
    #                 visibility_changed = True
    #                 popup.set_visible(visibility_changed)
    #             else:
    #                 visibility_changed = False
    #                 popup.set_visible(visibility_changed)
    #         if visibility_changed:
    #             self.canvas.draw()
    #
    #     self.wait = self.canvas.mpl_connect('motion_notify_event', on_motion)
    #
    # '''delete one node on click'''
    # def delete(self,event):
    #     compteur = 0
    #     [x0, y0] = [0, 0]
    #
    #     for i, node in enumerate(self.pos):
    #         if (self.pos[node][0] - 0.05 <= event.xdata <= self.pos[node][0] + 0.05) and (
    #                     self.pos[node][1] - 0.05 <= event.ydata <= self.pos[node][1] + 0.05):
    #             self.node2remove = node
    #             # print(self.node2remove)
    #             compteur = i
    #             [x0, y0] = [self.pos[node][0], self.pos[node][1]]
    #             self.controller.delete_evenement(self.node2remove)
    #             self.emit("delete_evenement", node)
    #
    #     if self.node2remove:
    #         self.clear_all()
    #         self.draw_cartograph()
    #     return self.node2remove
    #     #print("after clear %s" % self.node2remove)
    #
    # def delete_release(self,event):
    #     # self.draw_cartograph()
    #     self.canvas.draw()
    #     # return self.node2remove
    #     #print("delete-release %s" % self.node2remove)
    #
    # def Delete_Node(self):
    #     a = self.delete
    #     self.deletenodepress = self.canvas.mpl_connect('button_press_event', self.delete)
    #     self.deletenoderelease = self.canvas.mpl_connect('button_release_event', self.delete_release)
    #     #print(a)
    #
    # def disconnect_Delete_Node(self):
    #     self.canvas.mpl_disconnect(self.deletenodepress)
    #     self.canvas.mpl_disconnect(self.deletenoderelease)
    #
    # def delete_release_node2remove(self,event):
    #     # self.draw_cartograph()
    #     self.canvas.draw()
    #     # return self.node2remove
    #     #print("delete-release %s" % self.node2remove)
    #
    # # Delete node
    # def Delete_Node_node2remove(self, node):
    #     '''
    #     Erase a node from the plot.
    #     '''
    #
    #     if node:
    #         self.controller.delete_evenement(node)
    #         self.emit("delete_evenement", node)
    #         self.clear_all()
    #         self.draw_cartograph()
    #     else :
    #         return True
    # def Delete_Node_node2remove(self):
    #
    #     self.deletenodepress_node2remove = self.canvas.mpl_connect('button_press_event', self.delete_node2remove)
    #     self.deletenoderelease_node2remove = self.canvas.mpl_connect('button_release_event', self.delete_release_node2remove)
    #
    # def disconnect_Delete_Node_node2remove(self):
    #     self.canvas.mpl_disconnect(self.deletenodepress_node2remove)
    #     self.canvas.mpl_disconnect(self.deletenoderelease_node2remove)
    #
    # '''delete one edge on click'''
    # # Delete edge
    # def Delete_Edge(self):
    #     def delete(event):
    #         Node2remove1 = None
    #         Node2remove2 = None
    #         x = event.xdata
    #         y = event.ydata
    #
    #         for edge in self.edgelist:
    #             # print(self.controller.edge_data(edge[0],edge[1]))
    #             a = (edge[0].y - edge[1].y) / (edge[0].x - edge[1].x)
    #             b = edge[0].y - a * edge[0].x
    #             b1 = b + 0.05
    #             b2 = b - 0.05
    #             infx = min(edge[0].x, edge[1].x)
    #             supx = max(edge[0].x, edge[1].x)
    #             infy = min(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)
    #             supy = max(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)
    #             # get function a and b
    #             # we create a rectangle around the edge
    #             if (infx < event.xdata < supx) and (infy < event.ydata < supy):
    #                 # print("oui, on detecte l'arret")
    #                 Node2remove1 = edge[0]
    #                 Node2remove2 = edge[1]
    #                 self.controller.remove_edge(Node2remove1, Node2remove2)
    #                 break
    #
    #         if Node2remove1:
    #             self.clear_all()
    #             self.draw_cartograph()
    #
    #     def delete_release(event):
    #         self.canvas.draw()
    #
    #     self.deleteedge_press = self.canvas.mpl_connect('button_press_event', self.delete)
    #     self.deleteedge_release = self.canvas.mpl_connect('button_release_event', self.delete_release)
    #
    # def disconnect_Delete_Edge(self):
    #     self.canvas.mpl_disconnect(self.deleteedge_press)
    #     self.canvas.mpl_disconnect(self.deleteedge_release)
    #
    #
    # '''delete Edge when we know which edge to delete'''
    # def delete_edge_on_click(self, edge):
    #     edge2remove = edge
    #     Node2remove1 = edge[0]
    #     Node2remove2 = edge[1]
    #     #print()
    #     self.controller.remove_edge(Node2remove1, Node2remove2)
    #
    #     if Node2remove1:
    #         self.clear_all()
    #         self.draw_cartograph()
    #
    #     self.canvas.draw()


    # '''draw lines from nodes/Edge '''

    # def DrawLines(self):
    #     def on_press(event):
    #         x0 = None
    #         y0 = None
    #         # if the event is on node
    #         for i in self.datanode:
    #             if (i[0] - 0.05 <= event.xdata <= i[0] + 0.05) and (i[1] - 0.05 <= event.ydata <= i[1] + 0.05):
    #                 x0 = i[0]
    #                 y0 = i[1]
    #                 break
    #         # if the event is on edge
    #         for edge in self.edgelist:
    #             # print(self.controller.edge_data(edge[0],edge[1]))
    #             a = (edge[0].y - edge[1].y) / (edge[0].x - edge[1].x)
    #             b = edge[0].y - a * edge[0].x
    #             b1 = b + 0.1
    #             b2 = b - 0.1
    #             infx = min(edge[0].x, edge[1].x)
    #             supx = max(edge[0].x, edge[1].x)
    #             infy = min(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)
    #             supy = max(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)
    #
    #             # get function a and b : y = ax + b
    #             # we create a rectangle around the edge
    #             if (infx < event.xdata < supx) and (infy < event.ydata < supy):
    #                 # print("oui, on detecte l'arret")
    #
    #                 x0 = event.xdata
    #                 y0 = event.ydata
    #                 break
    #
    #         # if the event is not node
    #         if x0 == None:
    #             x0 = 0
    #             y0 = 0
    #
    #         self.press = [x0, y0, event.xdata, event.ydata]
    #         # print("press %s" %self.press)
    #
    #     def on_motion(event):
    #
    #         if not self.press:
    #             return False
    #
    #         x0, y0, xpress, ypress = self.press
    #         # print([x0, y0, xpress, ypress])
    #
    #         if [x0, y0] == [0, 0]:
    #             self.pan_drag()
    #         else:
    #
    #             dx = event.xdata - xpress
    #             dy = event.ydata - ypress
    #
    #             self.xdrag = xpress + dx
    #             self.ydrag = ypress + dy
    #
    #             line1_xs = (x0, self.xdrag)
    #             line1_ys = (y0, self.ydrag)
    #             self.line_artist.set_visible(True)
    #             print(self.line_artist.get_data())
    #             self.line_artist.set_data(line1_xs, line1_ys)
    #             self.xdata = event.xdata
    #             self.ydata = event.ydata
    #             # print(self.xdrag,self.ydrag,event.xdata,event.ydata,x0, y0, xpress, ypress)
    #
    #             self.canvas.draw()
    #
    #     def on_release(event):
    #         for i in self.datanode:
    #             if (i[0] - 0.05 <= event.xdata <= i[0] + 0.05) and (i[1] - 0.05 <= event.ydata <= i[1] + 0.05):
    #                 self.event = [i]
    #
    #                 self.temp_selection = ("node", self.event)
    #
    #                 self.selection = self.temp_selection
    #                 self.emit('selection_change', self.selection)
    #                 self.emit("lrelease_canvas", "Drag_Node_windows")
    #
    #
    #         for edge in self.edgelist:
    #             # print(self.controller.edge_data(edge[0],edge[1]))
    #             a = (edge[0].y - edge[1].y) / (edge[0].x - edge[1].x)
    #             b = edge[0].y - a * edge[0].x
    #             b1 = b + 0.1
    #             b2 = b - 0.1
    #             infx = min(edge[0].x, edge[1].x)
    #             supx = max(edge[0].x, edge[1].x)
    #             infy = min(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)
    #             supy = max(a * min(edge[0].x, edge[1].x) + b1, a * max(edge[0].x, edge[1].x) + b2)
    #
    #             # get function a and b : y = ax + b
    #             # we create a rectangle around the edge
    #             if (infx < event.xdata < supx) and (infy < event.ydata < supy):
    #                 print("oui, on detecte l'arret")
    #
    #                 self.node1 = edge[0]
    #                 self.node2 = edge[1]
    #                 self.event = [self.node1, self.node2]
    #
    #                 self.temp_selection = ("edge", self.event)
    #
    #                 self.selection = self.temp_selection
    #                 self.emit('selection_change', self.selection)
    #                 self.emit("lrelease_canvas", "Drag_Edge_windows")
    #
    #         if self.event == None:
    #             self.emit("lrelease_canvas", "Empty")
    #
    #
    #         #self.clear_all()
    #         self.draw_cartograph()
    #         self.line_artist.set_visible(False)
    #         self.ax.add_line(self.line_artist)
    #         self.press = []
    #         self.node1 = None
    #         self.node2 = None
    #         self.canvas.draw()
    #
    #     self.line_artist = lines.Line2D((0, 0), (0, 0), linewidth=2, color='black')
    #     self.ax.add_line(self.line_artist)
    #     self.line_artist.set_visible(False)
    #     self.canvas.mpl_connect('button_press_event', on_press)
    #     self.canvas.mpl_connect('button_release_event', on_release)
    #     self.canvas.mpl_connect('motion_notify_event', on_motion)

    # # Copy node
    # def copy_node(self, node = None):
    #     '''
    #     Function to put a node into the transference area.
    #
    #     .. todo: integrate with gtk3 clipboard
    #
    #     '''
    #     if not node:
    #         if self.selection:
    #             if self.selection[0] == 'node':
    #                 self.copy_node_selection = self.selection[1][0]
    #             else :
    #                 print("no node")
    #                 return True
    #     else:
    #         self.copy_node_selection = node
    #
    #
    #
    # # Clear selection
    # def clear_copy_node_selection(self):
    #     self.copy_node_selection = None

    # # Paste node
    # def paste_node(self, xpos = False, ypos = False):
    #
    #     print("1st canvas")
    #     print(self.ax.get_figure().canvas)
    #     print(self.ax.get_figure())
    #
    #
    #     self.clear_all()
    #
    #     self.redraw_carto()
    #     print("2nd canvas")
    #     print(self.ax.get_figure().canvas)
    #     print(self.ax.get_figure())
    #     self.connect_functions_Carto()
    #     self.canvas.draw()
    #
    #     #reinit
    #     self.selection = None

    def build_popups(self):
        # Node attibute popup
        self.popup = self.ax.text(0, 0, '', style='italic', bbox={'facecolor': 'y', 'alpha': 0.5, 'pad': 10})

        # Edge attribute popup
        self.popupedge = self.ax.text(0, 0, '', style='italic', bbox={'facecolor': 'y', 'alpha': 0.5, 'pad': 10})

    def connect_functions_Carto(self):
        # MouseFunction Carto

        self.pan_drag()
        self.drag_node()
        self.Detect()
        self.node_popup_mouse_over()
        self.edge_popup_mouse_over()
        self.pan_keyboard()
        self.drag_create_edge()
