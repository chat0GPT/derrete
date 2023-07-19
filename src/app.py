
#------------------------------------------------------------------------------
# DERRETE MBL
#------------------------------------------------------------------------------

# Libraries....................................................................
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime

# Import data..................................................................
path = 'https://raw.githubusercontent.com/chat0GPT/derrete/main/derretembl.csv'

df = pd.read_csv (path)

# Fix Date format
df["Data"] = pd.to_datetime(df["Data"], format='%d/%m/%Y')

df['Diferenca'] = ''
df.loc[0,'Diferenca']=0
for x in range(1,len(df['Seguidores'])):
    df.loc[x,'Diferenca'] = df.loc[x,'Seguidores']-df.loc[x-1,'Seguidores']

df['Diferenca'] = df['Diferenca'].astype(int)

perda_total = abs(sum(df.Diferenca[(df['Diferenca'] <0)]))

timedel = df['Data'].iloc[-1] - df['Data'].iloc[-2]
taxa = (df['Seguidores'].iloc[-1] - df['Seguidores'].iloc[-2])/(timedel.days)
if taxa <= 0:
    titulo = 'derretimento'
else:
    titulo = 'crescimento'


## adding a column with colors
df["Color"] = np.where(df["Diferenca"] < 0, 'red', 'green')

#for slider
df['Mes_Ano'] = ''
for x in range(0,len(df['Data'])):
    df.loc[x,'Mes_Ano'] = '{}-{}'.format(df.loc[x,'Data'].date().month,df.loc[x,'Data'].date().year)

dic_dates = {i: str(x) for i,x in enumerate(df['Mes_Ano'].unique())}
dic_keys = (list(dic_dates.keys()))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# App layout...................................................................
app.layout = dbc.Container(children=[

    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.Img(src='https://github.com/chat0GPT/derrete/blob/main/assets/derrete_logo.jpg?raw=true', 
                                     alt='Derrete MBL com uma imagem de vela derretendo', 
                                     style={'height':'100px'}),],style={'text-align' : 'center',
                                                                        'margin' : '10px 10px 10px 10px'})
                        ),
                    dbc.Col(
                        html.Div([
                        html.Br(),
                        html.H5('* Último dado: {}/{}/{} -- {} mucilons '.format(df['Data'].iloc[-1].date().day,
                                                           df['Data'].iloc[-1].date().month,
                                                           df['Data'].iloc[-1].date().year,
                                                           df['Seguidores'].iloc[-1])+'\N{baby}'),
                        html.H5('* Perda total desde início: {} pessoas completaram 18 anos '.format(
                                                           perda_total)+'\N{man}'),
                        html.H5('* Taxa atual de {}: {:.2f} seguidores por dia'.format(
                                                           titulo,taxa))                                 
                        ]), lg=8
                        ),                                           
                ])
            ]),
            dcc.Graph(id='grafico'), 
            dcc.RangeSlider(id='slider',
                min=dic_keys[0],
                max=dic_keys[-1],
                marks=dic_dates,
                step=None,
                value=[dic_keys[-5],dic_keys[-1]],
                allowCross=False
            )
        ],style={'margin' : '20px 20px 20px 20px'}),
        html.Br(),
    ])
])


# Callback ....................................................................

@app.callback(
    Output(component_id='grafico', component_property='figure'),
    Input(component_id='slider', component_property='value'))
def graficuzinho(selection):
    inicio = datetime.strptime('01-'+dic_dates[selection[0]],'%d-%m-%Y')
    fim = datetime.strptime('30-'+dic_dates[selection[1]],'%d-%m-%Y')
    df_filter = df[(df['Data'] >= inicio) & (df['Data'] <= fim)]
    
    fig = make_subplots(rows=2, cols=1,shared_xaxes=True,
                    vertical_spacing=0.01, row_heights=[0.2, 0.8])
    
    fig.add_trace(go.Bar(x=df_filter['Data'], y=df_filter['Diferenca'], 
                     marker_color= df_filter['Color'],hoverlabel=dict(namelength=0)),
                     row=1, col=1)
    fig.update_yaxes(title='Diferença',row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df_filter['Data'], y=df_filter['Seguidores'], 
                             mode='lines+markers', line=dict(color="#0000ff"),
                             hoverlabel=dict(namelength=0)),
                        row=2, col=1)
    fig.update_yaxes(title='Seguidores',row=2, col=1)
    fig.update_xaxes(title='Data',row=2, col=1)
    
    fig.update_layout(showlegend=False, margin=dict(l=20,r=20,t=30,b=20), height=500)
    return fig

# .............................................................................
if __name__ == '__main__':
    app.run_server(debug=False)
    
