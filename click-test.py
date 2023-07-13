#!/usr/bin/python3
# This sample demonstrate click event handling in Plotly Dash.
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback

# Read data from file and build the OHLC dataframe.
series = pd.read_json('ohlc-data.json').groupby('DateTime').Close.last()
ohlc = series.resample('5min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
fig = go.Figure(layout=dict(width=800, height=600, xaxis=dict(rangeslider_visible=False)))
fig.add_trace(go.Candlestick(x=ohlc.index, open=ohlc.Open, high=ohlc.High, low=ohlc.Low, close=ohlc.Close))

app = Dash(__name__)

app.layout = html.Div(
	[
		html.Label(
			"Click anywhere on the chart",
			id='label'
		),
		dcc.Graph(
			id='chart',
      figure=fig,
			config=dict(displayModeBar=True, modeBarButtonsToAdd=['drawline', 'eraseshape'])
		),		
	]
)

@callback(
		Output('label', 'children'),
		Input('chart', 'clickData'),
		prevent_initial_call=True
)
def callback_on_click(click_data):
	return str(click_data)

app.run(debug=True)