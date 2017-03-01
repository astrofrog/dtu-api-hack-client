from client import DataClient, AxesHelper
import matplotlib.pyplot as plt

client = DataClient()

fig = plt.figure()

ax1 = fig.add_subplot(1, 2, 1)
helper1 = AxesHelper(ax1, client)
helper1.histogram1d('a', 10)
helper1.update()

ax2 = fig.add_subplot(1, 2, 2)
helper2 = AxesHelper(ax2, client, selection_callback=helper1.set_selection)
helper2.histogram2d('a', 'b', 10, 15)
helper2.update()

print(fig.canvas.callbacks.callbacks)

plt.show()
