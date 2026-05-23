#!/usr/bin/env python3
"""
Calculadora numerológica integrada.
Recebe nome completo e data de nascimento.
Retorna JSON com todos os números calculados nos sete sistemas.

Uso:
    python3 calculadora.py "Nome Completo" "DD/MM/AAAA"
    python3 calculadora.py "Ana Ruth Maquieli Retore Moro" "14/10/1978"

Modo sinastria:
    python3 calculadora.py --sinastria "Nome1" "DD/MM/AAAA" "Nome2" "DD/MM/AAAA"

Modo marca:
    python3 calculadora.py --marca "Nome da Marca" "DD/MM/AAAA"

Modo ano-pessoal:
    python3 calculadora.py --ano-pessoal "Nome" "DD/MM/AAAA" --ano 2026
"""

import sys
import json
import unicodedata
from datetime import datetime
import argparse

# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar(nome):
    """Remove acentos, normaliza para A-Z maiúsculo."""
    nfkd = unicodedata.normalize('NFKD', nome)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    sem_acento = sem_acento.replace('Ç', 'C').replace('ç', 'C')
    apenas_letras = "".join(c for c in sem_acento.upper() if c.isalpha() or c == ' ')
    return apenas_letras.strip()


def separar_palavras(nome):
    """Retorna lista de palavras do nome normalizado."""
    return [p for p in normalizar(nome).split() if p]


VOGAIS = set("AEIOU")


def eh_vogal(letra):
    return letra in VOGAIS


# ============================================================
# REDUÇÕES
# ============================================================

NUMEROS_MESTRES = {11, 22, 33, 44}
NUMEROS_KARMICOS = {13, 14, 16, 19}


def reduzir(numero, preservar_mestres=True):
    """Reduz a um único dígito, preservando mestres se solicitado."""
    while numero > 9:
        if preservar_mestres and numero in NUMEROS_MESTRES:
            return numero
        numero = sum(int(d) for d in str(numero))
    return numero


def detectar_karmicos_no_caminho(data_str):
    """Detecta números kármicos na soma da data, dia e vida passada tântrica."""
    dia, mes, ano = parse_data(data_str)
    digitos = list(str(dia)) + list(str(mes)) + list(str(ano))
    soma = sum(int(d) for d in digitos)
    ano_str = f"{ano:04d}"
    vida_passada_bruta = int(ano_str[:2])
    karmicos = []
    if soma in NUMEROS_KARMICOS:
        karmicos.append({'numero': soma, 'origem': 'caminho_de_vida_bruto'})
    if dia in NUMEROS_KARMICOS:
        karmicos.append({'numero': dia, 'origem': 'dia_nascimento'})
    if vida_passada_bruta in NUMEROS_KARMICOS:
        karmicos.append({'numero': vida_passada_bruta, 'origem': 'vida_passada_tantrica'})
    return karmicos


def parse_data(data_str):
    """Parse de DD/MM/AAAA."""
    partes = data_str.replace('-', '/').replace('.', '/').split('/')
    if len(partes) != 3:
        raise ValueError(f"Data inválida: {data_str}")
    dia, mes, ano = int(partes[0]), int(partes[1]), int(partes[2])
    if ano < 100:
        ano = 1900 + ano if ano >= 30 else 2000 + ano
    return dia, mes, ano


# ============================================================
# SISTEMA PITAGÓRICO
# ============================================================

TABELA_PITAGORICO = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}


def soma_palavra(palavra, tabela):
    return sum(tabela.get(c, 0) for c in palavra)


