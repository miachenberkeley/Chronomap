import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from pylab import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import Draw as D
import Controller as ct
import BasicModel as md



# Initialise plot
#model using GTK
window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)
window.set_default_size(1500, 1500)
window.set_title('TestDrawChronograph')

#using matplotlib creation of canvas
fig = Figure(figsize=(12,12), dpi=80)
ax = fig.add_subplot(111)

canvas=FigureCanvas(fig)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
window.add(box)
box.pack_start(canvas,True,True,0)

#init controller
model = md.Model()
controller = ct.Controller(model)
A = D.DrawChronoMap(ax,controller)

controller.create_new_graph("GraphChronomap")

#create node in controller
nodeA=A.controller.create_evenement("outdated research material", "01-01-2016 00:00:00", "01-02-2016 00:00:00", 1, "BLAH BLAH BLAH", "http://")
nodeB= A.controller.create_evenement("Projected tsunami frequency too low", "08-08-2016 00:00:00", "09-10-2016 00:00:00", 1, "OK", "http://")
nodeC=A.controller.create_evenement("EV C", "08-07-2016 00:00:00", "09-08-2016 00:00:00", 1, "HOOOOO", "http://")
nodeD=A.controller.create_evenement("Accident", "08-10-2016 00:00:00", "09-11-2016 00:00:00", 2, "HOOOOO", "http://")


A.controller.create_edge(nodeA,nodeB, "LeLien", "Une mega explosion", "[]")
A.controller.create_edge(nodeB,nodeA, "InverserLeLien", "Une giga explosion", "[]")



#print(controller.model.total_graph.nodes())
#print('GRAPH =====================================')
#print(A.controller.model.total_graph.nodes())

A.draw_chronograph()
#A.pan_keyboard()
#A.ChangeColor()
#A.cursor()
#A.zoom_wheel(1)

#A.node_popup_mouse_over()
#A.deleteNode()
A.Detect()
#A.drag_rectangle()
#A.clear_all()
#A.zoom_wheel(1.2)
#A.copynode()


#B.LeftClick()
#B.drag_rectangle()





#display
window.show_all()
Gtk.main()
