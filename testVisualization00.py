import os
import pickle
import time
import numpy as np
import matplotlib.pyplot as plt
from novainstrumentation import smooth
from math import pi
from collections import Counter, defaultdict
from bokeh.driving import cosine
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed import autoload_server
from utils.heatmap import Heatmap, RGBAColorMapper
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Slider, TapTool, HoverTool, LinearColorMapper, LogColorMapper, OpenURL, CustomJS, Slider, Callback, Button, AbstractButton, ColorBar, RangeSlider
from bokeh.models.glyphs import ImageURL
from bokeh.models.widgets import Select
from bokeh.models.glyphs import Rect, Patches, Bezier
from bokeh.charts import Area
from utils.DivText import Header
from bokeh.server.server import Server
from bokeh.layouts import row, widgetbox, Spacer
from bokeh.plotting import figure, ColumnDataSource, save, curdoc, output_file, show
from bokeh.client import show_session, push_session
from CreateHeatmapData import HeatMapData
from bokeh.palettes import Blues9, Viridis11
from SanboxCatia.pathmath import createMouseData
import seaborn as sns
from bokeh.document import Document
from random import randint
import pandas as pd
from WBMTools.sandbox.interpolation import interpolate_data
from ConvertHexToRGB import hex_to_rgb


# output_file('ClickTest.html')
#push_session in the current document
main_session = push_session(curdoc())

#Directory of the Collection
coll_dir = "Collections/CollectionsJoao"
#List Collections
file = os.listdir(coll_dir)[60]
#open data
with open(coll_dir + "/" + file, 'rb') as handle:
	collection = pickle.load(handle)

#Variables
ClickType = []
ClickTime = []
ClickXPosition = []
ClickYPosition = []
ClickColor = []
colors = ['yellow', 0, 'red']
MouseX = []
MouseY = []
MouseTime = []
t_C = 0
ScrollAmp = []
ScrollTime = []
ScrollLeft = [0]
ScrollRight = []
#look inside collection for all events
for i in collection:

	event = collection[i]
	# print(event['Type'])
	if(event['Type'] == "New Connection"):
		Time_I = float(event['Time'])
	elif (event['Type'] == 'Settings'):
		height = event['Data']['ScreenProperties']['availHeight']
		width = event['Data']['ScreenProperties']['availWidth']

	elif(event['Type'] == "Click"):
		data = event['Data'].split(";")
		ClickType.append(data[0])
		ClickTime.append((float(event['Time']) - Time_I))

		ClickColor.append(colors[int(data[0])])

		xpos = randint(0, width)
		ypos = randint(0, height)

		ClickXPosition.append(xpos)
		ClickYPosition.append(ypos)
	elif(event['Type'] == "Scroll"):
		data = event['Data'].split(';')
		ScrollAmp.append(float(data[0]))
		ScrollTime.append(float(event['Time'])-Time_I)
		ScrollLeft.append(float(event['Time'])-Time_I)
		ScrollRight.append(float(event['Time']) - Time_I)
	elif(event['Type'] == "Keyboard"):
		continue
	elif(event['Type'] == "Wheel"):
		continue
	elif(event['Type'] == "Mouse"):
		data = event["Data"].split(';')
		MouseX.append(int(data[2]))
		MouseY.append(int(data[3]))
		# if(t_C == 0):
		# 	MouseTime.append(0)
		# 	time_I = float(data[-1])
		# 	t_C = 1
		# else:
		MouseTime.append((float(event['Time']) - Time_I))
	elif(event['Type'] == "TabClosed"):
		T_end = float(event['Time'] - Time_I)
		print(event)

ScrollRight.append(600.0)
#create np array scroll
ScrollAmp = np.array(ScrollAmp)
ScrollAmp = np.around(8*abs((ScrollAmp/max(ScrollAmp))-1)).astype(int)
ScrollColor = [Blues9[i] for i in ScrollAmp]
widt = 0.1
#create line map for scroll information
ScrolWidth = [widt+(0.1*i) for i in range(0,len(ScrollAmp))]