def pitagorico(nome, data_str):
    palavras = separar_palavras(nome)
    nome_limpo = normalizar(nome).replace(' ', '')

    # Soma por palavra
    somas_palavras = []
    for p in palavras:
        soma = soma_palavra(p, TABELA_PITAGORICO)
        somas_palavras.append({
            'palavra': p,
            'soma_bruta': soma,
            'reduzido': reduzir(soma),
            'reduzido_sem_mestres': reduzir(soma, preservar_mestres=False)
        })

    # Caminho de Vida (soma da data)
    dia, mes, ano = parse_data(data_str)
    digitos_data = list(str(dia)) + list(str(mes)) + list(str(ano))
    soma_data = sum(int(d) for d in digitos_data)
    caminho_vida = reduzir(soma_data)
    caminho_vida_sem_mestre = reduzir(soma_data, preservar_mestres=False)

    # Expressão (todas as letras)
    soma_total = soma_palavra(nome_limpo, TABELA_PITAGORICO)
    expressao = reduzir(soma_total)

    # Alma (vogais)
    soma_vogais = sum(TABELA_PITAGORICO.get(c, 0) for c in nome_limpo if eh_vogal(c))
    alma = reduzir(soma_vogais)

    # Personalidade (consoantes)
    soma_consoantes = sum(TABELA_PITAGORICO.get(c, 0) for c in nome_limpo if not eh_vogal(c))
    personalidade = reduzir(soma_consoantes)

    # Maturidade (CV + Expressão)
    maturidade = reduzir(caminho_vida_sem_mestre + reduzir(soma_total, preservar_mestres=False))

    # Dia natalício
    dia_natalicio = reduzir(dia, preservar_mestres=False)

    # Vibrações ausentes (de 1 a 9)
    vibracoes_presentes = set(TABELA_PITAGORICO[c] for c in nome_limpo)
    vibracoes_ausentes = sorted([n for n in range(1, 10) if n not in vibracoes_presentes])

    # Vibrações em excesso (3 ou mais vezes)
    contagem = {}
    for c in nome_limpo:
        v = TABELA_PITAGORICO[c]
        contagem[v] = contagem.get(v, 0) + 1
    vibracoes_excesso = sorted([n for n, c in contagem.items() if c >= 3])

    # Pináculos e Desafios
    cv = caminho_vida_sem_mestre
    pin1 = reduzir(reduzir(mes, False) + reduzir(dia, False), False)
    pin2 = reduzir(reduzir(dia, False) + reduzir(ano, False), False)
    pin3 = reduzir(pin1 + pin2, False)
    pin4 = reduzir(reduzir(mes, False) + reduzir(ano, False), False)

    des1 = abs(reduzir(mes, False) - reduzir(dia, False))
    des2 = abs(reduzir(dia, False) - reduzir(ano, False))
    des3 = abs(des1 - des2)
    des4 = abs(reduzir(mes, False) - reduzir(ano, False))

    idade_pin1_fim = 36 - cv
    idade_pin2_fim = idade_pin1_fim + 9
    idade_pin3_fim = idade_pin2_fim + 9

    pinaculos = [
        {'ordem': 1, 'idade': f"0 a {idade_pin1_fim}", 'numero': pin1, 'desafio': des1},
        {'ordem': 2, 'idade': f"{idade_pin1_fim} a {idade_pin2_fim}", 'numero': pin2, 'desafio': des2},
        {'ordem': 3, 'idade': f"{idade_pin2_fim} a {idade_pin3_fim}", 'numero': pin3, 'desafio': des3},
        {'ordem': 4, 'idade': f"{idade_pin3_fim}+", 'numero': pin4, 'desafio': des4}
    ]

    # Ciclos de Vida
    ciclo_juventude = reduzir(mes, False)
    ciclo_produtividade = reduzir(dia, False)
    ciclo_maturidade = reduzir(ano, False)

    ciclos = [
        {'ordem': 1, 'nome': 'Juventude', 'idade': '0 a 28', 'numero': ciclo_juventude, 'base': 'mês'},
        {'ordem': 2, 'nome': 'Produtividade', 'idade': '28 a 56', 'numero': ciclo_produtividade, 'base': 'dia'},
        {'ordem': 3, 'nome': 'Maturidade', 'idade': '56+', 'numero': ciclo_maturidade, 'base': 'ano'}
    ]

    # Ano Pessoal (relativo ao ano atual)
    ano_atual = datetime.now().year
    ano_pessoal_atual = reduzir(reduzir(dia, False) + reduzir(mes, False) + reduzir(ano_atual, False), False)
    ano_pessoal_proximo = reduzir(reduzir(dia, False) + reduzir(mes, False) + reduzir(ano_atual + 1, False), False)

    return {
        'sistema': 'pitagorico',
        'somas_palavras': somas_palavras,
        'caminho_vida': caminho_vida,
        'caminho_vida_bruto': soma_data,
        'expressao': expressao,
        'expressao_bruta': soma_total,
        'alma': alma,
        'alma_bruta': soma_vogais,
        'personalidade': personalidade,
        'personalidade_bruta': soma_consoantes,
        'maturidade': maturidade,
        'dia_natalicio': dia_natalicio,
        'vibracoes_ausentes': vibracoes_ausentes,
        'vibracoes_excesso': vibracoes_excesso,
        'pinaculos': pinaculos,
        'ciclos': ciclos,
        'ano_pessoal_atual': {'ano': ano_atual, 'numero': ano_pessoal_atual},
        'ano_pessoal_proximo': {'ano': ano_atual + 1, 'numero': ano_pessoal_proximo}
    }


