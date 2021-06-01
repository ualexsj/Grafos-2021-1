
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input


df = pd.read_csv('estados.csv')
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
#df.sort_values("Date", inplace=True)
data01 = df.drop(["codigo_uf", "uf", "nome","Date","capital"], axis=1)
daux=data01.values

# Calcule a distância euclidiana no espaço n da rota r que atravessa as cidades c, terminando no início do caminho.
caminho_distancia = lambda r,c: np.sum([np.linalg.norm(c[r[p]]-c[r[p-1]]) for p in range(len(r))])

# Inverta a ordem de todos os elementos do elemento i para o elemento k na matriz r.
two_opt_swap = lambda r,i,k: np.concatenate((r[0:i],r[k:-len(r)+i-1:-1],r[k+1:len(r)]))

def two_opt(cidades,melhor_threshold): # 2-opt Algorithm adaptado de https://en.wikipedia.org/wiki/2-opt
    rota = np.arange(cidades.shape[0]) # Faça uma matriz de números de linha correspondendo a cidades.
    melhor_factor = 1 # Inicializar o fator de melhoria.
    a_melhor_distancia = caminho_distancia(rota,cidades) # Calcule a distância do caminho inicial.
    while melhor_factor > melhor_threshold: # Se a rota ainda estiver melhorando, continue!
        distancia_to_beat = a_melhor_distancia # Registre a distância no início do loop.
        for swap_first in range(1,len(rota)-2): # # De cada cidade, exceto a primeira e a última,
            for swap_last in range(swap_first+1,len(rota)): # para cada uma das seguintes cidades,
                    nova_rota = two_opt_swap(rota,swap_first,swap_last) # tente inverter a ordem dessas cidades
                    nova_distancia = caminho_distancia(nova_rota,cidades) # e verifique a distância total com esta modificação.
                    if nova_distancia < a_melhor_distancia: # Se a distância do caminho for uma melhoria,
                            rota = nova_rota # torna esta a melhor rota aceita
                            a_melhor_distancia = nova_distancia # e atualize a distância correspondente a esta rota.
        melhor_factor = 1 - a_melhor_distancia/distancia_to_beat # Calcule o quanto a rota melhorou.
    return rota # Quando a rota não estiver mais melhorando substancialmente, pare de pesquisar e retorne a rota.


# Crie uma matriz de cidades, com cada linha sendo um local em 2 espaços (a função funciona em n dimensões).
#cidades = np.random.RandomState(42).rand(70,2)
cidades=daux
# Encontre uma boa rota com 2-opt ("rota" fornece a ordem de viagem para cada cidade por número de linha.)
rota = two_opt(cidades,0.001)

import matplotlib.pyplot as plt
# Reordene a matriz de cidades por ordem de rota em uma nova matriz para plotagem.
nova_cidades_ordem = np.concatenate((np.array([cidades[rota[i]] for i in range(len(rota))]),np.array([cidades[0]])))

# Print a rota como números de linha e a distância total percorrida pelo caminho.
#print("rota: " + str(rota) + "\n\ndistancia: " + str(caminho_distancia(rota,cidades)))

df_right=df
lon = pd.DataFrame(nova_cidades_ordem[:,1])
lat = pd.DataFrame(nova_cidades_ordem[:,0])
df_right['CX_lon']=lon
df_right['CX_lat']=lat


xre=[]
xre=pd.DataFrame(xre, columns=['uf','nome','longitude','latitude','Date','capital']) # criando um pandas vazio
for i in range(len(df_right)):
    atual1 =df_right.iloc[i,7]
    atual2 =df_right.iloc[i,8]
    for j in range(len(df_right)):
        anterior1=df_right.iloc[j,4]
        anterior2=df_right.iloc[j,3]
        if anterior1 == atual1 and anterior2 == atual2 :
          estado = df_right.iloc[j,1]
          city = df_right.iloc[j,2]
          Date = df_right.iloc[j,5]
          capital = df_right.iloc[j,6]
          xre=xre.append({'uf':estado,'nome':city,'longitude':atual1, 'latitude':atual2,'Date':Date,'capital':capital},ignore_index=True) 


#data= xre
data = df
data01 = xre

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🥑", className="header-emoji"),
                html.H1(
                    children="GRAFOS: Two-opt", className="header-title"
                ),
                html.P(
                    children="Grafo utilizando o Two-opt",
                    className="header-description",
                ),
            ], 
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="uf", className="menu-title"),
                        dcc.Dropdown(
                            id="uf-filter",
                            options=[
                                {"label": uf, "value": uf}
                                for uf in np.sort(data01.uf.unique())
                            ],
                            value="Estados",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="capital", className="menu-title"),
                        dcc.Dropdown(
                            id="capital-filter",
                            options=[
                                {"label": avocado_type, "value": avocado_type}
                                for avocado_type in data01.capital.unique()
                            ],
                            value="0",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.Date.min().date(),
                            max_date_allowed=data.Date.max().date(),
                            start_date=data.Date.min().date(),
                            end_date=data.Date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure")],
    [
        Input("uf-filter", "value"),
        Input("capital-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)

def update_charts(uf, avocado_type, start_date, end_date):
 
    mask = (
        (data.uf == uf)
        & (data.capital == avocado_type)
        & (data.Date >= start_date)
        & (data.Date <= end_date)
    )
        #filtered_data = data.loc[mask, :]
    filtered_data_t = data.loc[mask, :]
    filtered_data =  filtered_data_t.append(filtered_data_t[:1],ignore_index=True)
    
    mask01 = (
        (data01.uf == uf)
        & (data01.capital == avocado_type)
        & (data01.Date >= start_date)
        & (data01.Date <= end_date)
    )

    filtered_data_t_01 = data01.loc[mask01, :]
    filtered_data_01 =  filtered_data_t_01.append(filtered_data_t_01[:1],ignore_index=True)
    
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["longitude"],
                "y": filtered_data["latitude"],
                "showlegend": False,
                "type": "lines",
                "mode": "markers+lines+text",
                "marker": dict(size=20, color='red'),
                "textposition" :'top right',
                "textfont": dict(size=1, color='white'),
                "text": filtered_data["nome"],
                #"hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "GRAFO ORIGINAL",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],

        },
    }
    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data_01["longitude"],
                "y": filtered_data_01["latitude"],
                "showlegend": False,
                "type": "lines",
                "mode": "markers+lines+text",
                "marker": dict(size=20, color='blue'),
                "textposition" :'top right',
                "textfont": dict(size=1, color='white'),
                "text": filtered_data_01["nome"],
            },
        ],
        "layout": {
            "title": {
            "text": "GRAFO UTILIZANDO O TWO-OPT"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure

 
if __name__ == "__main__":
    app.run_server(debug=True)

