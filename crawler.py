import requests
from bs4 import BeautifulSoup
import time
import re
import os
from collections import deque

URL_BASE = "https://pt.wikipedia.org"
PAGINA_INICIAL = "/wiki/Wikip%C3%A9dia:P%C3%A1gina_principal"
PASTA_SALVAR = "paginas_salvas"

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Cria a pasta "paginas_salvas" se ela ainda não existir
if not os.path.isdir(PASTA_SALVAR):
    os.makedirs(PASTA_SALVAR)

# Cria uma fila (deque) que já começa com a página principal.
fila_links = deque([PAGINA_INICIAL]) 
# Cria um set para guardar os links já visitados
links_visitados = {PAGINA_INICIAL}

contador_paginas_processadas = 0
contador_pessoas_encontradas = 0
LIMITE_PESSOAS = 50 # Limite de pessoas a serem encontradas

# Cria o while que percorre as páginas (crawler)
while fila_links and contador_pessoas_encontradas < LIMITE_PESSOAS:
    print("fila de links:", len(fila_links))

    # Pega o próximo link da fila de links não visitados
    prox_url = fila_links.popleft()

    # Cria a URL completa
    pagina_completa = URL_BASE + prox_url

    print(f"({contador_paginas_processadas + 1}) Processando: {pagina_completa}")
    contador_paginas_processadas += 1

    try:
        # Pega o html da página
        resposta = requests.get(pagina_completa, headers=header)
        resposta.raise_for_status() # Garante que a requisição foi bem sucedida
        soup = BeautifulSoup(resposta.content, "html.parser")
        
        pessoa = False
        infobox = soup.find("table", class_="infobox")

        if infobox:
            # Verifica se a página possui a label "Nascimento"
            label_nascimento = infobox.find("th", class_="infobox-label", string=re.compile(r"Nascimento"))
            if not label_nascimento:
                label_nascimento = infobox.find("td", scope="row", string=re.compile(r"Nascimento"))
            if label_nascimento:
                pessoa = True

        # Verifica se a página é de uma pessoa
        if pessoa:
            # Salva a página como um arquivo .html
            titulo_pagina = pagina_completa.split('/')[-1]
            nome_arquivo = f"{titulo_pagina}.html"  # Nome do arquivo
            caminho_arquivo = os.path.join(PASTA_SALVAR, nome_arquivo)  # Caminho completo do arquivo

            # Salva o conteúdo da página
            with open(caminho_arquivo, "wb") as f:
                f.write(resposta.content)

            contador_pessoas_encontradas += 1
            print(f"✅ Pessoa encontrada! {contador_pessoas_encontradas}/{LIMITE_PESSOAS} Página salva em: {caminho_arquivo}\n")

            # Se for uma pessoa, adiciona TODOS os links da página na fila
            area_conteudo = soup.find("div", {"id": "bodyContent"})  # Área de conteúdo da página
            if area_conteudo:
                regex_links_validos = re.compile(r"^/wiki/((?!:).)*$") 
                links_encontrados = area_conteudo.find_all("a", href=regex_links_validos)

                for link in links_encontrados:
                    href = link.get('href')
                    if href and href not in links_visitados:
                        links_visitados.add(href)
                        fila_links.append(href)
        
        else: 
            print("Não é uma página de pessoa.\n")

        # Se a fila estiver vazia após o processamento, pega apenas UM link da página atual para não parar
        if not fila_links:
            area_conteudo = soup.find("div", {"id": "bodyContent"})
            if area_conteudo:
                regex_links_validos = re.compile(r"^/wiki/((?!:).)*$")
                links_encontrados = area_conteudo.find_all("a", href=regex_links_validos)
                for link in links_encontrados:
                    href = link.get('href')
                    if href and href not in links_visitados:
                        links_visitados.add(href)
                        fila_links.append(href)
                        break # Sai do loop para garantir que apenas UM link seja adicionado

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}\n")

    time.sleep(0.5)

print("---------------------------------------------------------")
print("Crawler finalizado!")
print(f"Total de páginas processadas: {contador_paginas_processadas}")
print(f"Total de páginas de pessoas encontradas e salvas: {contador_pessoas_encontradas}")