# ============================================================
# SISTEMA CABALÍSTICO
# ============================================================

TABELA_CABALISTICO = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5,
    'U': 6, 'V': 6, 'W': 6, 'X': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}


def cabalistico(nome):
    palavras = separar_palavras(nome)
    nome_limpo = normalizar(nome).replace(' ', '')

    somas_palavras = []
    for p in palavras:
        soma = soma_palavra(p, TABELA_CABALISTICO)
        somas_palavras.append({
            'palavra': p,
            'soma_bruta': soma,
            'reduzido': reduzir(soma)
        })

    soma_total = soma_palavra(nome_limpo, TABELA_CABALISTICO)

    return {
        'sistema': 'cabalistico',
        'somas_palavras': somas_palavras,
        'destino': reduzir(soma_total),
        'destino_bruto': soma_total,
        'destino_reduzido_sem_mestre': reduzir(soma_total, preservar_mestres=False)
    }


# ============================================================
# SISTEMA CALDEU
# ============================================================

TABELA_CALDEU = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
    # Não há atribuição 9 no Caldeu tradicional. 9 emerge apenas da soma.
}


def caldeu(nome):
    palavras = separar_palavras(nome)
    nome_limpo = normalizar(nome).replace(' ', '')

    somas_palavras = []
    for p in palavras:
        soma = soma_palavra(p, TABELA_CALDEU)
        somas_palavras.append({
            'palavra': p,
            'soma_bruta': soma,
            'reduzido': reduzir(soma)
        })

    soma_total = soma_palavra(nome_limpo, TABELA_CALDEU)
    soma_vogais = sum(TABELA_CALDEU.get(c, 0) for c in nome_limpo if eh_vogal(c))
    soma_consoantes = sum(TABELA_CALDEU.get(c, 0) for c in nome_limpo if not eh_vogal(c))

    return {
        'sistema': 'caldeu',
        'somas_palavras': somas_palavras,
        'destino': reduzir(soma_total),
        'destino_bruto': soma_total,
        'alma': reduzir(soma_vogais),
        'alma_bruta': soma_vogais,
        'personalidade': reduzir(soma_consoantes),
        'personalidade_bruta': soma_consoantes
    }


# ============================================================
# SISTEMA VÉDICO
# ============================================================

PLANETAS_VEDICOS = {
    1: 'Sol', 2: 'Lua', 3: 'Júpiter', 4: 'Rahu', 5: 'Mercúrio',
    6: 'Vênus', 7: 'Ketu', 8: 'Saturno', 9: 'Marte'
}


