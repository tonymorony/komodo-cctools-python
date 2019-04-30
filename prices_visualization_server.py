#!/usr/bin/env python3

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import pandas as pd
import time
import os

from lib import tuilib, visualization_lib

rpc_connection = tuilib.def_credentials("REKT0")
server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

visualization_lib.make_csv_for_stack(rpc_connection, ["BTC_USD", "KMD_BTC", "*", 1], "BTC_USD*KMD_BTC", "435")

df = pd.read_csv('BTC_USD*KMD_BTC.csv')


app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False

pair_names = ["BTC_USD*KMD_BTC"]

options_arg = []
for pair in pair_names:
    pair_arg = {}
    pair_arg['label'] = pair
    pair_arg['value'] = pair
    options_arg.append(pair_arg)

app.layout = html.Div([
    html.H1('Prices provided by Komodo PricesCC trustless oracle'),
    dcc.Dropdown(
        id='my-dropdown',
        options=options_arg,
        value='BTC_USD*KMD_BTC'
    ),
    dcc.Graph(id='my-graph')
], className="container")

@app.callback(Output('my-graph', 'figure'),
              [Input('my-dropdown', 'value')])

def update_graph(selected_dropdown_value):

    visualization_lib.make_csv_for_stack(rpc_connection, ["BTC_USD", "KMD_BTC", "*", 1], "BTC_USD*KMD_BTC", "435")
    df = pd.read_csv('BTC_USD*KMD_BTC.csv')

    dff = df[df['pair'] == selected_dropdown_value]
    return {
        'data': [

        {
        'x': dff.date,
        'y': dff.price1,
        'line': {
            'width': 3,
            'shape': 'spline'
        }
        },

        {
            'x': dff.date,
            'y': dff.price2,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        },

        {
            'x': dff.date,
            'y': dff.price3,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        },
        ],
        'layout': {
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                't': 20
            }
        }
    }


if __name__ == '__main__':
    app.run_server(host = '0.0.0.0')
