
import re
import os
import pandas as pd

from collections.abc import Iterable
from collections import OrderedDict, ChainMap

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


def orgaos_superiores():
    return {
        20000 : 'Presidência da República',
        22000 : 'Ministério da Agricultura, Pecuária e Abastec',
        24000 : 'Ministério da Ciência, Tecnologia, Inovações',
        25000 : 'Ministério da Economia',
        26000 : 'Ministério da Educação',
        30000 : 'Ministério da Justiça e Segurança Pública',
        32000 : 'Ministério de Minas e Energia',
        33000 : 'Ministério da Previdência Social',
        35000 : 'Ministério das Relações Exteriores',
        36000 : 'Ministério da Saúde',
        37000 : 'Controladoria-Geral da União',
        39000 : 'Ministério da Infraestrutura',
        44000 : 'Ministério do Meio Ambiente',
        52000 : 'Ministério da Defesa',
        53000 : 'Ministério do Desenvolvimento Regional',
        54000 : 'Ministério do Turismo',
        55000 : 'Ministério da Cidadania',
        63000 : 'Advocacia-Geral da União',
        81000 : 'Ministério da Mulher, Família e Direitos Huma'
    }
