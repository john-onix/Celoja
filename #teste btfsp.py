import os
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import sys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import subprocess
import pandas
import time
from concurrent.futures import ThreadPoolExecutor

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
service = Service(ChromeDriverManager().install(),
                      log_path=os.devnull,
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL) 
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def criacao_url(marca, pagina):
    url = 'https://www.drogariasminasmais.com.br/medicamentos/' + str(marca) + '?initialMap=c&initialQuery=medicamentos&map=category-1,brand&page=' + str(pagina)

    return url



def extracao_num_itens(url):

    driver.get(url)

    time.sleep(2)

    html = driver.page_source
    
    soup = BeautifulSoup(html, 'html.parser')

    time.sleep(2)

    num = soup.find('div', class_="vtex-search-result-3-x-totalProducts--layout")

    num_only = re.sub(r"\D", "", num.text)

    final = num_only.replace(' ', '')

    return (final)



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

    
    return marcas_list



def extrator(url):

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    info_list = []
    elementos = soup.find_all('span', class_='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body')
    preco_ant = soup.find_all('span', class_='vtex-product-price-1-x-currencyContainer vtex-product-price-1-x-currencyContainer--summary')

    cont = 0

    for i in range(len(elementos)):
        info_list.append([])
        info_list[i].append(elementos[i].text)
        for j in range(cont, cont + 1):
            try:
                check = driver.find_element(By.XPATH, ('//*[@id="gallery-layout-container"]/div[' + str(i + 1) + ']/section/a/article/div[3]/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/span/span/span'))

            except NoSuchElementException:
                check = None

            if check != None:
                info_list[i].append(re.sub('\xa0', '', preco_ant[j].text))
                info_list[i].append(re.sub('\xa0', '', preco_ant[j + 1].text))
                cont += 2

            else:
                info_list[i].append('N/A')
                info_list[i].append(re.sub('\xa0', '', preco_ant[j].text))
                cont += 1


    return (info_list)



def conversor(inp):

    numero = 0

    dicionario = {
        '0': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        }
    
    for i in range(len(inp)):
        valor = dicionario[inp[i]]
        numero = numero * 10 + valor

    return(numero)





def main():

    lista_final = []

    todas_marcas = extracao_marcas()


    for i in range (len(todas_marcas)):

        urlas = criacao_url(todas_marcas[i], '1')

        inter = extracao_num_itens(urlas)

        print(inter)

        inter = conversor(inter)

        print(todas_marcas[i])

        print(inter)

        numero_de_paginas = inter // 15

        for j in range(1, numero_de_paginas + 1):

            time.sleep(2)

            sub_lista = extrator(criacao_url(todas_marcas[i], str(j)))

            lista_final.append(sub_lista)

            print(sub_lista)

    print(lista_final)

    driver.quit()

    

all_workers = os.cpu_count()

with ThreadPoolExecutor(max_workers=all_workers) as executor:
    executor.submit(main())

