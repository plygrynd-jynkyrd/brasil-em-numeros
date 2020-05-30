import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime
import math


def funcao_por_ano(despesas):

    df = despesas.query(
        "modalidade == 'Pago'"
    ).groupby(
        ['ano_mes', "Função"], as_index = False
    ).sum()

    df['data'] = df['ano_mes'] + "/01"
    df['data'] = pd.to_datetime(df['data'], format = '%Y/%m/%d')

    fig = go.Figure()
    hover_template = "<b>%{text}</b><br>Gasto: %{y:$,.0f}"
    funs = sorted(df['Função'].unique())
    for fun in funs:
        
        plot_data = df.loc[df['Função'] == fun]
        x = plot_data['data']
        y = plot_data['valor']
        fig.add_trace(
            go.Scatter(
                x = x,
                y = y,
                mode = "lines+markers",
                name = fun,
                text = plot_data['Função'],
                line = {'shape' : 'spline'},
                hovertemplate = hover_template
            )
        )

    fig.update_layout(yaxis_title = "Valor Pago")
    fig.update_layout(title = "Gastos por categoria")
    return fig


def gastos_por_ministerio(despesas):

    df = despesas.groupby(
        ['ano_mes', 'Órgão Superior'], as_index = False
    ).sum()

    fig  = go.Figure()

    # ----------------------
    #  Top 10 ministérios
    # ----------------------

    top10 = df.groupby(
        ['ano_mes'],
        as_index = False
    ).rank(method = "min", ascending = False)

    top10.columns = ['rank']
    df = pd.merge(
        df, top10,
        how = "left",
        left_index = True,
        right_index = True
    ).assign(
        ministerio = lambda x: [
            "Outros" if r > 10 else m for m, r in zip(
                x['Órgão Superior'],
                x['rank']
            )
        ]
    ).groupby(
        ['ano_mes', 'ministerio'],
        as_index = False
    ).sum().drop(
        columns = ['rank']
    ).assign(
        data = lambda x: x['ano_mes'].apply(
            lambda d: datetime.datetime.strptime(d + "/01", "%Y/%m/%d").strftime("%b/%Y")
        )
    )

    # --------------------------
    #  Calcula tamanho do eixo
    # --------------------------

    x_max = max(df['valor'])
    zeros = int(math.log10(x_max))
    x_final = x_max / pow(10, zeros)
    if (x_final % 1) < 0.5:
        x_final = int(x_final) + 0.5
    else:
        x_final = int(x_final) + 1.0
    eixo_x = [0, x_final * pow(10, zeros)]

    # ----------------------
    #  Calcula cada quadro
    # ----------------------

    for dt, grp in df.groupby(['data']):
        fig.add_trace(
            go.Scatter(
                visible=False,
                name = dt,
                x = grp['valor'],
                y = grp['ministerio'],
                mode = "markers"
            )
        )

    fig.data[0].visible = True

    # Create and add slider
    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method = "update",
            args = [
                {"visible": [False] * len(fig.data)}
            ],  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [
        dict(
            active = 0,
            currentvalue = {"prefix": "Data: "},
            pad = {"t": 50},
            steps = steps
        )
    ]

    fig.update_layout(
        sliders = sliders,
        title = "Top 10 ministérios com maior gasto no mês"
        # -- Usar o abaixo com dados reais
        # xaxis = dict(range = eixo_x, autorange = False)
    )

    fig.update_xaxes( # the y-axis is in dollars
        showgrid=False
    )

    return fig
