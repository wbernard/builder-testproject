# main.py
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

import sys
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio

from .window import OriginalWindow



class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='im.bernard.original',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):

        self.win = self.props.active_window
        if not self.win:
            self.win = OriginalWindow(application=self)

        self.win.present()

        self.aktionMenu()

    def aktionMenu(self):
        infoAktion = Gio.SimpleAction.new("about", None)
        infoAktion.connect("activate", self.beiInfoKlick)
        self.add_action(infoAktion)


    def beiInfoKlick(self, action, widget):
        infoDialog = Gtk.AboutDialog()
        infoDialog.set_logo_icon_name("im.bernard.Original")
        infoDialog.set_destroy_with_parent(True)
        infoDialog.set_name("Original")
        infoDialog.set_version("0.3")
        infoDialog.set_authors(["Walter Bernard"])
        infoDialog.set_artists(["Tobias Bernard"])
        infoDialog.set_license_type(Gtk.License.GPL_3_0)
        infoDialog.set_copyright("© 2021 Walter Bernard")
        infoDialog.set_modal(True)
        infoDialog.set_transient_for(self.win)

        infoDialog.run()
        infoDialog.destroy()


def main(version):
    app = Application()
    return app.run(sys.argv)
