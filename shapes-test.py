#!/usr/bin/python3
import os
import json
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate

data_path = 'ohlc-data.json'
uirevision = 1

app = Dash(__name__)

app.layout = html.Div(
	[
		html.Button('Toggle timeframe', id='timeframe', n_clicks=0),
		html.Button('Save shapes', id='save', n_clicks=0),
		html.Label('', id='info'),
		dcc.Graph(
			id='chart',
			config=dict(
				displayModeBar=True,
				modeBarButtonsToAdd=[
					'drawline',
					'drawopenpath',
					'drawcircle',
					'drawrect',
					'eraseshape'
				]
			)
		),		
	]
)

# Display an candlestick chart with shapes loaded from file.
@callback(
	Output('chart', 'figure'),
	Output('timeframe', 'children'),
	Input('timeframe', 'n_clicks')
)
def on_timeframe(n_clicks):
	if n_clicks % 2:
		tf = '5min'
	else:
		tf = '15min'
	# Read data from file and build the OHLC series.
	srcdf = pd.read_json(data_path)
	sr = srcdf.groupby('DateTime').Close.last()
	ohlc = sr.resample(tf).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
	# NOTE: NaNs messes up candlesticks, let's remove them.
	ohlc.dropna(inplace=True)
	# Create a figure with a candlestick chart using the above OHLCD data.
	fig = go.Figure(layout=dict(width=800, height=600, uirevision=uirevision))
	fig.add_trace(go.Candlestick(x=ohlc.index, open=ohlc.Open, high=ohlc.High, low=ohlc.Low, close=ohlc.Close))
	# Now add saved shapes (only once at page load).
	if n_clicks == 0:
		path = 'shapes.json'
		if os.path.isfile(path):
			with open(path , 'r') as f:
				shapes = json.load(f)
			if len(shapes):
				for shape in shapes:
					fig.add_shape(shape)
	return fig, tf

# Save existing 'editable' shapes to file.
@callback(
	Output('info', 'children'),
	Input('save', 'n_clicks'),
	State('chart', 'figure')
)
def on_save(n_clicks, fig):
	if n_clicks:
		if 'shapes' in fig['layout'].keys():
			shapes = []
			for shape in fig['layout']['shapes']:
				if shape is not None and 'editable' in shape.keys():
					shapes.append(shape)
			if len(shapes):
				path = 'shapes.json'
				print(f'Saving {len(shapes)} shapes to {path}')
				with open(path, 'w') as f:
					json.dump(shapes, f)
				return f"{len(shapes)} shapes were saved to {path}"
		return "No shape to save"
	else:
		raise PreventUpdate

if __name__ == '__main__':
	app.run(debug=True)