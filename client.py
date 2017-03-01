from functools import partial
from matplotlib.patches import Rectangle

import requests
import numpy as np

URL = 'http://google.com'


class DataClient(object):

    def __init__(self):
        pass

    def histogram1d(self, attribute, vrange, nbin):

        query = {}
        query['type'] = 'histogram'
        query['ndim'] = 1
        query['attribute'] = attribute
        query['min'] = vrange[0]
        query['max'] = vrange[1]
        query['nbin'] = nbin

        # request = requests.get(URL, query)
        #
        # print("did request", request.url)

        # TEMPORARY
        return np.linspace(vrange[0], vrange[1], nbin), np.random.random(nbin)

        # REAL CODE
        # result = request.json()
        # return result['edges'], result['values']

    def histogram2d(self, x_attribute, y_attribute, x_range, y_range, x_nbin, y_nbin):

        query = {}
        query['type'] = 'histogram'
        query['ndim'] = 2
        query['attribute'] = x_attribute
        query['attribute'] = y_attribute
        query['xmin'] = x_range[0]
        query['xmax'] = x_range[1]
        query['ymin'] = y_range[0]
        query['ymax'] = y_range[1]
        query['x_nbin'] = x_nbin
        query['y_nbin'] = y_nbin

        # TEMPORARY
        return np.random.random((y_nbin, x_nbin))

        # REAL CODE
        # request = requests.get(URL, query)
        # result = request.json()
        # return result['edges'], result['values']


class AxesHelper(object):

    def __init__(self, ax, data_client, selection_callback=None):
        self.ax = ax
        self.data_client = data_client
        self.selection_in_progress = False
        self._rectangle = None
        self.ax.figure.canvas.mpl_connect('button_press_event', self.start_selection)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.update_selection)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.finalize_selection)
        self.selection_callback = selection_callback

    def start_selection(self, event):
        if event.inaxes is not self.ax:
            return
        if event.button != 3:
            return
        if self.selection_in_progress:
            raise ValueError("Selection already in progress, unexpected error")
        self.selection_in_progress = True
        self.selection = {'type':'rectangle',
                          'xmin': event.xdata,
                          'ymin': event.ydata,
                          'xmax': event.xdata,
                          'ymax': event.ydata}
        self._rectangle = Rectangle((self.selection['xmin'], self.selection['ymin']),
                                    width=0, height=0, edgecolor='red', facecolor='none')
        self.ax.add_patch(self._rectangle)

    def update_selection(self, event):
        if event.inaxes is not self.ax:
            return
        if not self.selection_in_progress:
            return
        self.selection['xmax'] = event.xdata
        self.selection['ymax'] = event.ydata
        width = self.selection['xmax'] - self.selection['xmin']
        height = self.selection['ymax'] - self.selection['ymin']
        self._rectangle.set_width(width)
        self._rectangle.set_height(height)
        self.ax.figure.canvas.draw()

    def finalize_selection(self, event):
        if event.inaxes is not self.ax:
            return
        if not self.selection_in_progress:
            return
        self._rectangle.remove()
        self.selection_in_progress = False
        self.ax.figure.canvas.draw()
        if self.selection_callback is not None:
            self.selection_callback(self.selection)

    def set_selection(self, selection):
        self.selection = selection
        self.update()

    def histogram1d(self, x_attribute, x_nbin):
        self.x_attribute = x_attribute
        self.x_nbin = x_nbin
        self.histogram = None
        self.ax.callbacks.connect('xlim_changed', self.update_histogram1d)
        self.update = self.update_histogram1d

    def update_histogram1d(self, event=None):
        x_range = self.ax.get_xlim()
        midpoints, array = self.data_client.histogram1d(self.x_attribute, x_range, self.x_nbin)
        if self.histogram is not None:
            for patch in self.histogram:
                patch.remove()
        self.ax.set_autoscale_on(False)
        self.histogram = self.ax.plot(midpoints, array, drawstyle='steps-mid', color='k')
        self.ax.set_autoscale_on(True)
        self.ax.figure.canvas.draw()

    def histogram2d(self, x_attribute, y_attribute, x_nbin, y_nbin):
        self.x_attribute = x_attribute
        self.y_attribute = y_attribute
        self.x_nbin = x_nbin
        self.y_nbin = y_nbin
        self.image = None
        self.ax.callbacks.connect('xlim_changed', self.update_histogram2d)
        self.update = self.update_histogram2d

    def update_histogram2d(self, event=None):
        x_range = self.ax.get_xlim()
        y_range = self.ax.get_ylim()
        array = self.data_client.histogram2d(self.x_attribute, self.y_attribute,
                                             x_range, y_range, self.x_nbin, self.y_nbin)
        self.ax.set_autoscale_on(False)
        if self.image is None:
            self.image = self.ax.imshow(array, extent=[0, 1, 0, 1], transform=self.ax.transAxes)
        else:
            self.image.set_data(array)
        self.ax.set_autoscale_on(True)
        self.ax.figure.canvas.draw()

if __name__ == "__main__":

    client = DataClient()
    client.histogram1d('a', [1, 3], 100)
