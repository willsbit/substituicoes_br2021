import pprint
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# df = pd.DataFrame(columns=['time_casa', 'tecnico_casa', 'time_fora', 'tecnico_fora',
#                              'gols_casa', 'gols_fora', '11_casa', '11_fora', 'banco_casa', 'banco_fora'
#                                                                                            'sub1_casa',
#                              'sub_1_casa_tempo', 'sub2_casa', 'sub_2_casa_tempo',
#                              'sub3_casa', 'sub_3_casa_tempo', 'sub4_casa', 'sub_4_casa_tempo',
#                              'sub5_casa', 'sub_5_casa_tempo',
#                              'sub1_fora', 'sub_1_fora_tempo', 'sub2_fora', 'sub_2_fora_tempo',
#                              'sub3_fora', 'sub_3_fora_tempo', 'sub4_fora', 'sub_4_fora_tempo',
#                              'sub5_fora', 'sub_5_fora_tempo'])

# qual a troca mais comum? qual o jogador mais substituido?
# qual time troca mais cedo? e mais tarde? e quais técnicos fazem isso?


url = 'https://fbref.com/pt/comps/24/cronograma/Serie-A-Resultados-e-Calendarios'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

# pegar links do relatório de cada partida
relatorios = soup.find_all("a", string="Relatório da Partida")

relatorios_ls = []
for i in relatorios:
    relatorios_ls.append(str(i))

# formatar os links, remover tags e inline HTML
temp = list(map(lambda x: str.replace(x, "<a href=\"", "https://fbref.com/"), relatorios_ls))
links_relatorios = list(map(lambda x: str.replace(x, "\">Relatório da Partida</a>", ""), temp))


# print(links_relatorios)


# enumarate(links_relatorios)

def stats_jogos(links_relatorios):
    res = requests.get(links_relatorios)
    soup = BeautifulSoup(res.text, 'html.parser')
    gols = list(g.text for g in soup.find_all("div", class_="score"))
    tecnicos = list(t.text.replace('Técnico: ', '') for t in soup.find_all("div", class_="datapoint"))
    subs = list(s.text.replace('para ', '') for s in soup.select('small:contains("para ")'))
    # print(subs)
    return soup, gols, tecnicos, subs


def escalacao_casa(soup, gols, tecnicos, subs):
    for escalacao in soup.find_all("div", class_="lineup", id="a"):
        gols_casa = {'gols_casa': gols[0]}
        tecnico_casa = {'tecnico_casa': tecnicos[0].replace('\xa0', ' ')}
        time_casa = {'time_casa': escalacao.text.split(' ', 1)[0].replace('\n', '')}
        jogadores_casa_regex = re.split(' \(|\n|\)|[\d]|-', escalacao.text)
        jogadores_casa_temp = list(filter(None, jogadores_casa_regex))
        onze_casa = {'11_casa': jogadores_casa_temp[1:12]}
        banco_casa = {'banco_casa': jogadores_casa_temp[13:]}

        # substituições
        subs_casa = [sub for sub in subs if sub in jogadores_casa_temp]

        # print(f'{time_casa} {gols_casa}')
        # print(f'{tecnico_casa} - escalação:  {onze_casa}')
        # print(banco_casa)

        return time_casa, tecnico_casa, gols_casa, onze_casa, banco_casa, subs_casa


def escalacao_fora(soup, gols, tecnicos, subs):
    # time fora
    for escalacao in soup.find_all("div", class_="lineup", id="b"):
        gols_fora = {'gols_fora': gols[1]}
        tecnico_fora = {'tecnico_fora': tecnicos[2].replace('\xa0', ' ')}
        time_fora = {'time_fora': escalacao.text.split(' ', 1)[0].replace('\n', '')}
        # regex para remover quebras de linha, números e escalação
        jogadores_fora_regex = re.split(' \(|\n|\)|[\d]|-', escalacao.text)
        jogadores_fora_temp = list(filter(None, jogadores_fora_regex))
        # remover campos nulos na lista
        onze_fora = {'11_fora': jogadores_fora_temp[1:12]}  # slice da lista com os titulares
        banco_fora = {'banco_fora': jogadores_fora_temp[13:]}  # slice da lista com os reservas

        subs_fora = [sub for sub in subs if sub in jogadores_fora_temp]

        # print(f'{time_fora} {gols_fora}')
        # print(f'{tecnico_fora} - escalação: {onze_fora}')
        # print(banco_fora)
        # print(f'Substitutos que entraram: {subs_fora}')

        return time_fora, tecnico_fora, gols_fora, onze_fora, banco_fora, subs_fora


