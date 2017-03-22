import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import matplotlib.font_manager as font_manager
import matplotlib.dates
from pylab import *
from matplotlib.dates import MonthLocator, DateFormatter, drange


class DrawChronoMap(GObject.GObject):

    __gsignals__ = {
        'delete_evenement': (GObject.SIGNAL_RUN_FIRST, None,
                             (object,)),
        'rclick_canvas': (GObject.SIGNAL_RUN_FIRST, None,
                          (str,)),
        'selection_change': (GObject.SIGNAL_RUN_FIRST, None,
                             (object,)),
        'node_position_change': (GObject.SIGNAL_RUN_FIRST, None,
                                 (object, object,))
    }

    def __init__(self,ax, controller):
        # Init GObject Connection
        GObject.GObject.__init__(self)

        #Global controller
        self.controller = controller

        #Global event
        self.event = None

        #Global selection
        self.event = None
        self.selection = (None, None)
        self.temp_selection = (None, None)

        #Global graph
        self.G = self.controller.total_graph()

        #Global data for the setting chronograph
        self.h = None #step of the graduation of chronologie
        self.granularity = None #granualarity of the graduation

        #Global model
        self.model = self.controller.model

        #Global Axis
        self.ax = ax

        #Global figure
        self.fig = self.ax.get_figure()

        #Gloal canvas
        self.canvas = self.ax.get_figure().canvas

        #Global list

        self.nodelist = self.controller.get_node_list()
        self.edgelist=self.controller.get_edge_list()

        #Global empty collection
        #Global nodecollection
        self.nodecollection=None
        self.constante = None

        #Gloabl data of node
        self.datanode = []
        self.nodetime = []
        self.node2remove = None

        #Global empty list
        self.eventnode_with_rectangle=[]
        self.start_date=[]
        self.end_date=[]
        self.event_name=[]

        #Global data axes
        self.axis_x=[]

        #Global label axis y
        self.yticks = None

        # Drag time
        self.drag_time=0

        self.press = []

        self.drag_press = []

        self.xdrag=0
        self.ydrag=0

        #event data
        self.xdata=0
        self.ydata=0

        #event if we selecte edge
        self.node1=None
        self.node2=None

        #Global mpl functions
        self.dragrectangle_onpress = None
        self.dragrectangle_onrelease = None
        self.dragrectangle_onmotion = None

        self.darkblue = [ 100/255.0, 149/255.0, 237/255.0, 1]



