import time
import math
import functools
import librosshow.termgraphics as termgraphics
from librosshow.plotters import ScopePlotter

# https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects
def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


class SinglePlotViewer(object):
    def __init__(self, canvas, title = "", data_field = "data", array_index = None):
        self.g = canvas
        self.msg = None
        self.xmax = 10
        self.title = title
        self.data_field = data_field
        self.last_value = 0.0
        self.last_update_shape_time = 0
        self.array_index = array_index

        hmargin = self.g.shape[0]/40.
        vmargin = self.g.shape[1]/20.
        hsize = (self.g.shape[0] - 4*hmargin )
        vsize = (self.g.shape[1] - 4*vmargin )

        self.scope_plotter = ScopePlotter(self.g,
            left = hmargin,
            top = vmargin,
            right = hmargin + hsize,
            bottom = vmargin + vsize,
            ymin = None,
            ymax = None,
        )

    def update(self, msg):
        val = rgetattr(msg, self.data_field)
        if self.array_index is not None:
            val = val.__getitem__(self.array_index)
        self.last_value = float(val)
        self.scope_plotter.update(self.last_value)

    def draw(self):
        t = time.time()

        # capture changes in terminal shape at least every 0.25s
        if t - self.last_update_shape_time > 0.25:
            if self.g.update_shape():
                hmargin = self.g.shape[0]/40.
                vmargin = self.g.shape[1]/20.
                hsize = (self.g.shape[0] - 4*hmargin )
                vsize = (self.g.shape[1] - 4*vmargin )
                self.scope_plotter.left = hmargin
                self.scope_plotter.top = vmargin
                self.scope_plotter.right = hmargin + hsize
                self.scope_plotter.bottom = vmargin + vsize
            self.last_update_shape_time = t

        self.g.clear()

        self.g.set_color(termgraphics.COLOR_WHITE)
        self.scope_plotter.plot()

        if self.title:
            self.g.set_color((0, 127, 255))
            self.g.text(self.title, (0, self.g.shape[1] - 4))

        self.g.set_color((0, 255, 127))
        self.g.text(str(self.last_value), (int(self.g.shape[0]/3), self.g.shape[1] - 4))

        self.g.draw()