# ScrollSource1 = ColumnDataSource(data=dict(x = np.linspace(0,len(ScrollAmp), len(ScrollAmp)), alpha=ScrollAmp, width=ScrolWidth))
ScrollSource2 = ColumnDataSource(data=dict(left=ScrollLeft, right=ScrollRight, color=ScrollColor))
pim = figure(plot_width=1024, plot_height=128)
# pim.vbar(x='x', top=1, bottom=0,  width='width', fill_color="#FF1234", fill_alpha="alpha", source=ScrollSource1)
pim.quad(left='left', top=1, bottom=0,  right='right', fill_color='color', fill_alpha=0.5, line_color = None, source=ScrollSource2)
# pim.scatter(ScrollTime, ScrollAmp)

# plt.plot(ScrollTime, ScrollAmp)
# plt.show()
#Process data with Catia's code
MouseDict = dict(t=MouseTime, x=MouseX, y=MouseY)
dM = pd.DataFrame.from_dict(MouseDict)

time_variables, space_variables = interpolate_data(dM, t_abandon=20)
print(time)
#testvelocityparameters
rightV = np.array(time_variables['ttv'])
rightV = np.insert(rightV, 0, 0)
rightV = np.delete(rightV, -1)
leftV = time_variables['ttv']
# colorsV = Viridis11[]
vx = 10.0*(time_variables['vx']/max(time_variables['vx']))
print(vx)
sss = np.around(vx).astype(int)
print(sss)

colorsV = [Viridis11[i] for i in sss]
#Create Data Source with everything
MouseSpaceSource = ColumnDataSource(data=dict(x=space_variables['xs'], y=space_variables['ys']))
MouseTimeSource = ColumnDataSource(data=dict(x=time_variables['xt'], y=time_variables['yt'], t=time_variables['tt']))
MouseXSource = ColumnDataSource(data=dict(x = time_variables['xt'], v=time_variables['vx'], t = time_variables['ttv']))
MouseYSource = ColumnDataSource(data=dict(y = time_variables['yt'], v=time_variables['vy'], t = time_variables['ttv']))
MouseSpeedSource = ColumnDataSource(data=dict(vx=time_variables['vx'], vy=time_variables['vy'], t=time_variables['ttv'], vt = time_variables['vt'], right=rightV, left=leftV, color=colorsV))
ClickSource = ColumnDataSource(data=dict(x=ClickXPosition, y=ClickYPosition, type=ClickType, color = ClickColor, time=ClickTime))

p1 = figure(
    tools="pan, box_zoom, ywheel_pan, resize, reset, save",
	plot_width=1024, plot_height=512,
    y_range=(height, 0),
    x_range=(0, width),
    x_axis_label="Pixels_X", y_axis_label="Pixels_Y",
	toolbar_sticky = False, toolbar_location='below'
    )

#Scatter Plot for mouse movement
l1 = p1.scatter('x', 'y', source=MouseSpaceSource, radius=10, fill_color="#2c7fb8", fill_alpha=0.25, line_color=None)
l2 = p1.annulus('x', 'y', source=ClickSource, color='color', alpha=0.2, inner_radius=5, outer_radius=10)

TOOLS = "box_zoom, hover, box_select, lasso_select, save, pan, tap, reset"