def vedico(nome, data_str):
    dia, mes, ano = parse_data(data_str)
    digitos_data = list(str(dia)) + list(str(mes)) + list(str(ano))

    # Mulank (Psíquico) = dia reduzido
    mulank = reduzir(dia, preservar_mestres=False)

    # Bhagyank (Destino) = total da data reduzido
    bhagyank = reduzir(sum(int(d) for d in digitos_data), preservar_mestres=False)

    # Naam Ank (Nome) = mesmo do Pitagórico
    nome_limpo = normalizar(nome).replace(' ', '')
    naam_ank = reduzir(soma_palavra(nome_limpo, TABELA_PITAGORICO), preservar_mestres=False)

    # Lo Shu Grid Védico
    digitos_presentes = [int(d) for d in digitos_data if d != '0']
    contagem_grid = {n: digitos_presentes.count(n) for n in range(1, 10)}

    # Linhas/colunas/diagonais do Lo Shu (mesma estrutura do chinês)
    grid_layout = {
        4: (0, 0), 9: (0, 1), 2: (0, 2),
        3: (1, 0), 5: (1, 1), 7: (1, 2),
        8: (2, 0), 1: (2, 1), 6: (2, 2)
    }

    def linha_completa(numeros):
        return all(contagem_grid[n] > 0 for n in numeros)

    planos_grid = {
        'mente': linha_completa([4, 9, 2]),
        'coracao': linha_completa([3, 5, 7]),
        'pratico': linha_completa([8, 1, 6]),
        'vontade': linha_completa([1, 5, 9]),
        'protecao': linha_completa([4, 5, 6]),
        'acao': linha_completa([2, 5, 8]),
        'raiz_materia': linha_completa([4, 3, 8]),
        'emocao_conexao': linha_completa([2, 7, 6])
    }

    return {
        'sistema': 'vedico',
        'mulank': mulank,
        'mulank_planeta': PLANETAS_VEDICOS[mulank] if mulank in PLANETAS_VEDICOS else None,
        'bhagyank': bhagyank,
        'bhagyank_planeta': PLANETAS_VEDICOS[bhagyank] if bhagyank in PLANETAS_VEDICOS else None,
        'naam_ank': naam_ank,
        'naam_ank_planeta': PLANETAS_VEDICOS[naam_ank] if naam_ank in PLANETAS_VEDICOS else None,
        'lo_shu_grid': contagem_grid,
        'planos_grid': planos_grid
    }


# ============================================================
# SISTEMA TÂNTRICO (Kundalini)
# ============================================================

CORPOS_TANTRICOS = {
    1: 'Corpo da Alma',
    2: 'Corpo Mental Negativo',
    3: 'Corpo Mental Positivo',
    4: 'Mente Neutra',
    5: 'Corpo Físico',
    6: 'Linha de Arco',
    7: 'Aura',
    8: 'Corpo Pranayama',
    9: 'Corpo Sutil',
    10: 'Corpo Radiante',
    11: 'Eu Embodied'
}


def tantrico(data_str):
    dia, mes, ano = parse_data(data_str)
    ano_str = f"{ano:04d}"
    primeiros_dois_ano = int(ano_str[:2])
    ultimos_dois_ano = int(ano_str[2:])

    # Alma = dia reduzido
    alma = reduzir(dia, preservar_mestres=False)

    # Karma = mês reduzido
    karma = reduzir(mes, preservar_mestres=False)

    # Dom (Gift) = últimos dois dígitos do ano reduzidos
    dom = reduzir(ultimos_dois_ano, preservar_mestres=False)

    # Vida Passada = primeiros dois dígitos do ano reduzidos
    vida_passada = reduzir(primeiros_dois_ano, preservar_mestres=False)

    # Caminho = soma total reduzida
    soma_total = sum(int(d) for d in str(dia) + str(mes) + str(ano))
    caminho = reduzir(soma_total, preservar_mestres=False)

    karmicos_tantricos = []
    if primeiros_dois_ano in NUMEROS_KARMICOS:
        karmicos_tantricos.append({'numero': primeiros_dois_ano, 'posicao': 'vida_passada_bruta'})
    if ultimos_dois_ano in NUMEROS_KARMICOS:
        karmicos_tantricos.append({'numero': ultimos_dois_ano, 'posicao': 'dom_bruto'})
    if soma_total in NUMEROS_KARMICOS:
        karmicos_tantricos.append({'numero': soma_total, 'posicao': 'caminho_bruto'})

    return {
        'sistema': 'tantrico',
        'alma': {'numero': alma, 'corpo': CORPOS_TANTRICOS.get(alma)},
        'karma': {'numero': karma, 'corpo': CORPOS_TANTRICOS.get(karma)},
        'dom': {'numero': dom, 'corpo': CORPOS_TANTRICOS.get(dom)},
        'vida_passada': {'numero': vida_passada, 'corpo': CORPOS_TANTRICOS.get(vida_passada), 'bruto': primeiros_dois_ano},
        'caminho': {'numero': caminho, 'corpo': CORPOS_TANTRICOS.get(caminho)},
        'karmicos_tantricos': karmicos_tantricos
    }


# ============================================================
# SISTEMA CHINÊS
# ============================================================

ZODIACO_CHINES = [
    ('Rato', 0), ('Boi', 1), ('Tigre', 2), ('Coelho', 3),
    ('Dragão', 4), ('Serpente', 5), ('Cavalo', 6), ('Cabra', 7),
    ('Macaco', 8), ('Galo', 9), ('Cão', 10), ('Porco', 11)
]

