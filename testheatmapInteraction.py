import os
import pickle
import time
import numpy as np
from math import pi
from collections import Counter, defaultdict
from bokeh.io import Document
from bokeh.driving import cosine
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed import autoload_server
from utils.heatmap import Heatmap
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Slider, TapTool, HoverTool, LinearColorMapper, LogColorMapper, OpenURL, CustomJS, Slider, Callback, Button, AbstractButton, ColorBar, RangeSlider
from bokeh.models.glyphs import ImageURL
from bokeh.models.widgets import Div
from bokeh.server.server import Server
from bokeh.layouts import row, widgetbox
from bokeh.plotting import figure, ColumnDataSource, save, curdoc
from bokeh.client import show_session, push_session
from bokeh.palettes import Blues9
import seaborn as sns
from bokeh.document import Document


main_session = push_session(curdoc())

coll_dir = "David_Collection"
collections = os.listdir(coll_dir)
# ----------------------------------------------------------------------------------------------------
# In the future this might have to go to a Bokeh function
# ----------------------------------------------------------------------------------------------------
# Access Screenshot using localhost for server access
url1 = "http://localhost:8000/static/ScreenShots/Screen.png"
AvailableCollections = []
# Access Data
TimeofEvent = []
TotalSession = 0
MaxDuration = 0
TotalEvents = []
LastEventTime = []
ActivityRatio = []

SessionDays = []
SessionHour = dict()

SessionNames = dict()
SessionEvents = dict()
TimeEvents = dict()

#MouseData
MouseData = defaultdict(dict)
ActivityData = defaultdict(dict)
i = 0
for file in collections:
	# open Collection/Session
	with open(coll_dir + "/" + file, 'rb') as handle:
		collection = pickle.load(handle)
	if(len(collection.keys())>50):
		AvailableCollections.append(file[:-4])
		MouseX = []
		MouseY = []
		#SaveNamesinList
		# Scroll in collection to find all events
		for i in collection:
			event = collection[i]
			# print(event)
			if (event['Type'] == 'Settings'):
				height = event['Data']['ScreenProperties']['availHeight']
				width = event['Data']['ScreenProperties']['availWidth']
			elif(event['Type'] == 'New Connection'):
				MouseData[file[:-4]]['Time'] = event['Time']
				SessionDays.append(str(time.localtime(event['Time'])[2]))
				# print(time.localtime(event['Time']))
				HOUR = time.localtime(event['Time'])[3] + (time.localtime(event['Time'])[4])/60 + (time.localtime(event['Time'])[5])/3600
				MouseData[file[:-4]]['Events'] = len(collection.keys())
				TotalEvents.append(event['Time'])
				key = str(time.localtime(event['Time'])[2])
				SessionHour.setdefault(key, {})
				SessionEvents.setdefault(key, {})
				SessionNames.setdefault(key, {})
				key2 = str(int(HOUR))
				SessionHour[key].setdefault(key2, []).append(HOUR)
				SessionEvents[key].setdefault(key2, []).append(len(collection.keys()))
				SessionNames[key].setdefault(key2, []).append(file[:-4])
				TimeEvents.setdefault(key, []).append(str(time.localtime(event['Time'])[3]))
				TotalSession = TotalSession + 1

			elif(event['Type'] == 'TabClosed'):
				if(MaxDuration < event['Data']['Duration']):
					MaxDuration = event['Data']['Duration']

			elif(event['Type'] == 'Mouse'):
				data = event["Data"].split(';')
				MouseX.append(int(data[2]))
				MouseY.append(int(data[3]))
				TotalEvents.append(event['Time'])
				key = str(time.localtime(event['Time'])[2])
				# TimeEvents.setdefault(key, []).append(str(time.localtime(event['Time'])[3]))

			else:
				# print(event)
				TotalEvents.append(event['Time'])
				key = str(time.localtime(event['Time'])[2])
				# TimeEvents.setdefault(key, []).append(str(time.localtime(event['Time'])[3]))
			# ActivityRatio.append(event['Data']['NumberOfMessages']/event['Data']['Duration'])
			# TimeofEvent.append((event['Time']))

		# When All Events are Done Save x and y data in Dictionnary
		MouseData[file[:-4]]['x'] = MouseX
		MouseData[file[:-4]]['y'] = MouseY



Days = [x for x in TimeEvents.keys()]
Days.sort()

Hours = np.linspace(0, 23, 24).astype('int').astype('str')
# print(TimeEvents.items())
for a in TimeEvents.keys():
	Cou = Counter(TimeEvents[a])
	TimeEvents[a] = Cou