#plot with Mouse velocity
pV1 = figure(title="Mouse and Velocity X", x_axis_location="above",
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below', plot_width=1024, plot_height=256)

pV1.quad(left='left', top=1, bottom=0,  right='right', fill_color='color', fill_alpha=0.5, line_color = None, source=ScrollSource2)
pV1.circle(x = 't', y = 'v', source = MouseXSource, line_dash="4 4", line_width=1, color='blue')
pV1.line(x = 't', y = 'v', source = MouseXSource, line_dash="4 4", line_width=0.5, color='blue', legend='X Velocity')
pV1.circle(x = 't', y = 'x', source = MouseXSource, line_dash="4 4", line_width=0.5, color='red')
pV1.line(x = 't', y = 'x', source = MouseXSource, line_dash="4 4", line_width=0.5, color='red', legend='X Position')
pV1.vbar(x='time', bottom=0, top=max(time_variables['vx']), width=0.2, source=ClickSource, color='color')

pV1.legend.location = "top_left"
# pV1.legend.click_policy="hide"

#plot with Mouse velocity

pV3 = figure(title="Mouse and Velocity Y", x_axis_location="above",
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below', plot_width=1024, plot_height=256)

pV3.quad(left='left', top=1, bottom=0,  right='right', fill_color='color', fill_alpha=0.5, line_color = None, source=ScrollSource2)
pV3.circle(x = 't', y = 'v', source = MouseYSource, line_dash="4 4", line_width=1, color='blue')
pV3.line(x = 't', y = 'v', source = MouseYSource, line_dash="4 4", line_width=0.5, color='blue', legend='X Velocity')
pV3.circle(x = 't', y = 'x', source = MouseYSource, line_dash="4 4", line_width=0.5, color='red')
pV3.line(x = 't', y = 'x', source = MouseYSource, line_dash="4 4", line_width=0.5, color='red', legend='X Position')
pV3.vbar(x='time', bottom=0, top=max(time_variables['vx']), width=0.2, source=ClickSource, color='color')

pV3.legend.location = "top_left"
# pV3.legend.click_policy="hide"

# cr = pV1.circle(x='t', y='vx', source=MouseSpeedSource, size=5,
#                 fill_color="grey", hover_fill_color="firebrick",
#                 fill_alpha=0.05, hover_alpha=0.3,
#                 line_color=None, hover_line_color="white")

# pV1.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))

pV2 = figure(title="Mouse Velocity Y", x_axis_location="above",
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below', plot_width=1024, plot_height=256)

pV2.circle(x = 't', y = 'vy', source = MouseSpeedSource, line_dash="4 4", line_width=1, color='gray')
pV2.line(x = 't', y = 'vy', source = MouseSpeedSource)

pV2.vbar(x='time', bottom=0, top=max(time_variables['vy']), width=0.2, source=ClickSource, color='color')

#plot with Mouse Position
pV5 = figure(title="Mouse Time X", x_axis_location="above",
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below', plot_width=1024, plot_height=256)

pV5.line(x = 't', y = 'x', source = MouseTimeSource)
pV5.vbar(x='time', bottom=0, top=max(time_variables['xt']), width=0.2, source=ClickSource, color='color')

pV4 = figure(title="Mouse Time Y", x_axis_location="above",
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below', plot_width=1024, plot_height=256)

pV4.line(x = 't', y = 'y', source = MouseTimeSource)
pV4.vbar(x='time', bottom=0, top=max(time_variables['yt']), width=0.2, source=ClickSource, color='color')

#Test horizontal bars

pV6 = figure(title="Mouse Time X", x_axis_location="above",
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below', plot_width=1024, plot_height=512)


LinkingSource = ColumnDataSource(data=dict(vx=time_variables['vx'], vy=time_variables['vy'], t=time_variables['ttv'], vt = time_variables['vt'], right=rightV, left=leftV, color=colorsV))
#Try linking 2 velocity plots
#plot with Mouse velocity
pVLink1 = figure(title="Mouse Velocity Linked", x_axis_location="above",
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below', plot_width=1024, plot_height=256)

pVLink1.circle(x = 't', y = 'vx', source = MouseSpeedSource)

pVLink2 = figure(title="Mouse Velocity Linked", x_axis_location="above",
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below', plot_width=1024, plot_height=256)

pVLink2.circle(x = 't', y = 'vy', source = MouseSpeedSource)


# pV5.quad(left='left', top=1, bottom=0,  right='right', fill_color='color', line_color = None, source=MouseSpeedSource)
l=layout([p1],
         [pV1],
         [pV3],
         )

# show(l)
curdoc().add_root(l)
main_session.show(l)
main_session.loop_until_closed()
