#!/usr/bin/env python3

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import flask
import pandas as pd
import time
import os, sys

from lib import tuilib, visualization_lib
from os import listdir
from os.path import isfile, join

AC_NAME = "BETSTEST"

# connection to assetchain
rpc_connection = tuilib.def_credentials(AC_NAME)

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

# pre-creating needed csv files on user side
visualization_lib.create_prices_csv(rpc_connection, "725")
visualization_lib.create_delayed_prices_csv(rpc_connection, "580")
visualization_lib.create_csv_with_bets(rpc_connection, "open")
visualization_lib.create_csv_with_bets(rpc_connection, "closed")

# pre-creating tickers for graph
pair_names = visualization_lib.get_pairs_names(rpc_connection)
options_arg = []
for pair in pair_names:
    pair_arg = {}
    pair_arg['label'] = pair
    pair_arg['value'] = pair
    options_arg.append(pair_arg)

user_args = []
graphs_files_list = [f for f in listdir('usergraphs') if isfile(join('usergraphs', f))]
for file in graphs_files_list:
    file_arg = {}
    file_arg['label'] = file
    file_arg['value'] = file
    user_args.append(file_arg)

# and load it into dash to draw graphs and etc
df = pd.read_csv('prices.csv')
df2 = pd.read_csv('delayed_prices.csv')
df3 = pd.read_csv('betlist.csv')
df4 = pd.read_csv('betlist_history.csv')

# amount of records per table page
PAGE_SIZE = 15

# application object
app = dash.Dash(__name__, server=server, static_folder='static')

# init configuration, second param allow to make dynamic callbacks
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

# static layout
app.layout = html.Div([
    html.Link(href='/static/undo-redo.css', rel='stylesheet'),
    html.Title("PricesCC trading web-interface"),
    html.H5("Pairs from prices RPC call:"),
    dcc.Dropdown(
        id='my-dropdown',
        options=options_arg,
        value='BTC_USD'),
#    html.H5("User custom prices:"),
#     dcc.Dropdown(
#         id='user-dropdown',
#         options=user_args,
#         value=user_args[0]),
    dcc.Loading(dcc.Graph(id='my-graph')),
    html.Br(),
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


# getting data from blockchain and rendering graph
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
        # {
        #     'x': dff2.date,
        #     'y': dff.price3,
        #     'line': {
        #         'width': 3,
        #         'shape': 'spline'
        #     }
        # }
        ],
        'layout': {
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                #'t': 20
            },
            'title': 'Prices provided by Komodo PricesCC trustless oracle'
        }
    }

# loading local static files from static dir
@app.server.route('/assets/<path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return flask.send_from_directory(static_folder, path)


# tabs content rendering
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    # tab 1 is bets constructor
    if tab == 'tab-1':
        # left side of first tab
        return html.Div([
            html.Br(),
            html.H5('User balance: ' + str(rpc_connection.getinfo()['balance']) + " " + AC_NAME),
            html.Div(id='output-container-button',
                     children='Enter values and press submit', style={'marginBottom': 5, 'marginTop': 5, 'font-size': '16px'}),
            dcc.Input(
                placeholder='Input bet amount...',
                type='text',
                value='',
                id='betamount_text',
                style={'marginBottom': 10, 'marginTop': 10}
            ),
            html.Br(),
            dcc.Input(
                placeholder='Input leverage...',
                type='text',
                value='',
                id='leverage_text',
                style={'marginBottom': 10, 'marginTop': 10}
            ),
            html.Br(),
            dcc.Input(
                placeholder='Input synthetic...',
                type='text',
                value='',
                id='synthetic_text',
                style={'marginBottom': 15, 'marginTop': 10}
            ),
            html.Br(),
            html.Button('Open position', id='button', style={'marginBottom': 25})], style={'width': '50%', 'float': 'left'}),\
                  html.Div([html.Div(id='daemon_ouptut',
                     children='Daemon output print', style={'marginBottom': 10, 'marginTop': 15})], style={'width': '50%', 'float': 'right'})
    # tab 2 displaying active positions with possibility to add leverage or close it
    elif tab == 'tab-2':
        visualization_lib.create_csv_with_bets(rpc_connection, "open")
        df3 = pd.read_csv('betlist.csv')
        return html.Div([
            html.H5('User balance: ' + str(rpc_connection.getinfo()['balance']) + " " + AC_NAME),
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df3.columns],
                data=df3.to_dict("rows"),
                sorting=True,
                row_selectable='single',
                selected_rows=[],
                style_cell={
                    'minWidth': '0px', 'maxWidth': '240px',
                    'whiteSpace': 'normal'
                },
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                }],
                pagination_settings={
                                        'current_page': 0,
                                        'page_size': PAGE_SIZE,
                                    }
            ),
            html.H5("Select position to add funding or close it"),
            html.Div(id='position-select-container', children='', style={'marginBottom': 10, 'marginTop': 15}),
            dcc.Input(
                placeholder='Input funding...',
                type='text',
                value='',
                id='funding_text',
                style={'marginBottom': 10, 'marginTop': 10}
            ),
            html.Button('Add funding', id='funding-button'),
            html.Button('Cashout position', id='close-button', style={'marginBottom': 100}),
            html.Div(id='position-closing-output', style={'width': '50%', 'float': 'right'}),
            html.Div([html.Div(id='daemon_ouptut2',
                               children='Daemon output print', style={'marginBottom': 10, 'marginTop': 15})],
                     style={'width': '50%', 'float': 'right'})
        ])
    # tab 3 displaying bet history (closed bets)
    elif tab == 'tab-3':
        visualization_lib.create_csv_with_bets(rpc_connection, "closed")
        df4 = pd.read_csv('betlist_history.csv')
        return html.Div([
            dash_table.DataTable(
                id='table_history',
                columns=[{"name": i, "id": i} for i in df4.columns],
                data=df4.to_dict("rows"),
                sorting=True,
                selected_rows=[],
                style_cell={
                    'minWidth': '0px', 'maxWidth': '320px',
                    'whiteSpace': 'normal'
                },
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                }],
                pagination_settings={
                                        'current_page': 0,
                                        'page_size': PAGE_SIZE,
                                    }
            )
        ])