ELEMENTOS_CHINESES = ['Madeira', 'Fogo', 'Terra', 'Metal', 'Água']


def signo_chines(ano):
    """Aproximação simples. Para precisão astrológica, considerar ano novo lunar (varia entre 21/jan e 20/fev)."""
    # 1924 foi o início do ciclo de 60 anos: Rato de Madeira Yang
    # Ciclo de 12 animais
    indice_animal = (ano - 1924) % 12
    signo = ZODIACO_CHINES[indice_animal][0]

    # Elemento: ciclo de 10 anos, 2 anos por elemento, começando com Madeira em 1924
    indice_elemento = ((ano - 1924) % 10) // 2
    elemento = ELEMENTOS_CHINESES[indice_elemento]

    # Yin/Yang: anos pares são Yang, ímpares são Yin
    yin_yang = 'Yang' if ano % 2 == 0 else 'Yin'

    return {
        'signo': signo,
        'elemento': elemento,
        'yin_yang': yin_yang,
        'combinacao': f"{signo} de {elemento} ({yin_yang})"
    }


def chines(data_str):
    dia, mes, ano = parse_data(data_str)
    return {
        'sistema': 'chines',
        'zodiaco': signo_chines(ano),
        'nota': 'Lo Shu Grid completo já calculado no sistema védico'
    }


# ============================================================
# SISTEMA CÓSMICO / ESTELAR
# ============================================================

SIGNOS_ASTROLOGICOS = [
    ('Capricórnio', (12, 22), (1, 19)),
    ('Aquário', (1, 20), (2, 18)),
    ('Peixes', (2, 19), (3, 20)),
    ('Áries', (3, 21), (4, 19)),
    ('Touro', (4, 20), (5, 20)),
    ('Gêmeos', (5, 21), (6, 20)),
    ('Câncer', (6, 21), (7, 22)),
    ('Leão', (7, 23), (8, 22)),
    ('Virgem', (8, 23), (9, 22)),
    ('Libra', (9, 23), (10, 22)),
    ('Escorpião', (10, 23), (11, 21)),
    ('Sagitário', (11, 22), (12, 21))
]


def signo_solar(dia, mes):
    for signo, ini, fim in SIGNOS_ASTROLOGICOS:
        if ini[0] == fim[0]:
            if mes == ini[0] and ini[1] <= dia <= fim[1]:
                return signo
        else:
            if (mes == ini[0] and dia >= ini[1]) or (mes == fim[0] and dia <= fim[1]):
                return signo
    return None


def cosmico(data_str):
    dia, mes, ano = parse_data(data_str)

    # Vibração galáctica do ano
    galactica = reduzir(sum(int(d) for d in str(ano)), preservar_mestres=False)

    # Vibração do dia (numerologia solar)
    solar_diaria = reduzir(dia, preservar_mestres=False)

    # Vibração de cristal (dia + mês)
    cristal = reduzir(dia + mes, preservar_mestres=False)

    # Signo solar
    signo = signo_solar(dia, mes)

    return {
        'sistema': 'cosmico',
        'galactica': galactica,
        'solar_diaria': solar_diaria,
        'cristal': cristal,
        'signo_solar': signo
    }


# ============================================================
# CRUZAMENTO DE COERÊNCIA
# ============================================================

