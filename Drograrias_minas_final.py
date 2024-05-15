import os
import subprocess
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
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


def extracao_dados(soup):


    jsonSujo = soup.find_all('script')[-34].text
    jsonSujo = jsonSujo[:-8]



    jsonLimpo = jsonSujo.split("_STATE_ = ")[0]
    nomes = re.findall(r'"productName":"(.*?)"', jsonLimpo)
    eans = re.findall(r'"ean":"(.*?)"', jsonLimpo)
    prices = re.findall(r'"Price":(.*?)[,}]', jsonLimpo)
    listPrices = re.findall(r'"ListPrice":(.*?)[,}]', jsonLimpo)


    for i in range(0, len(nomes)):
        produto_sublista = [
                    nomes[i] if i < len(nomes) else None,
                    eans[i] if i < len(eans) else None,
                    prices[i] if i < len(prices) else None,
                    listPrices[i] if i < len(listPrices) else None,
                ]
        lista_final.append(produto_sublista)
  
    return lista_final


def extracao_num_itens(soup):

    jsonSujo = soup.find_all('script')[-34].text
    jsonSujo = jsonSujo[:-8]
    jsonLimpo = jsonSujo.split("_STATE_ = ")[0]
    num = re.findall(r'"recordsFiltered":(.*?)[,}]', jsonLimpo)

    return int(num[0])


def extracao_marcas():
    
    driver.get('https://www.drogariasminasmais.com.br/medicamentos?initialMap=c&initialQuery=medicamentos&map=category-1')
    
    html = driver.page_source
    
    soup = BeautifulSoup(html, 'html.parser')

    marcas = soup.find_all('label', class_="vtex-checkbox__label")

    marcas_list = []

    for i in marcas:
        marcas_list.append(i.text)

    for i in range (len(marcas_list) - 1, -1, -1):
            if marcas_list[i].upper() != marcas_list[i] or marcas_list[i].lower() == marcas_list[i]:
                marcas_list.remove(marcas_list[i])

    for j in range(len(marcas_list)):
         marcas_list[j] = marcas_list[j].lower()
         marcas_list[j] = re.sub(r"\s+", "-", marcas_list[j])
         marcas_list[j] = re.sub(r'/', '-', marcas_list[j])

    return marcas_list


def main():

    marcas = extracao_marcas()

    for marca in marcas:

        url = "https://www.drogariasminasmais.com.br/medicamentos/" + str(marca) + "?initialMap=c&initialQuery=medicamentos&map=category-1,brand&page=1"
        requisicao = requests.get(url)
        soup = BeautifulSoup(requisicao.text, 'html.parser')
        total_pages.append(extracao_num_itens(soup))
        
    for j in range (len(marcas)):

        for i in range (1, total_pages[j] // 15 + 2):

            url = "https://www.drogariasminasmais.com.br/medicamentos/" + str(marcas[j]) + "?initialMap=c&initialQuery=medicamentos&map=category-1,brand&page=" + str(i)

            requisicao = requests.get(url)
            soup = BeautifulSoup(requisicao.text, 'html.parser')
            extracao_dados(soup)


    df = pd.DataFrame(lista_final, columns=['Nome', 'EAN', 'Preço com Desconto', 'Preço sem Desconto'])

    df.to_csv('dados_produtos.csv', sep=';', index=False, encoding='utf-8')


all_workers = os.cpu_count()

with ThreadPoolExecutor(max_workers=all_workers) as executor:

    executor.submit(main())