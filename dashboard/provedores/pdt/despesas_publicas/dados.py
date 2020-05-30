
import re
import os
import pandas as pd
from collections import ChainMap

loc = os.path.abspath(
    os.path.dirname(__file__)
)


def despesas():

    arquivos = os.listdir(loc)
    arquivos = filter(
        lambda a: re.search("^despesas_\\d{2}_\\d{4}\\.csv$", a) is not None,
        arquivos
    )

    desp = pd.concat(
        map(
            lambda a: pd.read_csv(os.path.join(loc, a), delimiter = ";"),
            arquivos
        ),
        sort = False
    )

    # -----------------------------
    #  Remove colunas com códigos
    # -----------------------------

    cols = filter(
        lambda c: re.search(r'código', c, re.I) is None,
        desp.columns
    )

    cols = list(cols)

    # -----------------------
    #  Renomeando as colunas
    # -----------------------

    anomes = {
        'Ano e mês do lançamento' : 'ano_mes'
    }

    nome = {
        c : re.sub(r'^Nome ', '', c) for c in cols if c.startswith('Nome ')
    }

    valor = {
        c : c.replace(
            'Valor', ''
        ).replace(
            'a Pagar ', ''
        ).replace(
            '(R$)', ''
        ).strip() for c in cols if c.startswith('Valor ')
    }

    novo_nome = ChainMap(anomes, nome, valor)
    return desp[list(cols)].rename(
        columns = novo_nome
    ).pipe(
        lambda df: df.melt(
            id_vars = [c for c in df.columns if c not in set(valor.values())],
            value_name = 'valor',
            var_name   = 'modalidade'
        )
    )
