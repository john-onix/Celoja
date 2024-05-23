import os
import subprocess
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
service = Service(ChromeDriverManager().install(),
                      log_path=os.devnull,
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL) 
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
lista = []

lista_final = []

total_pages = []

marcas = []


def extracao_dados(url):

    requisicao = requests.get(url)
    soup = BeautifulSoup(requisicao.text, 'html.parser')

    jsonSujo = soup.find_all('script')[-41].text

    index = jsonSujo.find('_STATE_')

    jsonSujo = jsonSujo[index:]

    nomes = re.findall(r'"productName":"(.*?)"', jsonSujo)
    eans = re.findall(r'"ean":"(.*?)"', jsonSujo)
    prices = re.findall(r'"Price":(.*?)[,}]', jsonSujo)
    listPrices = re.findall(r'"ListPrice":(.*?)[,}]', jsonSujo)


    for i in range(0, len(nomes)):
        produto_sublista = [
                    nomes[i] if i < len(nomes) else None,
                    eans[i] if i < len(eans) else None,
                    prices[i] if i < len(prices) else None,
                    listPrices[i] if i < len(listPrices) else None,
                ]
        lista_final.append(produto_sublista)

    return lista_final


def extracao_categorias():
    
    url = "https://www.saojoaofarmacias.com.br/medicamentos"
    requisicao = requests.get(url)
    soup = BeautifulSoup(requisicao.text, 'html.parser')

    jsonSujo = soup.find_all('script')[-41].text

    index = jsonSujo.find('_STATE_')

    jsonSujo = jsonSujo[index:]

    categorias = re.findall(r'"href":"(.*?)"', jsonSujo)

    for i in range(2, 25):
        marcas_sublista = [
                    categorias[i] if i < len(categorias) else None,
                ]
        marcas.append(marcas_sublista)


    for j in range(len(marcas)):

        marcas[j][0] = re.sub(r'medicamentos\\u002F', '', marcas[j][0])
        marcas[j][0] = re.sub(r'\?map=categoria', '', marcas[j][0])


    return marcas


def extracao_num_itens(url):

    driver.get(url)

    time.sleep(2)

    html = driver.page_source
        
    soup = BeautifulSoup(html, 'html.parser')

    time.sleep(1)

    num = soup.find('div', class_="vtex-search-result-3-x-totalProducts--layout")

    num_only = re.sub(r"\D", "", num.text)

    final = num_only.replace(' ', '')

    return (int(final))


def criacao_url(categoria, pagina):

    url = 'https://www.saojoaofarmacias.com.br/medicamentos/' + str(categoria) + '?initialMap=c&initialQuery=medicamentos&map=category-1,category-2&page=' + str(pagina)

    return url


def main():

    todas_categorias = extracao_categorias()

    for i in range (len(todas_categorias)):

        urlas = criacao_url(todas_categorias[i][0], '1')

        inter = extracao_num_itens(urlas)

        numero_de_paginas = inter // 15

        for j in range(1, numero_de_paginas + 1):

            url = criacao_url(todas_categorias[i][0], str(j))

            lista_final = extracao_dados(url)


    df = pd.DataFrame(lista_final, columns=['Nome do remédio', 'Ean', 'Preço com desconto', 'Preço sem desconto'])

 
    df.to_csv('lista_de_produtos_SJ.csv', index=False)

    df.to_excel('lista_de_produtos_SJ.xlsx', index=False)



    driver.quit()


all_workers = os.cpu_count()

with ThreadPoolExecutor(max_workers=all_workers) as executor:

    executor.submit(main())