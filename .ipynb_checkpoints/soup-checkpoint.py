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
    for idx, url in enumerate(links_relatorios):
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        gols = list(g.text for g in soup.find_all("div", class_="score"))
        tecnicos = list(t.text.replace("Técnico: , ''") for t in soup.find_all("div", class_="datapoint"))
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

    # print(subs_list)
    subs_dict = {}
    for idx, i in enumerate(subs_list):
        # print(idx, i)
        try:
            if int(subs_list.__getitem__(idx)) + int(subs_list.__getitem__(idx + 2)) == 90:
                subs_dict[subs_list[idx - 1]] = subs_list[idx + 1]
        except TypeError:
            continue
        except ValueError:
            continue
        except IndexError:
            break
    # print(subs_dict)

    subs_dict_casa = {}
    subs_dict_fora = {}
    for sub in list(subs_dict.keys()):
        if sub in subs_casa:
            subs_dict_casa[sub] = subs_dict.get(str(sub))
        else:
            subs_dict_fora[sub] = subs_dict.get(str(sub))
    # print(subs_dict_casa)
    # print(subs_dict_fora)
    return subs_dict_casa, subs_dict_fora


teste_cuiaba_bahia = ['https://fbref.com//pt/partidas/6df78309/Cuiaba-Juventude-2021Maio29-Serie-A']
soup, gols, tecnicos, subs = stats_jogos(teste_cuiaba_bahia)

time_casa, tecnico_casa, gols_casa, onze_casa, banco_casa, subs_casa = escalacao_casa(soup, gols, tecnicos, subs)
time_fora, tecnico_fora, gols_fora, onze_fora, banco_fora, subs_fora = escalacao_fora(soup, gols, tecnicos, subs)

subs_dict_casa, subs_dict_fora = substituicoes(subs_casa)


