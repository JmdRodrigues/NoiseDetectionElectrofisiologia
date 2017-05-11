from bokeh.models.widgets import Div


def Header(Name, User_id, NbrofSessions, MaxDuration):
	header = Div(text="""
	<img src="http://elearning.fct.unl.pt/elearning/files/fct02.jpg" style="width:128px;height:32px;">
	<img src="http://www.fct.unl.pt/sites/default/files/logo_libphys.png?1435070107" style="width:64px;height:32px;">
	<br />
	<b style="font-size:200%;">""" + Name + """</b>
	<br />
	<b>User_id: </b>""" + User_id + """
	<br />
	<b>Total Nbr of Sessions: </b>""" + str(NbrofSessions) + """ sessions
	<br />
	<b>Higher Time Spent on Session:</b> """ + str(int(MaxDuration/60)) + """ minutes""")

	return header

def MoustrackingPad():
	mouse = Div(text='''
	''')
	return mouse