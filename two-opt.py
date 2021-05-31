
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
path_distance = lambda r,c: np.sum([np.linalg.norm(c[r[p]]-c[r[p-1]]) for p in range(len(r))])

# Inverta a ordem de todos os elementos do elemento i para o elemento k na matriz r.
two_opt_swap = lambda r,i,k: np.concatenate((r[0:i],r[k:-len(r)+i-1:-1],r[k+1:len(r)]))

def two_opt(cities,improvement_threshold): # 2-opt Algorithm adaptado de https://en.wikipedia.org/wiki/2-opt
    route = np.arange(cities.shape[0]) # Faça uma matriz de números de linha correspondendo a cidades.
    improvement_factor = 1 # Inicializar o fator de melhoria.
    best_distance = path_distance(route,cities) # Calcule a distância do caminho inicial.
    while improvement_factor > improvement_threshold: # Se a rota ainda estiver melhorando, continue!
        distance_to_beat = best_distance # Registre a distância no início do loop.
        for swap_first in range(1,len(route)-2): # # De cada cidade, exceto a primeira e a última,
            for swap_last in range(swap_first+1,len(route)): # para cada uma das seguintes cidades,
                    new_route = two_opt_swap(route,swap_first,swap_last) # tente inverter a ordem dessas cidades
                    new_distance = path_distance(new_route,cities) # e verifique a distância total com esta modificação.
                    if new_distance < best_distance: # Se a distância do caminho for uma melhoria,
                            route = new_route # torna esta a melhor rota aceita
                            best_distance = new_distance # e atualize a distância correspondente a esta rota.
        improvement_factor = 1 - best_distance/distance_to_beat # Calcule o quanto a rota melhorou.
    return route # Quando a rota não estiver mais melhorando substancialmente, pare de pesquisar e retorne a rota.


# Crie uma matriz de cidades, com cada linha sendo um local em 2 espaços (a função funciona em n dimensões).
#cities = np.random.RandomState(42).rand(70,2)
cities=daux
# Encontre uma boa rota com 2-opt ("rota" fornece a ordem de viagem para cada cidade por número de linha.)
route = two_opt(cities,0.001)

import matplotlib.pyplot as plt
# Reordene a matriz de cidades por ordem de rota em uma nova matriz para plotagem.
new_cities_order = np.concatenate((np.array([cities[route[i]] for i in range(len(route))]),np.array([cities[0]])))

# Print a rota como números de linha e a distância total percorrida pelo caminho.
#print("Route: " + str(route) + "\n\nDistance: " + str(path_distance(route,cities)))

df_right=df
lon = pd.DataFrame(new_cities_order[:,1])
lat = pd.DataFrame(new_cities_order[:,0])
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

app.title = "GRAFOS: Two-opt!"

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

