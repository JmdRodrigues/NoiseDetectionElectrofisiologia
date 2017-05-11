import numpy as np
from bokeh.palettes import OrRd9
from bokeh.models import ColumnDataSource
from scipy.stats import gaussian_kde
from utils.colormap import RGBAColorMapper

def Heatmap(x, y, ImageWidth, ImageHeight, ResolutionFactor, alpha):
	"""
	Create Zmap to plot the heatmap on the screen
	:param x: x-array with the mouse coordinates over the horizontal dimension
	:param y: y-array with the mouse coordinates over the vertical dimension
	:param ImageWidth: [0,ImageWidth] - It defines the ranges of the matrix that will store the heatmap values in the horizontal dimension
	:param ImageHeight: [0, ImageHeight] - It defines the ranges of the matrix that will store the heatmap values in the vertical dimension
	:param ResolutionFactor: value in range [0,1] that will define the number of points in each dimension
	:param alpha: "a" value of the rgba matrix [0-255]
	:return: Zmap - matrix with rgba values to be plotted in bokeh by the image_rgba method
	"""

	if(ResolutionFactor > 1 or ResolutionFactor < 0):
		raise ValueError("Resolution factor only accepts values between 0 and 1.")
	if(alpha > 255 or alpha < 0):
		raise ValueError("Alpha only accepts values between 0 and 255")


	#Organize arrays in Matrix
	values = np.vstack([x, y])

	#Calculates the density of points smoothed by a gaussian
	kernel = gaussian_kde(values)

	#creates a grid to allocate RGBA values
	X, Y = np.mgrid[0:ImageWidth:int(1/ResolutionFactor), 0:ImageHeight:int(1/ResolutionFactor)]

	#Map of positions
	positions = np.vstack([X.ravel(), Y.ravel()])

	#Map of density
	Z = np.reshape(kernel(positions).T, X.shape)

	#ColorMap
	colormap = RGBAColorMapper(0, np.max(Z), OrRd9, inverse=True)

	#Colormap of density
	Zmap = colormap.color(np.rot90(Z), alpha=alpha)
	ZmapSource = ColumnDataSource(data = dict(im=[Zmap]))

	return ZmapSource





