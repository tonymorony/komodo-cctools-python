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

visualization_lib.create_prices_csv(rpc_connection, "435")
visualization_lib.create_delayed_prices_csv(rpc_connection, "435")

df = pd.read_csv('prices.csv')
df2 = pd.read_csv('delayed_prices.csv')
print(type(df))

print(df)

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False

pair_names = visualization_lib.get_pairs_names(rpc_connection)

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
        value='BTCUSD'
    ),
    dcc.Graph(id='my-graph')
], className="container")

@app.callback(Output('my-graph', 'figure'),
              [Input('my-dropdown', 'value')])

def update_graph(selected_dropdown_value):
    visualization_lib.create_prices_csv(rpc_connection, "580")
    visualization_lib.create_delayed_prices_csv(rpc_connection, "580")
    df = pd.read_csv('prices.csv')
    df2 = pd.read_csv('delayed_prices.csv')
    dff = df[df['pair'] == selected_dropdown_value]
    dff2 = df2[df2['pair'] == selected_dropdown_value]
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
        {
            'x': dff2.date,
            'y': dff.price3,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }
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