############### Global function #########################################
    def draw_chronograph(self):

        #update self.event_name
        self.event_name=[]

        #update graph
        self.G = self.controller.total_graph()

        #update data of nodecollection
        self.nodelist = self.controller.get_node_list()

        self.eventnode_with_rectangle = []

        self.nodetime = []

        print(self.nodelist)
        print(self.event_name)

        # Sorts node by priority
        self.nodelist.sort(key=lambda node: node.d_order, reverse=True)

        for i, node in enumerate(self.nodelist):
            self.event_name.append(node.title)
            bottom = ((i-1)*0.5) + 1.0
            width = node.end_time - node.start_time
            left = node.start_time
            height = 0.3

            rectangle = self.ax.barh(((i-1)*0.5)+1.0, width, left=left, height=height, align='center', color= self.darkblue, alpha = 0.75)

            for r in rectangle:
                rx, ry = r.get_xy()
                cx = rx + r.get_width()/2.0
                cy = ry + r.get_height()/2.0

                r.annotation = self.ax.annotate(node.title, (cx, cy), color='black',
                               fontsize=8, ha='center', va='center')

            rectangle.bottom = bottom
            rectangle.i = i

            self.eventnode_with_rectangle.append([node,rectangle])
            node.pos=i
            self.nodetime.append(node.start_time)
            self.nodetime.append(node.end_time)

             #pos of i in the dictionnary


        taille=len(self.event_name)
        print(taille)
        pos=arange(0.5,(taille+2)*0.5+0.5,0.5)
        print(pos)
        self.yticks=yticks(pos,self.event_name)
        locsy,labelsy=self.yticks
        self.ax.set_yticks(pos)
        self.ax.set_yticklabels([], size='small')
        self.ax.axis('tight')
        self.ax.set_ylim(0, taille*0.5+0.5)

        #format the x-axis
        delta = datetime.timedelta(hours=720)
        if len(self.nodetime) == 0:
            minAx = 735964.0
            maxAx = 736277.0
        else:
            minAx = min(self.nodetime)
            maxAx = max(self.nodetime)

        dates = drange(matplotlib.dates.num2date(int(minAx)), matplotlib.dates.num2date(int(maxAx)),delta)
        posx = arange(len(dates)*3.0)

        self.xticks = xticks(posx,dates)
        locsx,labelsx = self.xticks
        print(len(locsx))
        self.ax.set_xticks(posx)

        # self.ax.set_xticklabels(labelsx, size='small')
        self.ax.set_xlim(minAx, maxAx)
        self.ax.xaxis.set_major_locator(MonthLocator())
        # self.ax.xaxis.set_minor_locator(HourLocator())

        self.ax.xaxis.set_major_formatter(DateFormatter('%d-%b'))
        # self.ax.xaxis.set_minor_formatter(DateFormatter('%m-%d %H:%M'))
        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
        #self.ax.xaxis.tick_top()

        # Finish up
        self.ax.grid(color = 'g', linestyle = ':')
        font = font_manager.FontProperties(size='small')
        self.ax.legend(loc=1,prop=font)
        self.ax.invert_yaxis()
        self.fig.autofmt_xdate()

        # Create popups
        self.build_popups()

        # Create cursor
        self.build_cursor()


        #init cursor
        self.ly.set_xdata((minAx+ maxAx)/2)
        self.txt.set_text('y=%s' % (self.controller.model.string_from_numdate((minAx+ maxAx)/2)))

        self.canvas.draw()

    def full_redraw(self):
         self.clear_all()
         self.draw_chronograph()

    def do_selection_change(self, selection):

        if selection[0] == "node":
            self.change_rectangle_color(selection[1][0])
        else:
            self.change_rectangle_color(None)

    def change_rectangle_color(self, node):

        # Colors definition
        red = [1, 0, 0, 1]
        dark = [0, 0, 0, 1]
        yellow=[1,1,0,1]
        blue = self.darkblue

        if node == None:
            for i,rectangle in self.eventnode_with_rectangle:
                for j in rectangle:
                    j.set_facecolor(blue)
        else:
            for node_item,rectangle in self.eventnode_with_rectangle:
                if node_item == node:
                    for n_rect in rectangle:
                        n_rect.set_facecolor(yellow)
                else :
                    for n_rect in rectangle :
                        n_rect.set_facecolor(blue)
        # Colors changed redraw canvas
        self.canvas.draw()

 ############################# Detect function ##############################################


    def Detect(self):
        '''
        Picks an object to determine the element that was selected
        self.event holds the actual clicked object
        self.selected holds the last selected object.
        '''
        def on_click(event):
            # Erase acutal data
            self.event = None
            self.temp_selection = (None, None)
            #if we clic on a node
            x=event.xdata
            y=event.ydata
            #print("1st")
            #print(x,y,event.inaxes, self.event,event.button)
            #print("2nd")
            #print(event.canvas.figure)

            for node, rectangle in self.eventnode_with_rectangle:
                if (node.start_time < x < node.end_time) and ((node.pos - 1) * 0.5 + 1 - 0.1 < y < (node.pos - 1) * 0.5 + 1 + 0.1):
                    self.event = [node]
                    self.temp_selection = ("node", self.event, rectangle)
                    self.selection = self.temp_selection

            if event.button == 3 :
                #print ("activate")
                if event.inaxes == None:
                    #print("activate Graduation")
                    self.emit("rclick_canvas", "Graduation")
                    #print("activate")
                    #print(self.event, event.inaxes)

                elif event.inaxes != None and self.event != None:
                    #print("node selection in Detect")

                    #self.emit('selection_change', self.selection)
                    self.emit("rclick_canvas", "Node")


                else:
                    self.emit("rclick_canvas", "Empty")


        def on_release(event):

            self.emit('selection_change', self.selection)
            #print('on release')
            #print(self.selection)

        self.canvas.mpl_connect('button_press_event', on_click)
        self.canvas.mpl_connect('button_release_event', on_release)


    def node_popup_mouse_over(self):

        def on_motion(event):
            x = event.xdata
            y = event.ydata
            visibility_changed = False
            should_be_visible = None
            self.popup.set_visible(False)
            actual_node = None

            for i,rectangle in self.eventnode_with_rectangle:
                if (i.start_time<x<i.end_time) and ((i.pos-1)*0.5+1-0.1<y<(i.pos-1)*0.5+1+0.1) :
                    should_be_visible = True
                    # print("non")
                    # print(should_be_visible,popup.get_visible())
                    actual_node =  i
                    break

            if should_be_visible != self.popup.get_visible():
                visibility_changed = True

                #print(should_be_visible,self.popup.get_visible(),actual_node)
                if actual_node:
                    #print("yes")
                    self.popup.set_text('Titre : %s\ndate du debut: %s -date de fin : %s \ngroupe du noeud: %s, description: %s, fichier attache: %s ' %(actual_node.title, actual_node.start_time,actual_node.end_time,actual_node.node_group,actual_node.description,actual_node.attachment_list))
                    self.popup.set_position((x,y))
                self.popup.set_visible(should_be_visible)

            if visibility_changed:
                self.canvas.draw()

        self.canvas.mpl_connect('motion_notify_event',on_motion)



