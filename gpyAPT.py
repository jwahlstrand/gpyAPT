import time,sys
import pyAPT,pylibftdi
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib,Gio

# warning: this program has only been tested with one rotation stage

serial=str(83841365)

true_home=131.2

MENU_XML="""
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <item>
        <attribute name="action">app.prefs</attribute>
        <attribute name="label" translatable="yes">_Preferences</attribute>
      </item>
      <item>
        <attribute name="action">app.about</attribute>
        <attribute name="label" translatable="yes">_About</attribute>
      </item>
      <item>
        <attribute name="action">app.quit</attribute>
        <attribute name="label" translatable="yes">_Quit</attribute>
        <attribute name="accel">&lt;Primary&gt;q</attribute>
    </item>
    </section>
  </menu>
</interface>
"""

builder = Gtk.Builder()

class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super(AppWindow,self).__init__(*args, **kwargs)
        self.app = self.get_application()
        
        
        builder.add_from_file("gpyAPT.glade")
        grid = builder.get_object("grid1")

        self.add(grid)
        
        self.set_title("SN: "+serial)
        self.connect("delete-event",Gtk.main_quit)
        grid.show()

try:
  con = pyAPT.PRM1(serial_number=serial)
except pylibftdi.FtdiError as ex:
    print '\tCould not find APT controller S/N of',serial
    #sys.exit(1)

window=AppWindow()
window.show_all()

pos_label = builder.get_object("curr_pos_label")

def display_pos(pos):
  pos_label.set_text(u"%1.5f\u00B0" % (pos+true_home))

display_pos(con.position())

goto_sb = builder.get_object("goto_spinbutton")

def get_goto_pos():
  return goto_sb.get_value()-true_home

goto_sb.set_value(con.position()+true_home)

home_button = builder.get_object("home_button")

step_sb = builder.get_object("step_spinbutton")
up_button = builder.get_object("up_button")
down_button = builder.get_object("down_button")
stop_button = builder.get_object("stop_button")

moving_label = builder.get_object("moving_label")
homing_label = builder.get_object("homing_label")

def update_pos():
  stat=con.status()
  display_pos(stat.position)
  m=stat.moving
  if not m:
    moving_label.set_text("")
  return stat.moving
  
def update_pos2():
  stat=con.status()
  display_pos(stat.position)
  h=stat.homing
  if not h:
    homing_label.set_text("")
  m=stat.moving
  if not m:
    moving_label.set_text("")
  return stat.homing

def on_stop_clicked(button):
  con.stop(wait=False)
  GLib.timeout_add(100,update_pos)

def on_home_clicked(button):
  con.home(velocity=2, wait=False)
  homing_label.set_text("homing")
  moving_label.set_text("moving")
  GLib.timeout_add(100,update_pos2)

def on_up_clicked(button):
  con.move(step_sb.get_value(),wait=False)
  moving_label.set_text("moving")
  GLib.timeout_add(100,update_pos)

def on_down_clicked(button):
  con.move(-step_sb.get_value(),wait=False)
  moving_label.set_text("moving")
  GLib.timeout_add(100,update_pos)

def on_goto_changed(spinbutton):
  position = get_goto_pos()
  con.goto(position, wait=False)
  moving_label.set_text("moving")
  GLib.timeout_add(100,update_pos)

def check_position():
  display_pos(con.position())
  return True

goto_sb.connect("value-changed", on_goto_changed)
home_button.connect("clicked", on_home_clicked)
up_button.connect("clicked", on_up_clicked)
down_button.connect("clicked", on_down_clicked)
stop_button.connect("clicked", on_stop_clicked)

GLib.timeout_add(500,con.keepalive)
GLib.timeout_add(250,check_position)

Gtk.main()

