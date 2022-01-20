import pprint
import requests
from bs4 import BeautifulSoup
import re

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
        for escalacao_casa in soup.find_all("div", class_="lineup", id="a"):
            jogadores_casa_regex = re.split(' \(|\n|\)|[\d]|-', escalacao_casa.text)
            jogadores_casa_temp = list(filter(None, jogadores_casa_regex))
            onze_casa = jogadores_casa_temp[1:12]
            banco_casa = jogadores_casa_temp[13:]
            print(onze_casa)
            print(banco_casa)
            
        for escalacao_fora in soup.find_all("div", class_="lineup", id="b"):
            jogadores_fora_regex = re.split(' \(|\n|\)|[\d]|-', escalacao_fora.text)
            jogadores_fora_temp = list(filter(None, jogadores_fora_regex))
            onze_fora = jogadores_fora_temp[1:12]
            banco_fora = jogadores_fora_temp[13:]
            print(onze_fora)
            print(banco_fora)

        # table = soup.find(lambda tag: tag.name == 'table') #and tag.has_attr('id') and tag['id'] == "Table1"
        # rows = table.find_all(lambda tag: tag.name == 'tr')
        # pprint.pprint(list(escalacao_casa))


teste_cuiaba_bahia = ['https://fbref.com//pt/partidas/6df78309/Cuiaba-Juventude-2021Maio29-Serie-A']
stats_jogos(teste_cuiaba_bahia)
