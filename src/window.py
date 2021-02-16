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

# Gtk Imports

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk, Gio
from gi.repository import GLib

# Python Imports
import cairo
import time

@Gtk.Template(resource_path='/im/bernard/original/window.ui')

class OriginalWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'OriginalWindow'

    drawArea = Gtk.Template.Child()
    anZeige  = Gtk.Template.Child()
    quadranten  = Gtk.Template.Child()
    neustarten  = Gtk.Template.Child()



    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawArea.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.drawArea.connect('draw', self.onDraw)
        self.drawArea.connect('configure-event', self.onConfigure)
        self.drawArea.connect("button-press-event", self.onButtonPress)
        self.drawArea.connect("motion-notify-event", self.zeigeKoord)
        self.quadranten.connect("clicked", self.einVierQuad)
        self.neustarten.connect("clicked", self.neuStart)

        self.quadra = 2
        self.zeichneneu  = True
        self.surface     = None
        self.aktBreite   = 0
        self.aktHoehe    = 0
        self.crFarbe     = [1.0, 0.0, 0.0, 1.0]
        self.crDicke     = 4


    def onButtonPress(self, event, widget):
        print ("Bonege!")

    def einVierQuad(self, widget):
        if self.quadra == 2:
            self.quadra = 8
        elif self.quadra == 8:
            self.quadra = 2
        else:
            print ("self.quadra muss 2 oder 8 sein!")

        print ("quadranten", self.quadra)

        self.neuStart(widget)

    def neuStart(self, widget):
        sb = self.surface.get_width()
        sh = self.surface.get_height()
        #print("neush, sb", sh, sb)
        self.cr.rectangle(0, 0, sb, sh)  # x, y, width, height
        self.cr.set_operator(0);
        self.cr.fill()
        #print("ne2sh, sb", sh, sb)

        self.cr.set_operator(1)
        self.linio(0, pha, sb, pha) # zeichnet die horizontale Achse
        self.linio(pva, 0, pva, sh)
        #print("pha, pva", sh, sb)

        #self.drawArea.queue_draw()


    def zeigeKoord (self, area, eve):

        sb = self.surface.get_width()
        sh = self.surface.get_height()
        (x1, y1) = eve.x, eve.y

        x = int(x1-pva)         # x und y sind die Koordinaten im Aschsenkreuz der Zeichenebene
        y = int(-y1+pha)
        text = "(x = " + str(x) + ", y = " + str(y) + ")"
        #print (text)

        self.anZeige.set_text(text)

    def onConfigure(self, area, eve, data = None): # wird bei Änderung des Fensters aufgerufen
        ab = area.get_allocated_width()   #liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        _surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ab, ah)

        # wenn das Fenster verändert wird, wird die Zeichenebene angepasst
        if self.surface is not None:
            global sb, sh
            sb = self.surface.get_width()
            sh = self.surface.get_height()



            # bei Verkleinerung bleibt die alte Zeichenebene
            if ab < sb and ah < sh:
                return False

            cr = cairo.Context(_surface)

            # lädt die vorherige Ebene
            cr.set_source_surface(self.surface, 0.0, 0.0)
            cr.scale(ab, ah)
            cr.paint()

            self.aktBreite   = ab
            self.aktHoehe  = ah

            self.zeichneneu    = True     # d.h. dass in onDraw die Zeichenfläche neu gezeichnet wird


        else:
            self.drawArea.set_size_request(self.aktBreite, self.aktHoehe)

        self.surface = _surface
        self.cr   = cairo.Context(self.surface)
        return False

        # onDraw wird aufgerufen, wenn die Zeichebene neu gerendert wird
    def onDraw(self, area, cr):    # area ist das Fenster  cr ist ein context
        ab = area.get_allocated_width()   # liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        if self.surface is not None:
            cr.set_source_surface(self.surface, 0.0, 0.0)
            cr.paint()

            sb = self.surface.get_width()
            sh = self.surface.get_height()

            global pva, pha         # Position der vertikalen/horizontalen Achse
            pva = sb/self.quadra
            pha = sh - sh/self.quadra

            #print ("ab", ab, ah)
            #print ("sb", sb, sh)
            # bei Verkleinerung bleibt die alte Zeichenebene
            if ab < sb and ah < sh:
                return False

            if self.zeichneneu:
                print ("2pva =", pva, "pha =", pha)

                self.cr.rectangle(0, 0, sb, sh)  # x, y, width, height
                self.cr.set_operator(0);
                self.cr.fill()
                self.cr.set_operator(1)
                self.linio(0, pha, sb, pha) # zeichnet die horizontale Achse
                self.linio(pva, 0, pva, sh)

                #self.zeichneneu = False

        else:
            print ("Keine Infos über die Zeichenebene ...")

        return False

    def linio(self, x1, y1, x2, y2):
        self.cr.move_to(x1, y1)
        self.cr.line_to(x2, y2)

        self.cr.set_source_rgb(0, 0, 0)
        self.cr.set_line_width(1.5)
        self.cr.stroke()