def detectar_convergencias(resultados):
    """
    Identifica números que aparecem em três ou mais sistemas.
    Retorna dict {numero: [lista de ocorrências]}
    """
    ocorrencias = {}

    def adicionar(numero, sistema, posicao):
        if numero is None or not isinstance(numero, int):
            return
        if numero not in ocorrencias:
            ocorrencias[numero] = []
        ocorrencias[numero].append(f"{sistema} - {posicao}")

    p = resultados['pitagorico']
    adicionar(p['caminho_vida'], 'Pitagórico', 'Caminho de Vida')
    adicionar(p['expressao'], 'Pitagórico', 'Expressão')
    adicionar(p['alma'], 'Pitagórico', 'Alma')
    adicionar(p['personalidade'], 'Pitagórico', 'Personalidade')
    adicionar(p['maturidade'], 'Pitagórico', 'Maturidade')
    adicionar(p['dia_natalicio'], 'Pitagórico', 'Dia Natalício')

    c = resultados['cabalistico']
    adicionar(c['destino'], 'Cabalístico', 'Destino')

    cd = resultados['caldeu']
    adicionar(cd['destino'], 'Caldeu', 'Destino')
    adicionar(cd['alma'], 'Caldeu', 'Alma')
    adicionar(cd['personalidade'], 'Caldeu', 'Personalidade')

    v = resultados['vedico']
    adicionar(v['mulank'], 'Védico', 'Mulank')
    adicionar(v['bhagyank'], 'Védico', 'Bhagyank')
    adicionar(v['naam_ank'], 'Védico', 'Naam Ank')

    t = resultados['tantrico']
    adicionar(t['alma']['numero'], 'Tântrico', 'Alma')
    adicionar(t['karma']['numero'], 'Tântrico', 'Karma')
    adicionar(t['dom']['numero'], 'Tântrico', 'Dom')
    adicionar(t['vida_passada']['numero'], 'Tântrico', 'Vida Passada')
    adicionar(t['caminho']['numero'], 'Tântrico', 'Caminho')

    co = resultados['cosmico']
    adicionar(co['galactica'], 'Cósmico', 'Galáctica')
    adicionar(co['solar_diaria'], 'Cósmico', 'Solar Diária')
    adicionar(co['cristal'], 'Cósmico', 'Cristal')

    # Filtrar apenas convergências (3+ ocorrências)
    convergencias = {n: ocs for n, ocs in ocorrencias.items() if len(ocs) >= 3}
    # Ordenar por número de ocorrências desc
    convergencias_ordenadas = dict(sorted(convergencias.items(), key=lambda x: -len(x[1])))

    return convergencias_ordenadas


# ============================================================
# MODO MARCA / EMPRESA
# ============================================================