# bet placing button callback
@app.callback(Output('daemon_ouptut', 'children'), [Input('button', 'n_clicks')],
              [State('betamount_text', 'value'), State('leverage_text', 'value'), State('synthetic_text', 'value')])
#TODO: have to add confirmation popup
def on_click(n_clicks, betamount, leverage, synthetic):
    try:
        if n_clicks > 0:
            daemon_output = rpc_connection.pricesbet(betamount, leverage, synthetic)
            try:
                position_txid = rpc_connection.sendrawtransaction(daemon_output['hex'])
                return str(daemon_output) + "\n transaction broadcasted: " + str(position_txid)
            except KeyError:
                return str(daemon_output) + "\n transaction not broadcasted, please check error above"
        else:
            pass
    except TypeError:
        pass

# callback on radio select on tab2
@app.callback(
    Output('position-select-container','children'),
    [Input('table', 'derived_virtual_data'),
     Input('table', 'derived_virtual_selected_rows')])
def update_position_selection(rows,derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    if rows is None:
        dff3 = df3
    else:
        dff3 = pd.DataFrame(rows)
    try:
        active_row_txid = dff3['txid'][derived_virtual_selected_rows[0]]
        return html.Div([
            html.H5("Selected position: " + active_row_txid),
            html.Div(id='active_row_txid', children=active_row_txid, style={'display': 'none'})
            ]
        )
    except Exception as e:
        pass

# addfunding button callback
@app.callback(Output('daemon_ouptut2', 'children'), [Input('funding-button', 'n_clicks')],
              [State('active_row_txid', 'children'),State('funding_text', 'value')])
#TODO: have to add confirmation popup
def on_click(n_clicks, txid, funding_amount):
    if n_clicks > 0:
        daemon_output = rpc_connection.pricesaddfunding(str(txid), str(funding_amount))
        try:
            position_txid = rpc_connection.sendrawtransaction(daemon_output['hex'])
            return str(daemon_output) + "\n transaction broadcasted: " + str(position_txid)
        except KeyError:
            return str(daemon_output) + "\n transaction not broadcasted, please check error above"
    else:
        pass


# closeposition button callback
@app.callback(Output('position-closing-output', 'children'), [Input('close-button', 'n_clicks')],
              [State('active_row_txid', 'children')])
#TODO: have to add confirmation popup
def on_click(n_clicks, txid):
    if n_clicks > 0:
        daemon_output = rpc_connection.pricessetcostbasis(str(txid))
        try:
            costbasis_txid = rpc_connection.sendrawtransaction(daemon_output['hex'])
        finally:
            daemon_output = rpc_connection.pricescashout(str(txid))
            try:
                cashout_txid = rpc_connection.sendrawtransaction(daemon_output['hex'])
                return str(daemon_output) + "\n transaction broadcasted: " + str(cashout_txid)
            except KeyError:
                return str(daemon_output) + "\n transaction not broadcasted, please check error above"
    else:
        pass

if __name__ == '__main__':
    app.run_server(host = '0.0.0.0', port=777, debug=True)
