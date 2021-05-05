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
#!/usr/bin/python3

# Python Imports
import cairo
import math
import os, threading, time, datetime, sys
import numpy as np
from scipy.optimize import curve_fit
import random

# Gtk Imports

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk, Gio
from gi.repository import GLib


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper

@Gtk.Template(resource_path='/im/bernard/original/window.ui')

class OriginalWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'OriginalWindow'

    drawArea      = Gtk.Template.Child()
    messageLabel  = Gtk.Template.Child()
    messageWidget = Gtk.Template.Child()
    menuKnopf     = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.drawArea.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.drawArea.connect('draw', self.onDraw)
        self.drawArea.connect('configure-event', self.onConfigure)
        self.drawArea.connect('button-press-event', self.posDisk)


        self.linfarb     = [[0.1,0.37,0.71], [0.38,0.21,0.51],[0.15,0.64,0.41], [0.65,0.11,0.18], [0.39,0.27,0.17], [1, 0, 0.17], [0.39, 0, 1]]
        self.surface     = None
        self.aktBreite   = 0
        self.aktHoehe    = 0
        self.crFarbe     = [0.88, 0.11, 0.14, 1.0]
        self.zeichneneu  = True
        self.schlange    = []
        self.xkopf       = random.randint(20, 480)
        self.ykopf       = random.randint(20, 380)
        self.richtung    = 0          # 0 = rechts  1 = rauf  2 = links   3 = runter
        self.spielBeginn = True
        self.diskZuPos   = True
        self.zeigeAnw    = True


        self.warning    = "#00008b"

    def onConfigure(self, area, eve, data = None): # wird bei Änderung des Fensters aufgerufen
        ab = area.get_allocated_width()   #liest die aktuellen Abmessungen des Fensters ein
        ah = area.get_allocated_height()

        _surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ab, ah)

        # wenn das fenster verändert wird wird eine neue Zeichenebene erstellt
        if self.surface is not None:
            #global sb, sh
            sb = self.surface.get_width()
            sh = self.surface.get_height()

            # bei Verkleinerung bleibt die alte Ebene
            if ab < sb and ah < sh:
                return False

            cr = cairo.Context(_surface)

            # die alte ebene wird in die neue geladen
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
        print ("draw 118")
        if self.surface is not None:
            global sb, sh
            cr.set_source_surface(self.surface, 0.0, 0.0)
            #cr.set_source_rgb(0, 0, 0)   # setzt die Farbe der Fläche
            cr.paint()
            print ("draw 123")
            #self.drawArea.queue_draw()

            sb = self.surface.get_width()   # Breite der Zeichenebene
            sh = self.surface.get_height()  # Höhe der Zeichenebene

            # bei Verkleinerung bleibt die alte Ebene
            if ab < sb and ah < sh:
                return False

            if self.zeichneneu:

                if self.zeigeAnw:
                    self.zeigeAnweisung(self.warning, _("Klicke auf einen Punkt! \n Dort wird dann der Apfel liegen und das Spiel beginnt!"))
                    self.zeigeAnw = False
                else:
                    pass

                self.bereiteEbene()

                if self.diskZuPos == False:
                    rgba = self.crFarbe
                    print ("disko", xd)
                    self.zeichneDisk(xd, yd, rgba)

                #if self.spielBeginn == False:

                self.zeichneSchlange()
                #self.drawArea.queue_draw()

                self.zeichneneu = False
        else:
            print ("keine Zeichenebene !!")

    def zeichneDisk(self, x1, y1, farb):
        #print ("zeichnen")
        self.cr.set_source_rgba(farb[0], farb[1], farb[2], farb[3])
        self.cr.set_line_width(3)
        self.cr.set_line_cap(1) # Linienende 0 = BUTT, 1 = rund  2 = eckig

        self.cr.arc(x1, y1, 10, 0, 2*math.pi)
        self.cr.fill()

    def zeichneSchlange(self):
        kopf = True
        for disk in self.schlange:
            x = disk[0]
            y = disk[1]
            if kopf:   # der Kopf
                rgba = (0, 0.2, 1, 1)
                self.zeichneDisk(x, y, rgba)
                #self.drawArea.queue_draw()
                kopf = False
            else:
                rgba = (0, 1, 0, 1)
                self.zeichneDisk(x, y, rgba)
                #self.drawArea.queue_draw()

    def bewegeSchlange(self, rtg):
        n = 0
        while self.schlange[0][0] <= (sb-20):
            #self.drawArea.queue_draw()
            ng = len(self.schlange)-1
            for i in range(1,len(self.schlange)):
                self.schlange[ng] = self.schlange[ng-1].copy()
                ng -= 1

            if rtg == 0:
                self.schlange[0][0] += 20
            if rtg == 1:
                self.schlange[0][1] -= 20
            if rtg == 2:
                self.schlange[0][0] -= 20
            if rtg == 3:
                self.schlange[0][1] += 20

            self.zeichneneu = True
            #self.bereiteEbene()
            #rgba = self.crFarbe
            #self.zeichneDisk(xd, yd, rgba)
            #self.zeichneSchlange()
            self.onDraw(self.drawArea, self.cr)
            #self.drawArea.queue_draw()
            n += 1

            print ("uno", n, self.schlange)
            time.sleep(0.3)

    def bereiteEbene(self):
        self.cr.rectangle(0, 0, sb, sh)  # x, y, Breite, Höhe
        self.cr.set_operator(0)
        self.cr.fill()
        self.cr.set_operator(1)

    def posDisk(self, area, eve):  # positioniert den Apfel
        if self.diskZuPos == True:
            global xd, yd
            xd = int(eve.x)
            yd = int(eve.y)
            rgba = self.crFarbe
            #print ("disko", xd)
            self.zeichneDisk(xd, yd, rgba)
            #time.sleep(1)
            self.diskZuPos = False
        else:
            pass
        self.drawArea.queue_draw()
        self.zeichneneu = False
        #time.sleep(1)
        if self.spielBeginn:
            self.posKopf()
            self.posSchlange()
        else:
            pass

    def posKopf(self):   # positioniert den Kopf zufällig
        self.xkopf       = random.randint(60, sb-20)
        self.ykopf       = random.randint(20, sh-20)
        if (abs(self.xkopf-xd) <= 20) or (abs(self.ykopf-yd) <= 20):
            self.posKopf()
        else:
            pass

    def posSchlange(self):   # positioniert die Schlange am Beginn des Spiels
        #ng = self.glieder
        x1 = self.xkopf
        y1 = self.ykopf
        self.schlange = [[x1,y1],[x1-20, y1], [x1-40, y1]]
        print (self.schlange)
        self.zeichneSchlange()
        self.spielBeginn = False
        self.bewegeSchlange(self.richtung)

    def displayMessage(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.messageLabel.set_markup(markup)
        self.messageWidget.popup()
        self.hideMessageTimed(1)

    def zeigeAnweisung(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.messageLabel.set_markup(markup)
        self.messageWidget.popup()
        self.hideMessageTimed(1)

    @threaded
    def hideMessageTimed(self,t):
        time.sleep(t)
        GLib.idle_add(self.messageWidget.popdown)


