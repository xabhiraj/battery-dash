##Author: AR 
##Date Started: 20180413
##pithytimeout=1800
##Notes: Upcoming feature: append persistent traces using clickdata. store values in a list and push using a button. see https://dash.plot.ly/dash-core-components for dcc options

from pithy import *
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

#####################################################################
#####################################################################
#load neware raw data into rd
rd = pd.read_csv('files/example.csv')
rd = rd.rename(index=str, columns={'test_vol': 'Voltage (V)', 'test_cur': 'Current (A)'})

#process df and store max value for each cycle into 'data'
cyc,qch,qdh,ech,edh = [],[],[],[],[]
for cycle in range(int(max(rd['cycle'])+1)):
    cyc.append(cycle+1)
    qch.append(max(rd[(rd['cycle']==cycle)]['test_capchg']))
    qdh.append(max(rd[(rd['cycle']==cycle)]['test_capdchg']))
    ech.append(max(rd[(rd['cycle']==cycle)]['test_engchg']))
    edh.append(max(rd[(rd['cycle']==cycle)]['test_engdchg']))
data = pd.DataFrame([cyc,qch,qdh,ech,edh]).T
data.columns = ['cyc','Max capacity, charging (Ah)','Max capacity, discharging (Ah)','Max energy, charging (Wh)','Max energy, discharging (Wh)']

# process df and store dqdv data into dqdv
dqdv=pd.DataFrame()
for cycle in range(int(max(rd['cycle'])+1)):
    ways = ['test_capdchg','test_capchg']
    for w in range(len(ways)):
        way = ways[w]
        v = rd[(rd['cycle']==cycle) & (rd[way]!=0)]['Voltage (V)']
        c = rd[(rd['cycle']==cycle) & (rd[way]!=0)][way]
        foo = pd.DataFrame({'cycle':cycle,'way':way,'voltage':v[:-1],'dqdv':diff(c)/diff(v)})
        dqdv = pd.concat([dqdv,foo])

#declaring dash app
app = dash.Dash()


#####################################################################
#####################################################################
#this is where the layout of the html page is organized
app.layout = html.Div([
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='cycling-data-column',
                options=[{'label': i, 'value': i} for i in data.columns[1:]],
                value='Max capacity, discharging (Ah)'
            )
        ], style={'width': '43%', 'display': 'inline-block','padding-right':'20px'}),
    
        html.Div([
            dcc.Dropdown(
                id='single-data-column',
                options=[{'label': i, 'value': i} for i in [rd.columns.tolist()[i] for i in [2,3]]],
                value='Voltage (V)'
            )
        ], style={'width': '43%', 'display': 'inline-block'}),
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '20px 20px'
    }),

    html.Div([
        dcc.Graph(id='cycling-data')
    ],style={'width':'45%', 'display':'inline-block'}),

    html.Div([
        dcc.Graph(id='single-data')
    ],style={'width':'45%', 'display':'inline-block'}),
    
    html.Div([
        dcc.Graph(id='qchg-data'),
        dcc.Graph(id='qdchg-data'),
    ],style={'width':'45%', 'display':'inline-block'}),
    
    html.Div([
        dcc.Graph(id='dqdv-data'),
    ],style={'width':'45%', 'display':'inline-block'})
])

#####################################################################
#####################################################################
#this callback passes dropdown #1 value to the cycling-data figure
@app.callback(
    dash.dependencies.Output('cycling-data', 'figure'),
    [dash.dependencies.Input('cycling-data-column', 'value')])
def update_graph(yaxis_value):
    return {
        'data': [go.Scatter(
            x= data['cyc'],
            y= data[yaxis_value],
            mode= 'markers'
        )],
        'layout': go.Layout(
            title='Cycling capacity',
            xaxis={'title': 'Cycle'},
            yaxis={'title': yaxis_value},
            margin={'l': 100, 'b': 100, 'r': 100, 't': 100},
            height=500,
            hovermode='closest')
    }


#####################################################################
#####################################################################
#this callback passes dropdown #2 value and hoverdata from the cycling-data fig to the single-data fig
@app.callback(
    dash.dependencies.Output('single-data', 'figure'),
    [dash.dependencies.Input('cycling-data', 'hoverData'),
    dash.dependencies.Input('single-data-column', 'value')]
    )
def display_voltage(hoverData,yaxis_value):
    try:
        xval = hoverData['points'][0]['x']
    except TypeError:
        xval = 1
        print 'Initializing single data plot to first cycle'
    return {
        'data': [go.Scatter(
            x=rd[(rd['cycle']==xval-1)]['unix_time'],
            y=rd[(rd['cycle']==xval-1)][yaxis_value],
            mode='markers'
        )],
        'layout': go.Layout(
            title='Single Cycle Data (Cycle: '+str(xval)+')',
            xaxis={'title': 'Time (since epoch)'},
            yaxis={'title': yaxis_value},
            margin={'l': 100, 'b': 100, 'r': 100, 't': 100},
            height=500
        )
    }


#####################################################################
#####################################################################
#the next two callbacks pass the hoverdata from the cycling plot and use the capvolt method to send a plot to the graph components above
def plot_capvolt(ways, xval, title):
    return {
        'data': [go.Scatter(
            x=rd[(rd['cycle']==xval-1)&(rd[ways]!=0)][ways],
            y=rd[(rd['cycle']==xval-1)&(rd[ways]!=0)]['Voltage (V)'],
            mode='markers'
        )],
        'layout': go.Layout(
            title=title+' (Cycle: '+str(xval)+')',
            xaxis={'title': 'Capacity (Ah)'},
            yaxis={'title': 'Voltage (V)'},
            margin={'l': 100, 'b': 100, 'r': 100, 't': 50},
            height=250
        )
    }
@app.callback(
    dash.dependencies.Output('qchg-data', 'figure'),
    [dash.dependencies.Input('cycling-data', 'hoverData')]
    )
def display_qchg(hoverData):
    try:
        xval = hoverData['points'][0]['x']
    except TypeError:
        xval = 1
        print 'Initializing charging plot to first cycle'
    return plot_capvolt('test_capchg', xval, 'Charging')
@app.callback(
    dash.dependencies.Output('qdchg-data', 'figure'),
    [dash.dependencies.Input('cycling-data', 'hoverData')]
    )
def display_qdchg(hoverData):
    try:
        xval = hoverData['points'][0]['x']
    except TypeError:
        xval = 1
        print 'Initializing discharging plot to first cycle'
    return plot_capvolt('test_capdchg', xval, 'Discharging')


#####################################################################
#####################################################################
#this callback passes dq/dv for a single hovered cycle to the dqdv graph component above
@app.callback(
    dash.dependencies.Output('dqdv-data', 'figure'),
    [dash.dependencies.Input('cycling-data', 'hoverData')]
    )
def display_dqdv(hoverData):
    try:
        xval = hoverData['points'][0]['x']
    except TypeError:
        xval = 1
        print 'Initializing dQ/dV plot to first cycle'
    return {
        'data': [go.Scatter(
            x=dqdv[(dqdv['cycle']==xval-1)]['voltage'],
            y=dqdv[(dqdv['cycle']==xval-1)]['dqdv'],
            mode='markers'
        )],
        'layout': go.Layout(
            title='dQ/dV (Cycle: '+str(xval)+')',
            xaxis={'title': 'Voltage (V)'},
            yaxis={'title': 'dQ/dV (Ah)'},
            margin={'l': 100, 'b': 100, 'r': 100, 't': 40},
            height=500
        )
    }


#####################################################################
#####################################################################


if __name__ == '__main__':
    app.run_server(port=8050,host="0.0.0.0")
    
