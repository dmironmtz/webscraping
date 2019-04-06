import os
import csv
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
categorias = []
# Recorremos los enlaces a las recetas
for link in links:
    if "plato" in str(link):
        #añadimos el plato al array de categorias
        categoria = link.contents[0]
        if categoria not in categorias:
            categorias.append(categoria)
        # Recorremos las recetas de cada categoria

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

# Array en el que almacenar la información de las recetas
array_recetas_data = []

conta = 0
# Ahora que tenemos las urls de todas las recetas vamos a extraer la información de cada una de ellas
for receta in array_recetas:
    result = requests.get(receta)
    if result.status_code == 200:
        conta += 1
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        # Si encontramos el menu de la categoria y titulo
        if soup.find(class_="cb-breadcrumbs"):
            # Extraemos la categoria
            categoria = soup.find(class_="cb-breadcrumbs").find_all('a')[1].contents[0]
            # Si la receta está en alguna de las categorías seguimos, si no saltamos la receta
            if categoria in categorias:    
                # Extraemos el titulo
                titulo = soup.find(class_="breadcrumb_last").contents[0].replace(",","")
                # Extraemos las instrucciones
                instrucciones = "Instrucciones: "
                # En primer lugar buscamos las instrucciones del panel Instrucciones
                if soup.find("span", string="Instrucciones"):
                    div_inst_act = soup.find("span", string="Instrucciones").find_parent('div').find_next_sibling('div')
                    arr_inst_act = [item.find_next("span").text for item in div_inst_act.find_all('span', class_='wpurp-recipe-instruction-text')]
                    arr_inst_act.pop()
                
                    inst_num = 1
                    for inst in arr_inst_act:
                        instrucciones += str(inst_num) + ") " + inst.replace(",","") + " " 
                        inst_num += 1
                
                    # Ahora hay que buscar si la receta tiene más instrucciones
                    arr_inst_extra = soup.find_all("span", class_="wpurp-recipe-instruction-group")
                    # Si hay mas instrucciones
                    if arr_inst_extra:
                        for inst_extra in arr_inst_extra:
                            # Nos quedamos con el titulo de la preparacion
                            titulo = inst_extra.contents[0]
                            # Extraemos las instrucciones
                            div_inst_act = inst_extra.find_parent('div').find_next_sibling('div')
                            arr_inst_act = [item.find_next("span").text for item in div_inst_act.find_all('span', class_='wpurp-recipe-instruction-text')]
                            arr_inst_act.pop()
                        
                            instrucciones += ". <<" + titulo + ">> "
                            inst_num = 1
                            for inst in arr_inst_act:
                                instrucciones += str(inst_num) + ") " + inst.replace(",","") + " " 
                                inst_num += 1
                
                    array_recetas_data.append([titulo, categoria, receta, "", "", instrucciones])
    # Para pruebas
    if conta > 50:       
        break

# Creacion del csv
currentDir = os.path.dirname(__file__)
filename = "recetas_dataset.csv"
filePath = os.path.join(currentDir, filename)

with open(filePath, 'w', newline='') as csvFile:
  writer = csv.writer(csvFile)
  writer.writerow(["Titulo", "Categoria", "Url", "Raciones", "Ingredientes", "Instrucciones"])
  for receta_data in array_recetas_data:
      writer.writerow(receta_data)