print(SessionHour)

hour = []
day = []
events = []
names = []
rate = []

print(SessionHour['21'])

for d in Days:
	for h in Hours:
		hour.append(SessionHour[d][h])
		day.append(d*np.ones(len(SessionHour[d][h])))
		events.append(SessionEvents[d][h])
		names.append(SessionNames[d][h])
		# TimeEvents[d][h])



source = ColumnDataSource(
	data=dict(day=day, hour=hour, rate=rate)
)
ActivitySource = ColumnDataSource(data=dict(day = day, hour= hour, events = events, name = names))
print(MouseData[AvailableCollections[0]])
MouseSource = ColumnDataSource(data=dict(x = MouseData[AvailableCollections[0]]['x'], y = MouseData[AvailableCollections[0]]['y']))

#Create Figure
p1 = figure(
    tools="pan, box_zoom, ywheel_pan, resize, reset, save",
	plot_width=1024, plot_height=512,
    y_range=(height, 0),
    x_range=(0, width),
    x_axis_label="Pixels_X", y_axis_label="Pixels_Y"
    )

#Heatmap Image
Zmap = Heatmap(MouseSource.data['x'], MouseSource.data['y'], width, height, 0.2, 75)
l1 = p1.image_rgba(image=[Zmap], x=0, y=height, dw=width, dh=height)
#Scatter Plot
l2 = p1.scatter('x', 'y', source=MouseSource, radius=10, fill_color="#2c7fb8", fill_alpha=0.25, line_color=None)

TOOLS = "hover,save,pan,tap"

p = figure(title="David Activity",
           x_range=Days, y_range=list(Hours),
           x_axis_location="above", plot_width=1024, plot_height=512,
           tools=TOOLS, toolbar_sticky=False, toolbar_location='below')

p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "10pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = pi / 3

# colors = ['#3288bd', '#99d594', '#e6f598', '#fee08b', '#fc8d59', '#d53e4f']
# colors = ['#C2CFD7', '#94B2C4', '#5B88A2', '#396F8F', '#1B618A', '#335D77', '#112B3A']
colors = ['#EBEBEB', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b']
# Blues9.reverse()
# print(Blues9)
mapper = LogColorMapper(palette=colors)
color_bar = ColorBar(color_mapper = mapper, location=(0,0))
p.rect(x="day", y="hour", width=1, height=1,
       source=ActivitySource,
       fill_color={'field': 'events', 'transform': mapper},
       line_color='White',
       line_alpha = 0.7,
       line_width=4,
       fill_alpha = 0.6,
       tags = names
       )
p.add_layout(color_bar, 'right')



p.select_one(HoverTool).tooltips = [
	('date', '@hour h @day December'),
	('rate', '@rate events')
 ]

text = Div(text="""
<img src="http://elearning.fct.unl.pt/elearning/files/fct02.jpg" style="width:128px;height:32px;">
<img src="http://www.fct.unl.pt/sites/default/files/logo_libphys.png?1435070107" style="width:64px;height:32px;">
<br />
<b style="font-size:200%;">David Collections</b>
<br />
<b>User_id: </b>""" + str(sum(rate)) + """ messages
<br />
<b>Total Nbr of Sessions: </b>""" + str(TotalSession) + """ sessions
<br />
<b>Higher Time Spent on Session:</b> """ + str(int(MaxDuration/60)) + """ minutes""")

# callback = CustomJS(code='''
# window.alert(hello)
# ''')

TextBox = Button(label='Session1', width = 50)
Left = AbstractButton(label='<', width = 5)
Right = AbstractButton(label='>', width = 5)
TapToolData = ColumnDataSource(dict(hour = [], day = []))
taptool = p.select(type=TapTool)
taptool.callback = CustomJS(args=dict(source=TapToolData, Obj=TextBox), code='''
source['hour'] = cb_data['geometries'][0]['y']
source['day'] = cb_data['geometries'][0]['x']
Obj.label = "Session on Day " + cb_data['geometries'][0]['x']
source.trigger('change')
Obj.trigger('change')
console.log(source['hour'])
''')

rslider = RangeSlider(start = 0, end = 10, step=1, orientation='horizontal', range=(0,10))

l = layout([text], [p], [Left, TextBox, Right], [p1], [rslider], sizing_mode="scale_width")

curdoc().add_root(l)
main_session.show(l)
main_session.loop_until_closed()