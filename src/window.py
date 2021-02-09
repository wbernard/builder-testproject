# window.py
#
# Copyright 2021 walter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
from gi.repository import Gdk, GObject

# Python Imports
import cairo
import time

@Gtk.Template(resource_path='/im/bernard/original/window.ui')

class OriginalWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'OriginalWindow'

    drawArea = Gtk.Template.Child()
    anZeige  = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawArea.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.drawArea.connect("button-press-event", self.onButtonPress)
        self.drawArea.connect("motion-notify-event", self.zeigeKoord)

    def onButtonPress(self, event, widget):
        print ("Bonege!")

    def zeigeKoord (self, area, eve):
        aw = area.get_allocated_width()   #liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, aw, ah)

        sw = self.surface.get_width()
        sh = self.surface.get_height()
        (x1, y1) = eve.x, eve.y
        x = int(x1-sw/2)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int(-y1+sh/2)
        text = "(x = " + str(x) + ", y = " + str(y) + ")"
        print (text)

        koordinat  = Gtk.Label(text)
        self.anZeige.add(koordinat)
        self.anZeige.show_all()
        time.sleep(0.5)
        self.anZeige.queue_draw()
        self.anZeige.show_all()



