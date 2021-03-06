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

import gi, faulthandler, signal, subprocess

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

# Python Imports
import cairo
import os, threading, time, datetime
import sys
import random
import math

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

@Gtk.Template(resource_path='/im/bernard/original/window.ui')

class OriginalWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'OriginalWindow'

    drawArea = Gtk.Template.Child()
    messageLabel  = Gtk.Template.Child()
    messageWidget = Gtk.Template.Child()
    anZeige  = Gtk.Template.Child()
    nivelo  = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawArea.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.drawArea.connect("button-press-event", self.onButtonPress)
        self.drawArea.connect("draw", self.on_draw)

        GLib.timeout_add(20, self.tick) # Go call tick every 10 whatsits.

        self.schlange    = []
        self.xkopf       = 0                        # Anfangsposition Schlange
        self.ykopf       = random.randint(-120, 200)
        self.richtung    = 0         # 0 = rechts  1 = rauf  2 = links   3 = runter
        self.spielBeginn = True
        self.diskZuPos   = True
        #self.zeigeAnw    = True
        self.xd          = random.randint(-200, 200)  # Anfangsposition Apfel
        self.yd          = random.randint(-200, 200)
        self.treffer     = False
        self.punkte      = 0
        self.nachLinks   = False
        self.nachRechts  = False
        self.zeitStart   = time.time()
        self.warte       = 0.2
        self.level       = 0

        self.warning    = "#00008b"

    def tick(self):
        ## Die Zeichenflächer wird erneuert und der "draw" - Effekt startet
        rect = self.get_allocation()
        self.get_window().invalidate_rect(rect, True)
        return True # Causes timeout to tick again.

    ## When the "draw" event fires, this is run
    def on_draw(self, widget, event):
        self.cr = self.get_window().cairo_create()
        ## Call our draw function to do stuff.
        geom = self.get_window().get_geometry()
        self.draw(geom.width, geom.height)
        #print (geom.width, geom.height)

    def onButtonPress(self, widget, eve):
        if eve.type == Gdk.EventType.BUTTON_PRESS and eve.button == 1:
            self.nachLinks  = True
            self.nachRechts = False
            if self.richtung == 3:
                self.richtung = 0
            else:
                self.richtung += 1
            #print (self.richtung)

        if eve.type == Gdk.EventType.BUTTON_PRESS and eve.button == 3:
            self.nachLinks  = False
            self.nachRechts = True
            if self.richtung == 0:
                self.richtung = 3
            else:
                self.richtung += -1

    def draw(self, width, height):

        cr = self.cr

        sb = width
        sh = height

        ## Zuerst wird der Nullpunkt in die Seitenmitte gesetzt
        ## Das heißt:
        ##  -y | -y
        ##  -x | +x
        ## ----0------
        ##  -x | +x
        ##  +y | +y

        matrix = cairo.Matrix(1, 0, 0, 1, width/2, height/2)
        cr.transform(matrix)

        cr.save()

        #print (sb, sh)

        if self.spielBeginn:
            self.zeigeAnweisung(self.warning, _("Linksklick = nach links Rechtsklick = nach rechts \n Spiel beginnt in 3 Sekunden"))
            self.posSchlange(cr)

        ng = len(self.schlange)-1
        #print (ng, self.schlange[ng] , self.schlange[ng-1])
        for i in range(ng,0,-1):
            self.schlange[i] = self.schlange[i-1].copy()

        if self.richtung == 0:
            self.schlange[0][0] += 20
        if self.richtung == 1:
            self.schlange[0][1] -= 20
        if self.richtung == 2:
            self.schlange[0][0] -= 20
        if self.richtung == 3:
            self.schlange[0][1] += 20

        if self.spielBeginn:
            time.sleep(5)

        self.zeichneSchlange(cr)
        time.sleep(self.warte)

        #cr.restore()

        kopf = self.schlange[0]
        if abs(kopf[0]) >= sb/2-25 or abs(kopf[1]) >= sh/2-25:
            #print (kopf[0], width/2)
            #cr.restore()
            #self.drawArea.queue_draw()
            rgba = (0, 1, 1, 1)
            self.zeichneDisk(0, 0, rgba, cr)
            #time.sleep(5)
            self.spielEnde(self.punkte, self.drawArea, cr)

        ax = abs(self.xd - kopf[0])
        ay = abs(self.yd - kopf[1])
        #print (ax,ay)
        if ax < 20 and ay < 20:
            self.treffer = True
            self.punkte += 1
            self.level = int(self.punkte/4)
            if self.level >= 1:
                self.warte = self.warte/(1+self.level/25)
            self.schlange.append([500,200])   # man kann einen beliebigen Punkt anhängen, es wird sowieso der Wert des vorangehenden hineinkopiert
            #print (self.schlange)
            punktausgabe = "Punkte: " + str(self.punkte)
            levelausgabe = "Level:  " + str(self.level)
            self.anZeige.set_text(punktausgabe)
            self.nivelo.set_text(levelausgabe)
            print ("Punkte:", self.punkte, "warte", self.warte)
        if self.treffer == True:
            self.xd          = random.randint(int(-sb/2+60), int(sh/2-60))  # neue Anfangsposition Apfel
            self.yd          = random.randint(int(-sh/2+100), int(sh/2-60))
            rgba =(1, 0, 0, 1)
            self.zeichneDisk(self.xd, self.yd, rgba, cr)
            print ("disko",sb, self.xd)
            self.treffer = False
        else:
            rgba =(1, 0, 0, 1)
            self.zeichneDisk(self.xd, self.yd, rgba, cr)

    def zeichneDisk(self, x1, y1, farb, cr):
        cr.set_source_rgba(farb[0], farb[1], farb[2], farb[3])
        cr.arc(x1, y1, 10, 0, 2*math.pi)
        cr.fill()

    def zeichneSchlange(self,cr):
        #print("zeichne Schlange")
        kopf = True
        for disk in self.schlange:
            x = disk[0]
            y = disk[1]
            if kopf:   # der Kopf
                rgba = (0, 0.2, 1, 1)
                self.zeichneDisk(x, y, rgba, cr)
                #self.drawArea.queue_draw()
                kopf = False
            else:
                rgba = (0, 1, 0, 1)
                self.zeichneDisk(x, y, rgba, cr)
                #self.drawArea.queue_draw()

    def spielEnde(self, pkt, drawArea, cr):
        print ("Du hast das Spiel mit ", pkt, "Punkten auf Level: ", self.level, "beendet!")
        rgba = (0, 1, 1, 1)
        self.zeichneDisk(0, 0, rgba, cr)
        endergebnis = "Spiel beendet mit " + str(self.punkte) + " Punkten."
        self.anZeige.set_text(endergebnis)
        time.sleep(2)

        sys.exit("Du bist aus dem Feld gekrochen!")

    def posSchlange(self, cr):   # positioniert die Schlange am Beginn des Spiels
        #ng = self.glieder
        x1 = self.xkopf
        y1 = self.ykopf
        self.schlange = [[x1,y1],[x1-20, y1], [x1-40, y1]]
        #print (self.schlange)
        self.spielBeginn = False

    def displayMessage(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.messageLabel.set_markup(markup)
        self.messageWidget.popup()
        self.hideMessageTimed(5)

    def zeigeAnweisung(self, type, text):
        markup = "<span foreground='" + type + "'>" + text + "</span>"
        self.messageLabel.set_markup(markup)
        self.messageWidget.popup()
        self.hideMessageTimed(12)

    @threaded
    def hideMessageTimed(self,t):
        time.sleep(t)
        GLib.idle_add(self.messageWidget.popdown)


    
