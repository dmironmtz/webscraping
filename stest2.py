# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 16:48:27 2019

@author: alfon
"""
import numpy as np
import requests
from bs4 import BeautifulSoup

url = "https://www.eladerezo.com/"

result = requests.get(url)
src = result.content
soup = BeautifulSoup(src, 'lxml')

# Funcion para eliminar duplicados
def eliminar_duplicados(x): 
  return list(dict.fromkeys(x))

# Funcion para extraer las urls de las recetas de una pagina
def extraer_links_recetas(url):
    array_recetas = []
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    # recorremos las recetas de la pagina actual
    recetas_pag_act = soup.find_all('h2', class_="cb-post-title")
    for receta in recetas_pag_act:
        if "recetas" in str(receta):
            link_receta = receta.a
            array_recetas.append(link_receta['href'])
    return array_recetas

# Extraemos los enlaces y eliminamos duplicados
links = soup.find_all('a')
links = list(dict.fromkeys(links))
links = eliminar_duplicados(links)

# En primer lugar vamos a almacenar los links de todas las recetas

array_recetas = []

# Recorremos los enlaces a las recetas
for link in links:
    if "plato" in str(link):
        # Recorremos las recetas de cada categoria
        categoria = link.contents[0]
        print(categoria)
        
        #Extraemos las recetas de la pagina actual
        
        array_recetas += extraer_links_recetas(link['href'])
        
        #Comprobamos si esta categoria tiene mas de una pagina
        result = requests.get(link['href'])
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        
        nav_pag = soup.find('ul', class_="page-numbers")
        # Si hay mas de una pagina
        if nav_pag:
            nav_pag_len = len(nav_pag.find_all('li'))
            # Almacenamos cuantas paginas hay
            last_pag = nav_pag.find_all('li')[nav_pag_len-2].find('a').contents[0]
            last_pag_int = int(str(last_pag))
            # La primera pagina que vamos a recorrer es la 2
            curr_pag = 2
            # Recorremos todas las paginas
            while curr_pag < last_pag_int + 1:
                array_recetas += extraer_links_recetas(link['href'] + '/page/' + str(curr_pag))
                curr_pag += 1
                
array_recetas = list(dict.fromkeys(array_recetas))            
array_recetas = eliminar_duplicados(array_recetas)
print(len(array_recetas))