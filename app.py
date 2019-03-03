# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output,Input,State
from dash.exceptions import PreventUpdate
import plotly
import random
import plotly
from collections import deque
import sqlite3
import pandas as pd
import datetime as dt

app = dash.Dash(__name__)
app.layout = html.Div(html.Div(
    [
        html.H2('Live Twitter sentiment'),
        dcc.Input(id='sentiment_term', value='olympic', type='text'),
        dcc.Graph(id='live-graph'),
        dcc.Interval(
            id='interval-component',
            interval=2*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-graph', 'figure'),
              [Input('sentiment_term',component_property='value'),
              Input('interval-component', 'n_intervals')]
)
def update_graph_scatter(sentiment_term,n_intervals):
    try:
        start = dt.datetime.now()
        conn = sqlite3.connect('/Users/nicolasvandermaas/Documents/Coding/Notebooks/twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix ASC LIMIT 1000",conn, params=('%' + sentiment_term + '%',))
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df['time'] = pd.to_datetime(df['unix'], unit='ms')
        df.dropna(inplace=True)
        end = dt.datetime.now()
        print 'took %s'%((end-start).total_seconds())

        X=df.time.iloc[-100:]
        Y=df.sentiment_smoothed.values[-100:]

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data]}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')
        return []

if __name__ == '__main__':
    app.run_server(debug=True)

