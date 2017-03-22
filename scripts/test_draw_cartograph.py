# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib.figure import Figure
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import draw_cartograph as D
import Controller as CT
import BasicModel as md



# Initialise plot
'''model using GTK'''
window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)
window.set_default_size(1500, 1500)
window.set_title('TestDrawCartograph')


#Canvas Figure display on networkx
fig = Figure(tight_layout=True)
ax = fig.add_subplot(111)

canvas=FigureCanvas(fig)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
window.add(box)
box.pack_start(canvas,True,True,0)


#Init controller
model = md.Model()
controller=CT.Controller(model)

FdessinCarto=D.DrawCartoMap(ax,controller)

#Create a New graph
FdessinCarto.controller.create_new_graph("GraphChronomap")

nodeA=FdessinCarto.controller.create_evenement("outdated research material", "01-01-2016 00:00:00", "01-02-2016 00:00:00", 1, "BLAH BLAH BLAH", "http://")
nodeB= FdessinCarto.controller.create_evenement("Projected tsunami frequency too low", "08-08-2016 00:00:00", "09-10-2016 00:00:00", 1, "OK", "http://")
nodeC=FdessinCarto.controller.create_evenement("EV C", "08-07-2016 00:00:00", "09-08-2016 00:00:00", 1, "HOOOOO", "http://")
nodeD=FdessinCarto.controller.create_evenement("Accident", "08-10-2016 00:00:00", "09-11-2016 00:00:00", 1, "HOOOOO", "http://")


FdessinCarto.controller.create_edge(nodeA,nodeB, "LeLien", "Une mega explosion", "[]")
FdessinCarto.controller.create_edge(nodeB,nodeA, "InverseLien", "Une giga explosion", "[]")
FdessinCarto.controller.create_edge(nodeC,nodeD, "LienTest", "Ceci est un lien test", "[]")

FdessinCarto.controller.calculate_position('spring_layout');
FdessinCarto.draw_cartograph()


# FUNCTION TEST NE PAS L'UTILISER

def testclick(self, arg):
        print("testclick")
        # print(abc);
        print(arg);

    #FdessinCarto.canvas.mpl_connect('button_press_event', event)


#FdessinCarto.ChangeNodeColor()
#FdessinCarto.ChangeEdgeColor()
#FdessinCarto.zoom_wheel(1)
FdessinCarto.pan_drag()
#FdessinCarto.copynode()
#FdessinCarto.Delete_Node()
#FdessinCarto.node_popup_mouse_over()


#FdessinCarto.connect('delete_evenement', testclick)

# a = testclick(FdessinCarto)
# print("a %s" %a )

#print(FdessinCarto.Delete_Node())
#FdessinCarto.edge_popup_mouse_over()
#FdessinCarto.DrawLines()
#FdessinCarto.drag_node()
#FdessinCarto.DrawLines()
#FdessinCarto.testclick()
#FdessinCarto.Delete_Edge()
#FdessinCarto.Detect()
#FdessinCarto.display_grid()
#FdessinCarto.pan_keyboard()

#display
window.show_all()
Gtk.main()
