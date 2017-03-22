import View as V
import sys
sys.path.append("/Users/chen/Desktop/minesparis/JE/Chronomap/scripts")
import BasicModel as md
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from matplotlib.figure import Figure
import numpy as np
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import random
import matplotlib.lines as lines
import Controller as CT



#model using GTK
window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)
window.set_default_size(1500, 1500)
window.set_title('ChronoMap')

# Init ChronoCanvas
figChrono = Figure(figsize=(20,20), dpi=80)
axChrono = figChrono.add_subplot(111)
canvasChrono = FigureCanvas(figChrono)


#Init CartoCanvas
figCarto = Figure(figsize=(20,20), dpi=80)
axCarto = figCarto.add_subplot(111)
canvasCarto = FigureCanvas(figCarto)



mainModel=md.Model()
controller=CT.Controller(mainModel)
A=Draw(controller,a)
A.controller.create_new_graph("ChronoGraph")
nodeA=A.create_node("EV A", "07-08-2016 17:25:00", "08-08-2016 17:25:01", 1, "BLAH BLAH BLAH", "http://")
nodeB=A.create_node("EV B", "08-08-2016 17:25:00", "09-08-2016 17:25:01", 1, "OK", "http://")
A.create_edge(nodeA,nodeB, "LeLien", "Une mega explosion", "[]")
A.create_edge(nodeB,nodeA, "InverseLien", "Une giga explosion", "[]")


A.FdessinChrono.controller.create_evenement("EV C", "08-07-2016 00:00:00", "09-08-2016 00:00:00", 1, "HOOOOO", "http://")

A.FdessinChrono.controller.create_evenement("Accident", "08-10-2016 00:00:00", "09-11-2016 00:00:00", 1, "HOOOOO", "http://")

A.FdessinChrono.controller.create_edge(nodeAchrono,nodeBchrono, "LeLien", "Une mega explosion", "[]")
A.FdessinChrono.controller.create_edge(nodeBchrono,nodeAchrono, "InverseLien", "Une giga explosion", "[]")

#Carto Canvas
nodeAcarto=A.FdessinCarto.controller.create_evenement("outdated research material", "01-01-2016 00:00:00", "01-02-2016 00:00:00", 1, "BLAH BLAH BLAH", "http://")

nodeBcarto=A.FdessinCarto.controller.create_evenement("Projected tsunami frequency too low", "08-08-2016 00:00:00", "09-10-2016 00:00:00", 1, "OK", "http://")

nodeCcarto=A.FdessinCarto.controller.create_evenement("EV C", "08-07-2016 00:00:00", "09-08-2016 00:00:00", 1, "HOOOOO", "http://")

nodeDcarto=A.FdessinCarto.controller.create_evenement("Accident", "08-10-2016 00:00:00", "09-11-2016 00:00:00", 1, "HOOOOO", "http://")

A.FdessinCarto.controller.create_edge(nodeAcarto,nodeBcarto, "LeLien", "Une mega explosion", "[]")
A.FdessinCarto.controller.create_edge(nodeBcarto,nodeAcarto, "InverseLien", "Une giga explosion", "[]")

#Chrono canvas



plt.draw_if_interactive()
canvas.draw()

window.show_all()
Gtk.main()
