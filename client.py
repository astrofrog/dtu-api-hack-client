import json
from functools import partial
from matplotlib.patches import Rectangle

import requests
import numpy as np

URL = 'http://google.com'


class DataClient(object):

    def __init__(self):
        pass

    def histogram1d(self, x_attribute, x_range, x_bin, selection=None):

        query = {}
        query['ndim'] = 1
        query['x_attribute'] = x_attribute
        query['x_range'] = "{0},{1}".format(*x_range)
        query['x_bin'] = x_bin

        if selection:
            query['selection'] = json.dumps(selection)

        print(query)

        # request = requests.get(URL, query)
        #
        # print("did request", request.url)

        # TEMPORARY
        return np.linspace(x_range[0], x_range[1], x_bin), np.random.random(x_bin)

        # REAL CODE
        # result = request.json()
        # return result['edges'], result['values']

    def histogram2d(self, x_attribute, y_attribute, x_range, y_range, x_bin, y_bin, selection=None):

        query = {}
        query['ndim'] = 2
        query['x_attribute'] = x_attribute
        query['y_attribute'] = y_attribute
        query['x_range'] = "{0},{1}".format(*x_range)
        query['y_range'] = "{0},{1}".format(*y_range)
        query['x_bin'] = x_bin
        query['y_bin'] = y_bin

        if selection:
            query['selection'] = json.dumps(selection)

        print(query)

        # TEMPORARY
        return np.random.random((y_bin, x_bin))

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
        self.x_attribute = None
        self.y_attribute = None
        self.selection = {}
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
        if self.y_attribute is None:
            ymin, ymax = self.ax.get_ylim()
            self.selection = {'type': 'range',
                              'x_min': event.xdata,
                              'x_max': event.xdata,
                              'x_attribute': self.x_attribute}
            self._rectangle = Rectangle((self.selection['x_min'], ymin),
                                        width=0, height=ymax - ymin, edgecolor='red', facecolor='none')
        else:
            self.selection = {'type': 'rectangle',
                              'x_min': event.xdata,
                              'x_max': event.xdata,
                              'y_min': event.ydata,
                              'y_max': event.ydata,
                              'x_attribute': self.x_attribute,
                              'y_attribute': self.y_attribute
                              }
            self._rectangle = Rectangle((self.selection['x_min'], self.selection['y_min']),
                                        width=0, height=0, edgecolor='red', facecolor='none')
        self.ax.add_patch(self._rectangle)

    def update_selection(self, event):
        if event.inaxes is not self.ax:
            return
        if not self.selection_in_progress:
            return

        self.selection['x_max'] = event.xdata
        width = self.selection['x_max'] - self.selection['x_min']
        self._rectangle.set_width(width)

        if 'y_max' in self.selection:
            self.selection['y_max'] = event.ydata
            height = self.selection['y_max'] - self.selection['y_min']
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
        self.ax.figure.canvas.mpl_connect('button_release_event', self.update_histogram1d)
        self.update = self.update_histogram1d

    def update_histogram1d(self, event=None):
        if self.selection_in_progress:
            return
        x_range = self.ax.get_xlim()
        midpoints, array = self.data_client.histogram1d(self.x_attribute, x_range, self.x_nbin, selection=self.selection)
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
        self.ax.figure.canvas.mpl_connect('button_release_event', self.update_histogram2d)
        self.update = self.update_histogram2d

    def update_histogram2d(self, event=None):
        if self.selection_in_progress or (event is not None and event.inaxes is not self.ax):
            return
        x_range = self.ax.get_xlim()
        y_range = self.ax.get_ylim()
        array = self.data_client.histogram2d(self.x_attribute, self.y_attribute,
                                             x_range, y_range, self.x_nbin, self.y_nbin, selection=self.selection)
        self.ax.set_autoscale_on(False)
        if self.image is None:
            self.image = self.ax.imshow(array, aspect='auto', extent=[0, 1, 0, 1], transform=self.ax.transAxes)
        else:
            self.image.set_data(array)
        self.ax.set_autoscale_on(True)
        self.ax.figure.canvas.draw()