#Molette
    def zoom_wheel(self, base_scale = 2.):
        def zoom(event):
            # get the current x and y limits
            ax = self.ax
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
            cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5

            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1/base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                #print event.button
            # set new limits
            ax.set_xlim([xdata - cur_xrange*scale_factor,
                        xdata + cur_xrange*scale_factor])
            self.canvas.draw() # force re-draw

        self.canvas.mpl_connect('scroll_event',zoom)

#   drag

        '''Fleche directionnelle'''

    def pan_keyboard(self):

        pan_multiplier = 0.05

        def pan_keypress(event):
            print(event.key)

            # TODO Si aucun noeud est selectionne
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            if event.key == 'right':
                left_movement = (cur_xlim[1] - cur_xlim[0]) * pan_multiplier
                self.ax.set_xlim([left_movement + cur_xlim[0],
                                 left_movement + cur_xlim[1]])

            if event.key == 'left':
                right_movement = (cur_xlim[1] - cur_xlim[0]) * pan_multiplier
                self.ax.set_xlim([ - right_movement + cur_xlim[0],
                                 - right_movement + cur_xlim[1]])

            if event.key == 'up':
                up_movement = (cur_ylim[1] - cur_ylim[0]) * pan_multiplier
                self.ax.set_ylim([ - up_movement + cur_ylim[0],
                                 - up_movement + cur_ylim[1]])

            if event.key == 'down':
                down_movement = (cur_ylim[1] - cur_ylim[0]) * pan_multiplier
                self.ax.set_ylim([ + down_movement + cur_ylim[0],
                                 + down_movement + cur_ylim[1]])
            self.canvas.draw()
        #self.canvas.mpl_connect('key_press_event', pan_keypress)

    #display grid
    def display_grid(self):
        self.ax.grid(True)

    #hide grid
    def hide_grid(self):
        self.ax.grid(False)


    #Drag rectangle
    def drag_rectangle(self):

        def on_press(event):
            node = None
            x = event.xdata
            y = event.ydata
            self.drag_press = (x,y)
            self.position_changed = False
            self.drag_new_date = None
            self.drag_new_end_date = None

        def on_motion(event):

            'on motion we will move the rect if the mouse is over us'
            if not self.drag_press:
                return None

            if not self.temp_selection[0] == 'node':
                return None

            if not event.button == 1:
                return None

            x_press, y_press = self.drag_press

            selection_type , node, rectangle = self.temp_selection
            #print(type(event.ydata),event.ydata,type(y_press), y_press)

            dx = event.xdata - x_press

            self.drag_new_date = x_press + dx
            for r in rectangle:
                r.set_x(self.drag_new_date)
                self.drag_new_end_date = self.drag_new_date + r.get_width()

                rx, ry = r.get_xy()
                cx = rx + r.get_width()/2.0
                cy = ry + r.get_height()/2.0
                r.annotation.xyann = (cx, cy)

            self.position_changed = True
            self.canvas.draw()



        def on_release(event):
            if self.position_changed:
                self.emit('node_position_change', self.temp_selection[1][0], (self.drag_new_date, self.drag_new_end_date))

            self.drag_new_date = None
            self.drag_new_end_date = None
            self.drag_press = None
            self.canvas.draw()

        #connect to all the events we need
        self.dragrectangle_onpress = self.canvas.mpl_connect('button_press_event', on_press)
        self.dragrectangle_onrelease = self.canvas.mpl_connect('button_release_event', on_release)
        self.dragrectangle_onmotion = self.canvas.mpl_connect('motion_notify_event', on_motion)

    def disconnect_drag_rectangle (self):
        self.canvas.mpl_disconnect(self.dragrectangle_onpress)
        self.canvas.mpl_disconnect(self.dragrectangle_onrelease)
        self.canvas.mpl_disconnect(self.dragrectangle_onmotion)


