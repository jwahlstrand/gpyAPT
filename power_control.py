import time,sys,gi,pyAPT,pylibftdi
from math import sin,pi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib

# warning: this program has only been tested with one rotation stage

serial=str(83857500)

true_home=131.2

try:
  con = pyAPT.PRM1(serial_number=serial)
except pylibftdi.FtdiError as ex:
    print '\tCould not find APT controller S/N of',serial
    sys.exit(1)

builder = Gtk.Builder()
builder.add_from_file("power_control.glade")

window = builder.get_object("window")
window.set_title("Power control: SN "+serial)
window.connect("delete-event",Gtk.main_quit)
window.show_all()

pos_label = builder.get_object("curr_pos_label")
mJ_label = builder.get_object("mJ_label")
max_mJ_sb = builder.get_object("max_mJ_spinbutton")

def display_pos(pos):
  true_pos = pos+true_home
  pos_label.set_text(u"%1.2f\u00B0" % true_pos)
  max_energy = max_mJ_sb.get_value()
  mJ_label.set_text(u"%.3f mJ" % (max_energy*sin((pi/180.0)*pos)**2))

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