def substituicoes(subs_casa):
    subs_list = []
    for subs_list_soup in soup.select('tbody .center+ .right , th a'):
        subs_list_text = subs_list_soup.get_text()
        subs_list.append(subs_list_text)
        # subs_dict = {subs_list[i]: subs_list[i + 1] for i in range(0, len(subs_list), 2)}

    subs_dict = {}
    for idx, i in enumerate(subs_list):
        # print(idx, i)
        try:
            if int(subs_list.__getitem__(idx)) + int(subs_list.__getitem__(idx + 2)) == 90:
                subs_dict[subs_list[idx - 1]] = subs_list[idx + 1]
                # adicionar caso de substituição da substituição (soma das 3 minutagens == 90)
                # exemplo: juan mata vs leicester 2016 (utd 2 - lcf)
            elif int(subs_list.__getitem__(idx)) + int(subs_list.__getitem__(idx + 2)) + int(
                    subs_list.__getitem__(idx + 4)) == 90:
                subs_dict[subs_list[idx - 1]] = subs_list[idx + 1]
                subs_dict[subs_list[idx + 1]] = subs_list[idx + 3]
        except TypeError:
            continue
        except ValueError:
            continue
        except IndexError:
            break

    subs_dict_casa = {}
    subs_dict_fora = {}

    for sub in subs_casa:
        subs_dict_casa[sub] = subs_dict.get(str(sub))
    for sub in subs_fora:
        subs_dict_fora[sub] = subs_dict.get(str(sub))

    return subs_dict_casa, subs_dict_fora, subs_list


def tempo_subs_casa(subs_casa, subs_dict_casa, subs_list):
    sub1_casa = []
    sub2_casa = []
    sub3_casa = []
    sub4_casa = []
    sub5_casa = []

    for idx, i in list(enumerate(subs_dict_casa.items())):
        if idx == 0:
            sub1_casa.append(i)
        elif idx == 1:
            sub2_casa.append(i)
        elif idx == 2:
            sub3_casa.append(i)
        elif idx == 3:
            sub4_casa.append(i)
        elif idx == 4:
            sub5_casa.append(i)

    tempo_subs = []
    for idx, i in enumerate(subs_list):
        try:
            if i in subs_dict_casa.keys():
                tempo_subs.append(int(subs_list.__getitem__(idx + 1)))
        except TypeError:
            continue
        except ValueError:
            continue
        except IndexError:
            break
    sub1_casa_tempo, sub2_casa_tempo, sub3_casa_tempo, sub4_casa_tempo, sub5_casa_tempo = [], [], [], [], []
    try:
        sub1_casa_tempo = sorted(tempo_subs)[0]
        sub2_casa_tempo = sorted(tempo_subs)[1]
        sub3_casa_tempo = sorted(tempo_subs)[2]
        sub4_casa_tempo = sorted(tempo_subs)[3]
        sub5_casa_tempo = sorted(tempo_subs)[4]
    except IndexError:
        None

    return sub1_casa, sub2_casa, sub3_casa, sub4_casa, sub5_casa, \
           sub1_casa_tempo, sub2_casa_tempo, sub3_casa_tempo, sub4_casa_tempo, sub5_casa_tempo


def tempo_subs_fora(subs_fora, subs_dict_fora, subs_list):
    sub1_fora = []
    sub2_fora = []
    sub3_fora = []
    sub4_fora = []
    sub5_fora = []

    for idx, i in list(enumerate(subs_dict_fora.items())):
        if idx == 0:
            sub1_fora.append(i)
        elif idx == 1:
            sub2_fora.append(i)
        elif idx == 2:
            sub3_fora.append(i)
        elif idx == 3:
            sub4_fora.append(i)
        elif idx == 4:
            sub5_fora.append(i)

    tempo_subs = []
    for idx, i in enumerate(subs_list):
        try:
            if i in subs_dict_fora.keys():
                tempo_subs.append(int(subs_list.__getitem__(idx + 1)))
        except TypeError:
            continue
        except ValueError:
            continue
        except IndexError:
            break

    sub1_fora_tempo, sub2_fora_tempo, sub3_fora_tempo, sub4_fora_tempo, sub5_fora_tempo = [], [], [], [], []
    try:
        sub1_fora_tempo = sorted(tempo_subs)[0]
        sub2_fora_tempo = sorted(tempo_subs)[1]
        sub3_fora_tempo = sorted(tempo_subs)[2]
        sub4_fora_tempo = sorted(tempo_subs)[3]
        sub5_fora_tempo = sorted(tempo_subs)[4]
    except IndexError:
        None

    return sub1_fora, sub2_fora, sub3_fora, sub4_fora, sub5_fora, \
           sub1_fora_tempo, sub2_fora_tempo, sub3_fora_tempo, sub4_fora_tempo, sub5_fora_tempo


