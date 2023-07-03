#!/usr/bin/python3
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback

app = Dash(__name__)

app.layout = html.Div(
	[
		"Click to swith data:",
		html.Button('Switch data', id='switch', n_clicks=0),
		dcc.Graph(id='chart', config={'displayModeBar': False}),		
	]
)

@callback(
	Output('chart', 'figure'),
	Output('switch', 'children'),
	Input('switch', 'n_clicks')
)
def on_switch(n_clicks):
	if n_clicks % 2:
		path = 'ohlc-data1.json'
	else:
		path = 'ohlc-data.json'
	# Read data from file and build the OHLC series.
	srcdf = pd.read_json(path)
	sr = srcdf.groupby('DateTime').Close.last()
	ohlc = sr.resample('5min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
	# Now create the figure and return it.
	fig = go.Figure(layout=dict(width=800, height=600))
	fig.add_trace(go.Candlestick(x=ohlc.index, open=ohlc.Open, high=ohlc.High, low=ohlc.Low, close=ohlc.Close))
	return fig, path

if __name__ == '__main__':
	app.run(debug=True)