import gi
gi.require_version('Gtk', '3.0')
import matplotlib.lines as lines
from pylab import *
import networkx as nx
import numpy as np
import View


'''delete one node on click'''
    def delete(self,event):
        compteur = 0
        [x0, y0] = [0, 0]

        for i, node in enumerate(self.pos):
            if (self.pos[node][0] - 0.05 <= event.xdata <= self.pos[node][0] + 0.05) and (
                        self.pos[node][1] - 0.05 <= event.ydata <= self.pos[node][1] + 0.05):
                self.node2remove = node
                # print(self.node2remove)
                compteur = i
                [x0, y0] = [self.pos[node][0], self.pos[node][1]]
                self.controller.delete_evenement(self.node2remove)
                break

        if self.node2remove:
            self.clear_all()
            self.draw_cartograph()
        return self.node2remove
        #print("after clear %s" % self.node2remove)

    def delete_release(self,event):
        # self.draw_cartograph()
        self.canvas.draw()
        # return self.node2remove
        #print("delete-release %s" % self.node2remove)


    def Delete_Node(self):
        a = self.delete
        self.deletenodepress = self.canvas.mpl_connect('button_press_event', self.delete)
        self.deletenoderelease = self.canvas.mpl_connect('button_release_event', self.delete_release)
        #print(a)


    def disconnect_Delete_Node(self):
        self.canvas.mpl_disconnect(self.deletenodepress)
        self.canvas.mpl_disconnect(self.deletenoderelease)