#Display attributs
    def wait(self):
        def on_motion(event):
            x= event.xdata
            y=event.ydata
            popup=self.ax.text(x, y, '', style='italic',bbox={'facecolor':'y', 'alpha':0.5, 'pad':10})
            visibility_changed = False
            should_be_visible=False
            popup.set_visible(visibility_changed)
            for i,rectangle in self.eventnode_with_rectangle:

                if (i.start_time<x<i.end_time) and ((i.pos-1)*0.5+1-0.1<y<(i.pos-1)*0.5+1+0.1) :
                    should_be_visible=True
                    if should_be_visible != popup.get_visible():
                        visibility_changed = True
                        popup.set_text('Titre : %s, Date du debut: %s, date de fin : %s, groupe du noeud: %s, description: %s, fichier attache: %s ' %(i.title,i.start_time,i.end_time,i.node_group,i.description,i.attachment_list))
                        visibility_changed = True
                        popup.set_visible(visibility_changed)

            if visibility_changed:
                self.canvas.draw()

        self.wait=self.canvas.mpl_connect('motion_notify_event',on_motion)

#def cursor:
    def cursor(self):

        def drag_press_cursor(event):
            #update self.press
            self.press=[]
            if len(self.nodetime) == 0:
                minAx = 735964.0
                maxAx = 736277.0
            else:
                minAx = min(self.nodetime)
                maxAx = max(self.nodetime)
            middle=(minAx+ maxAx)/2
            #print("cursor %s" %event.button)

            #print(middle, event.xdata,event.x)
            if ((middle-1<event.xdata <middle+1) and event.button == 3):
                x = event.xdata
                y = event.ydata
                self.press = [x,y]
                #self.emit('rclick_canvas', "Cursor")
            else :
                return

        def mouse_move_cursor(event):

            xpress = self.press
            #print(xpress)

            if xpress == [] :
                #self.pan_drag()
                return None
            elif event.button != 3 :
                return None
            else :
                self.ly.set_xdata(event.xdata)
                self.txt.set_text('Event date =%s' % (self.controller.model.string_from_numdate(int(event.xdata))))
                self.event = self.ly.set_xdata(event.xdata)
                self.temp_selection = ("cursor", self.event)
                #self.emit('selection_change', self.temp_selection)

                self.canvas.draw()

        def release_cursor(event):
            self.press=[]
            self.canvas.draw()

        self.cursor_drag_press = self.canvas.mpl_connect('button_press_event', drag_press_cursor)
        self.cursor_drag_motion = self.canvas.mpl_connect('motion_notify_event', mouse_move_cursor)
        self.cursor_release = self.canvas.mpl_connect('button_release_event', release_cursor)

    def disconnect_cursor(self):
        self.canvas.mpl_disconnect(self.cursor_drag_press)
        self.canavs.mpl_disconnect(self.cursor_drag_motion)
        self.canavs.mpl_disconnect(self.cursor_release)

    def _configure_xaxis(self):
        # make x axis date axis
        self.ax.xaxis_date()
        # format date to ticks on every 7 days
        rule = mdates.rrulewrapper(mdates.DAILY, interval=7)
        loc = mdates.RRuleLocator(rule)
        formatter = mdates.DateFormatter("%d %b")
        self._ax.xaxis.set_major_locator(loc)
        self._ax.xaxis.set_major_formatter(formatter)
        xlabels = self._ax.get_xticklabels()
        plt.setp(xlabels, rotation=30, fontsize=9)

    def build_cursor(self):
        self.ly = self.ax.axvline(color='k')  # the vert line
        self.txt = self.ax.text(0.7, 0.9, '', transform=self.ax.transAxes)

    def build_popups(self):
        #Node attibutes popup
        self.popup = self.ax.text(0, 0, '', style='italic',bbox = {'facecolor':'y', 'alpha':0.5, 'pad':10})


    def clear_all(self):

        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        self.ax.cla()
        self.ax.set_xlim(cur_xlim)
        self.ax.set_ylim(cur_ylim)

    # def set_legend_y(self):
    #     #update graph
    #     self.G = self.controller.total_graph()
    #     #update self.nodelist
    #     self.nodelist = self.controller.get_node_list()
    #     print("set_legend_y:")
    #     #print(nodelist)
    #     for i in range(len(self.nodelist)):
    #         self.event_name.append(self.nodelist[i].title)
    #     taille=len(self.event_name)
    #     pos=arange(0.5,(taille+2)*0.5+0.5,0.5)
    #
    #     self.yticks=yticks(pos,self.event_name)
    #     locsy,labelsy=self.yticks
    #
    #     self.ax.set_yticks(pos)
    #     self.ax.set_yticklabels(labelsy, size='small')
    #     self.ax.axis('tight')
    #
    #     self.ax.set_ylim(0, taille*0.5+0.5)
    #
    #     self.ax.grid(color = 'g', linestyle = ':')
    #
    #     font = font_manager.FontProperties(size='small')
    #     self.ax.legend(loc=1,prop=font)
    #     self.ax.invert_yaxis()
    #     self.canvas.draw()
