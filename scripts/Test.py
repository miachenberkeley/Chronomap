import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class DialogTest:

    def rundialog(self, widget, data=None):
        self.dia.show_all()
        result = self.dia.run()
        self.dia.hide()


    def destroy(self, widget, data=None):
        Gtk.main_quit()

    def __init__(self):
        self.window = Gtk.Window()
        self.window.connect("destroy", self.destroy)

        self.dia = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK_CANCEL,
                                       "Delete nodes?")
        self.dia.vbox.pack_start(self.window,True,True,0)


        self.button = Gtk.Button("Run Dialog")
        self.button.connect("clicked", self.rundialog, None)
        self.window.add(self.button)
        self.button.show()
        self.window.show()



if __name__ == "__main__":
    testApp = DialogTest()
    Gtk.main()