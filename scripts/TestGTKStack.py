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
from numpy import sin, cos, pi, linspace

w=Gtk.Window()

vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1000)
w.add(vbox)

# Init ChronoCanvas
figChrono = Figure(figsize=(20,20), dpi=80)
axChrono = figChrono.add_subplot(111)
canvasChrono = FigureCanvas(figChrono) 

n = 1000
xsin = linspace(-pi, pi, n, endpoint=True)
xcos = linspace(-pi, pi, n, endpoint=True)
ysin = sin(xsin)
ycos = cos(xcos)

sinwave = axChrono.plot(xsin, ysin, color='black', label='sin(x)')
coswave = axChrono.plot(xcos, ycos, color='black', label='cos(x)', linestyle='--')

axChrono.set_xlim(-pi,pi)
axChrono.set_ylim(-1.2,1.2)

axChrono.fill_between(xsin, 0, ysin, (ysin - 1) > -1, color='blue', alpha=.3)
axChrono.fill_between(xsin, 0, ysin, (ysin - 1) < -1, color='red',  alpha=.3)
axChrono.fill_between(xcos, 0, ycos, (ycos - 1) > -1, color='blue', alpha=.3)
axChrono.fill_between(xcos, 0, ycos, (ycos - 1) < -1, color='red',  alpha=.3)

axChrono.legend(loc='upper left')

axChrono = figChrono.gca()
axChrono.spines['right'].set_color('none')
axChrono.spines['top'].set_color('none')
axChrono.xaxis.set_ticks_position('bottom')
axChrono.spines['bottom'].set_position(('data',0))
axChrono.yaxis.set_ticks_position('left')
axChrono.spines['left'].set_position(('data',0))




#Init CartoCanvas
figCarto = Figure(figsize=(20,20), dpi=80)
axCarto = figCarto.add_subplot(111)
canvasCarto = FigureCanvas(figCarto) 

stack = Gtk.Stack()
stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
stack.set_transition_duration(1000)

stack.add_titled(canvasCarto,"chekc", "Check Button")
stack.add_titled(canvasChrono, "label", "A label")
#stack.add_named(canvasCarto,'canvasCarto')
#stack.add_named(canvasChrono,'canvasChrono')

stack_switcher = Gtk.StackSwitcher()
stack_switcher.set_stack(stack)
vbox.pack_start(stack_switcher, True, True, 0)
vbox.pack_start(stack, True, True, 0)

stack.set_visible_child(canvasChrono)
stack.set_visible_child_name('canvasChrono')

canvasChrono.draw()
canvasCarto.draw()


w.connect("delete-event", Gtk.main_quit)
w.show_all()
Gtk.main()