def analise_marca(nome, data_str):
    """Análise para entidades. Omite Tântrico (pessoal) e Mulank védico."""
    dia, mes, ano = parse_data(data_str)
    digitos_data = list(str(dia)) + list(str(mes)) + list(str(ano))
    bhagyank = reduzir(sum(int(d) for d in digitos_data), preservar_mestres=False)
    nome_limpo = normalizar(nome).replace(' ', '')
    naam_ank = reduzir(soma_palavra(nome_limpo, TABELA_PITAGORICO), preservar_mestres=False)

    resultados = {
        'meta': {
            'nome_original': nome,
            'nome_normalizado': normalizar(nome),
            'data_fundacao': data_str,
            'modo': 'marca',
            'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'pitagorico': pitagorico(nome, data_str),
        'cabalistico': cabalistico(nome),
        'caldeu': caldeu(nome),
        'chines': chines(data_str),
        'cosmico': cosmico(data_str),
        'vedico_parcial': {
            'bhagyank': bhagyank,
            'bhagyank_planeta': PLANETAS_VEDICOS.get(bhagyank),
            'naam_ank': naam_ank,
            'naam_ank_planeta': PLANETAS_VEDICOS.get(naam_ank),
            'nota': 'Mulank e Lo Shu Grid omitidos — não se aplicam a entidades'
        }
    }

    ocorrencias = {}
    def add(n, s, p):
        if n and isinstance(n, int):
            ocorrencias.setdefault(n, []).append(f"{s} - {p}")

    p = resultados['pitagorico']
    add(p['caminho_vida'], 'Pitagórico', 'Caminho de Vida')
    add(p['expressao'], 'Pitagórico', 'Expressão')
    add(p['alma'], 'Pitagórico', 'Alma')
    add(p['personalidade'], 'Pitagórico', 'Personalidade')
    add(resultados['cabalistico']['destino'], 'Cabalístico', 'Destino')
    add(resultados['caldeu']['destino'], 'Caldeu', 'Destino')
    add(bhagyank, 'Védico', 'Bhagyank')
    add(naam_ank, 'Védico', 'Naam Ank')
    add(resultados['cosmico']['galactica'], 'Cósmico', 'Galáctica')
    add(resultados['cosmico']['cristal'], 'Cósmico', 'Cristal')

    resultados['convergencias'] = dict(sorted(
        {n: ocs for n, ocs in ocorrencias.items() if len(ocs) >= 3}.items(),
        key=lambda x: -len(x[1])
    ))
    return resultados


# ============================================================
# ORQUESTRAÇÃO
# ============================================================

def analise_completa(nome, data_str):
    resultados = {
        'meta': {
            'nome_original': nome,
            'nome_normalizado': normalizar(nome),
            'data': data_str,
            'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'pitagorico': pitagorico(nome, data_str),
        'cabalistico': cabalistico(nome),
        'caldeu': caldeu(nome),
        'vedico': vedico(nome, data_str),
        'tantrico': tantrico(data_str),
        'chines': chines(data_str),
        'cosmico': cosmico(data_str)
    }
    resultados['convergencias'] = detectar_convergencias(resultados)
    resultados['karmicos_detectados'] = detectar_karmicos_no_caminho(data_str)
    return resultados


def sinastria(nome1, data1, nome2, data2):
    return {
        'pessoa_1': analise_completa(nome1, data1),
        'pessoa_2': analise_completa(nome2, data2),
        'comparativo': comparar(nome1, data1, nome2, data2)
    }


def comparar(nome1, data1, nome2, data2):
    a1 = analise_completa(nome1, data1)
    a2 = analise_completa(nome2, data2)

    cv1 = a1['pitagorico']['caminho_vida']
    cv2 = a2['pitagorico']['caminho_vida']
    alma1 = a1['pitagorico']['alma']
    alma2 = a2['pitagorico']['alma']
    exp1 = a1['pitagorico']['expressao']
    exp2 = a2['pitagorico']['expressao']

    return {
        'caminho_vida': {'p1': cv1, 'p2': cv2, 'igual': cv1 == cv2, 'diferenca': abs(cv1 - cv2) if isinstance(cv1, int) and isinstance(cv2, int) else None},
        'alma': {'p1': alma1, 'p2': alma2, 'igual': alma1 == alma2},
        'expressao': {'p1': exp1, 'p2': exp2, 'igual': exp1 == exp2}
    }


def ano_pessoal_detalhado(nome, data_str, ano_ref):
    dia, mes, _ = parse_data(data_str)
    base = reduzir(dia, False) + reduzir(mes, False) + reduzir(ano_ref, False)
    ano_pessoal = reduzir(base, False)

    meses = []
    for m in range(1, 13):
        mes_pessoal = reduzir(ano_pessoal + m, False)
        meses.append({'mes': m, 'numero': mes_pessoal})

    return {
        'ano_referencia': ano_ref,
        'ano_pessoal': ano_pessoal,
        'meses_pessoais': meses
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='Calculadora numerológica integrada')
    parser.add_argument('--sinastria', action='store_true', help='Modo sinastria (dois nomes)')
    parser.add_argument('--marca', action='store_true', help='Modo marca / empresa')
    parser.add_argument('--ano-pessoal', action='store_true', help='Modo ano pessoal detalhado')
    parser.add_argument('--ano', type=int, default=None, help='Ano de referência para ano pessoal')
    parser.add_argument('args', nargs='+', help='Argumentos posicionais (nome e data)')

    parsed = parser.parse_args()

    if parsed.sinastria:
        if len(parsed.args) != 4:
            print("Sinastria exige: nome1 data1 nome2 data2", file=sys.stderr)
            sys.exit(1)
        resultado = sinastria(parsed.args[0], parsed.args[1], parsed.args[2], parsed.args[3])
    elif parsed.marca:
        if len(parsed.args) != 2:
            print("Modo marca exige: nome_marca data_fundacao", file=sys.stderr)
            sys.exit(1)
        resultado = analise_marca(parsed.args[0], parsed.args[1])
    elif parsed.ano_pessoal:
        if len(parsed.args) != 2:
            print("Ano pessoal exige: nome data", file=sys.stderr)
            sys.exit(1)
        ano_ref = parsed.ano if parsed.ano else datetime.now().year
        resultado = {
            'analise_base': analise_completa(parsed.args[0], parsed.args[1]),
            'ano_pessoal_detalhado': ano_pessoal_detalhado(parsed.args[0], parsed.args[1], ano_ref)
        }
    else:
        if len(parsed.args) != 2:
            print("Modo padrão exige: nome data", file=sys.stderr)
            sys.exit(1)
        resultado = analise_completa(parsed.args[0], parsed.args[1])

    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
