import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import Controller
import BasicModel as md

class Draw:
    def __init__(self):
        window = Gtk.Window()
        window.connect("delete-event", Gtk.main_quit)
        window.set_default_size(1500, 1500)
        window.set_title('TestDrawCartograph')

        # Canvas Figure display on networkx
        fig = Figure(figsize=(12, 12), dpi=80)
        ax = fig.add_subplot(111)

        canvas = FigureCanvas(fig)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        window.add(box)
        box.pack_start(canvas, True, True, 0)

        MainModel = md.Model()
        A = Controller.Controller(MainModel)

        # Create new graph
        name_graph = A.create_new_graph("GraphOK")
        # A.model.load_graph('chronograph0')
        # print(A.model.total_graph.nodes())
        nodeA = A.create_evenement("EV A", "07-08-2016 17:25:00", "08-08-2016 17:25:01", 1, "BLAH BLAH BLAH", "http://")
        nodeB = A.create_evenement("EV B", "08-08-2016 17:25:00", "09-08-2016 17:25:01", 1, "OK", "http://")



