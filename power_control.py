import time,sys,gi,pyAPT,pylibftdi
from math import sin,pi,asin,sqrt
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib

serial=str(83841365)

try:
  con = pyAPT.PRM1(serial_number=serial)
except pylibftdi.FtdiError as ex:
    print '\tCould not find APT controller with S/N',serial
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
energy_sb = builder.get_object("energy_spinbutton")
min_angle_sb = builder.get_object("min_angle_spinbutton")
min_energy_b = builder.get_object("min_energy_button")

max_mJ_sb.set_value(0.7)
min_angle_sb.set_value(85)

def display_pos(pos):
  true_pos = pos
  pos_label.set_text(u"%1.2f\u00B0" % true_pos)
  max_energy = max_mJ_sb.get_value()
  min_angle = min_angle_sb.get_value()
  mJ_label.set_text(u"%.4f mJ" % (max_energy*sin((pi/180.0)*2*(pos-min_angle))**2))

display_pos(con.position())

goto_sb = builder.get_object("goto_spinbutton")

def get_goto_pos():
  return goto_sb.get_value()

goto_sb.set_value(con.position())

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
  con.home(velocity=10, wait=False)
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
  
def on_energy_changed(spinbutton):
  energy = spinbutton.get_value()
  max_energy = max_mJ_sb.get_value()
  if energy>max_energy:
    print "you requested an impossible energy"
    return
  new_pos = 180.0/pi*asin(sqrt(energy/max_energy))/2+min_angle_sb.get_value()
  con.goto(new_pos, wait=False)
  moving_label.set_text("moving")
  GLib.timeout_add(100,update_pos)

def on_minimize(button):
  con.goto(min_angle_sb.get_value(), wait=False)
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
energy_sb.connect("value-changed",on_energy_changed)
min_energy_b.connect("clicked", on_minimize)

GLib.timeout_add(500,con.keepalive)
GLib.timeout_add(250,check_position)

Gtk.main()

