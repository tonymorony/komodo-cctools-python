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

visualization_lib.create_prices_csv(rpc_connection, "725")
visualization_lib.create_delayed_prices_csv(rpc_connection, "580")

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
    html.Title("PricesCC trading web-interface"),
    html.H4('Prices provided by Komodo PricesCC trustless oracle',  style={'marginBottom': 25, 'marginTop': 25}),
    dcc.Dropdown(
        id='my-dropdown',
        options=options_arg,
        value='BTC_USD'),
    dcc.Loading(dcc.Graph(id='my-graph')),
    html.Br(),
    html.H5('User balance: ' + str(rpc_connection.getbalance()) + " REKT0"),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        # positions constructor, user should be able to see balance
        dcc.Tab(label='Open position', value='tab-1'),
        # active positions, user should be able to see position details and add funding
        dcc.Tab(label='Active positions', value='tab-2'),
        # history with closed positions
        dcc.Tab(label='Closed positions (history)', value='tab-3'),
        ]),
    html.Div(id='tabs-content'),
], className="container")


@app.callback(Output('my-graph', 'figure'),
              [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    visualization_lib.create_prices_csv(rpc_connection, "725")
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

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Br(),
            html.Div(id='output-container-button',
                     children='Enter values and press submit', style={'marginBottom': 10, 'marginTop': 10}),
            dcc.Input(
                placeholder='Input bet amount...',
                type='text',
                value='',
                id='betamount-input',
                style={'marginBottom': 10, 'marginTop': 15}
            ),
            html.Br(),
            dcc.Input(
                placeholder='Input leverage...',
                type='text',
                value='',
                id='leverage-input',
                style={'marginBottom': 10, 'marginTop': 10}
            ),
            html.Br(),
            dcc.Input(
                placeholder='Input synthetic...',
                type='text',
                value='',
                id='synthetic-input',
                style={'marginBottom': 25, 'marginTop': 10}
            ),
            html.Br(),
            html.Button('Submit', id='button')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])


def update_csv(rpc_connection):
    while True:
        visualization_lib.create_prices_csv(rpc_connection, "725")
        visualization_lib.create_delayed_prices_csv(rpc_connection, "580")
        time.sleep(15)


if __name__ == '__main__':
    app.run_server(host = '0.0.0.0', port=777, debug=True)
