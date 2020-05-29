from flask import Blueprint, render_template, request, make_response
from flask import session, jsonify
from flask import current_app as app
import plotly.express as px
import json

from .despesas_publicas import despesas

pdt_bp = Blueprint(
    name = "pdt_bp",
    import_name = __name__,
    template_folder = "templates",
    static_folder = 'assets',
    url_prefix = '/pdt'
)


def json_headers():
    return {'Content-Type' : 'application/json'}


desp    = despesas()
funcoes = sorted(desp['Função'].unique())
orgaos  = sorted(desp['Órgão Superior'].unique())
mods    = sorted(desp['modalidade'].unique())


@pdt_bp.before_app_first_request
def set_defaults():
    session['year'] = 2007
    session['modalidade'] = 'Pago'


def grafico_despesas(
    orgaos  = None,
    funcoes = None,
    modalidade = 'Pago'
):

    dd = desp.groupby(
        ['Órgão Superior', 'Função', 'Unidade Gestora', 'modalidade'],
        as_index = False
    ).sum()

    cond = dd['modalidade'] == modalidade
    if orgaos is not None:
        if orgaos:
            cond = cond & (dd['Órgão Superior'].isin(orgaos))
    
    if funcoes is not None:
        if funcoes:
            cond = cond & (dd['Função'].isin(funcoes))

    fig = dd.loc[cond, :].pipe(
        lambda df: px.treemap(
            df.query("valor > 0"),
            path   = ['Órgão Superior', 'Função', 'Unidade Gestora'],
            values = 'valor',
            maxdepth = 2
        )
    )

    fig.update_traces(hovertemplate = 'Valor: R$%{value:,.2f}')
    return json.loads(fig.to_json()).get('data')


@pdt_bp.route("/pdt", methods = ['GET', 'POST'])
def pdt_page():

    if request.method == 'POST':
        js = request.get_json()
        
        for key, val in js.items():
            print("{} : {}".format(key, val))
            session[key] = val
        
        return make_response(
            'Updating data succeeded!', 200, json_headers()
        )

    return render_template(
        "pdt.html",
        title = 'Portal da transparência',
        funcao = funcoes,
        orgao  = orgaos,
        modalidade = mods
    )


@pdt_bp.route("/pdt_data")
def pdt_data():

    org = session.get('orgao')
    fun = session.get('funcao')
    mod = session.get('modalidade')
    data = grafico_despesas(org, fun, mod)
    return make_response(jsonify(data), 200, json_headers())