# # teste_cuiaba_bahia = ['https://fbref.com//pt/partidas/6df78309/Cuiaba-Juventude-2021Maio29-Serie-A']
for idx, url in list(enumerate(links_relatorios)):
    soup, gols, tecnicos, subs = stats_jogos(url)

    time_casa, tecnico_casa, gols_casa, onze_casa, banco_casa, subs_casa = escalacao_casa(soup, gols, tecnicos, subs)
    time_fora, tecnico_fora, gols_fora, onze_fora, banco_fora, subs_fora = escalacao_fora(soup, gols, tecnicos, subs)

    subs_dict_casa, subs_dict_fora, subs_list = substituicoes(subs_casa)

    sub1_casa, sub2_casa, sub3_casa, sub4_casa, sub5_casa, sub1_casa_tempo, sub2_casa_tempo, sub3_casa_tempo, sub4_casa_tempo, sub5_casa_tempo = tempo_subs_casa(
        subs_casa, subs_dict_casa, subs_list)
    sub1_fora, sub2_fora, sub3_fora, sub4_fora, sub5_fora, sub1_fora_tempo, sub2_fora_tempo, sub3_fora_tempo, sub4_fora_tempo, sub5_fora_tempo = tempo_subs_fora(
        subs_fora, subs_dict_fora, subs_list)

    sub1_casa = {k: v for k, v in enumerate(sub1_casa)}
    sub2_casa = {k: v for k, v in enumerate(sub2_casa)}
    sub3_casa = {k: v for k, v in enumerate(sub3_casa)}
    sub4_casa = {k: v for k, v in enumerate(sub4_casa)}
    sub5_casa = {k: v for k, v in enumerate(sub5_casa)}

    sub1_fora = {k: v for k, v in enumerate(sub1_fora)}
    sub2_fora = {k: v for k, v in enumerate(sub2_fora)}
    sub3_fora = {k: v for k, v in enumerate(sub3_fora)}
    sub4_fora = {k: v for k, v in enumerate(sub4_fora)}
    sub5_fora = {k: v for k, v in enumerate(sub5_fora)}

    if idx == 0:
        dfs = pd.DataFrame([[time_casa.values(), tecnico_casa.values(), time_fora.values(), tecnico_fora.values(),
                             gols_casa.values(), gols_fora.values(),
                             onze_casa.values(), onze_fora.values(), banco_casa.values(), banco_fora.values(),
                             sub1_casa.values(), sub1_casa_tempo, sub2_casa.values(), sub2_casa_tempo,
                             sub3_casa.values(),
                             sub3_casa_tempo,
                             sub4_casa.values(), sub4_casa_tempo, sub5_casa.values(), sub5_casa_tempo,
                             sub1_fora.values(), sub1_fora_tempo, sub2_fora.values(), sub2_fora_tempo,
                             sub3_fora.values(), sub3_fora_tempo, sub4_fora.values(), sub4_fora_tempo,
                             sub5_fora.values(), sub5_fora_tempo]])

        cols = {'columns': {0: 'time_casa', 1: 'tecnico_casa', 2: 'time_fora', 3: 'tecnico_fora', 4: 'gols_casa',
                            5: 'gols_fora',
                            6: '11_casa', 7: '11_fora', 8: 'banco_casa', 9: 'banco_fora', 10: 'sub1_casa',
                            11: 'sub1_casa_tempo', 12: 'sub2_casa', 13: 'sub2_casa_tempo', 14: 'sub3_casa',
                            15: 'sub3_casa_tempo', 16: 'sub4_casa',
                            17: 'sub4_casa_tempo', 18: 'sub5_casa', 19: 'sub5_casa_tempo',
                            20: 'sub1_fora', 21: 'sub1_fora_tempo', 22: 'sub2_fora', 23: 'sub2_fora_tempo',
                            24: 'sub3_fora',
                            25: 'sub3_fora_tempo', 26: 'sub4_fora', 27: 'sub4_fora_tempo', 28: 'sub5_fora',
                            29: 'sub5_fora_tempo'}}

        dfs.reset_index(drop=True).rename(**cols)

    else:
        dfs_i = pd.DataFrame([[time_casa.values(), tecnico_casa.values(), time_fora.values(), tecnico_fora.values(),
                               gols_casa.values(), gols_fora.values(),
                               onze_casa.values(), onze_fora.values(), banco_casa.values(), banco_fora.values(),
                               sub1_casa.values(), sub1_casa_tempo, sub2_casa.values(), sub2_casa_tempo,
                               sub3_casa.values(),
                               sub3_casa_tempo,
                               sub4_casa.values(), sub4_casa_tempo, sub5_casa.values(), sub5_casa_tempo,
                               sub1_fora.values(), sub1_fora_tempo, sub2_fora.values(), sub2_fora_tempo,
                               sub3_fora.values(), sub3_fora_tempo, sub4_fora.values(), sub4_fora_tempo,
                               sub5_fora.values(), sub5_fora_tempo]])

        dfs_i.reset_index(drop=True).rename(**cols)

        dfs_final = dfs.append(dfs_i, ignore_index=True)
        dfs = dfs_final

