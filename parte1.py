import requests
from bs4 import BeautifulSoup
import time
import re
import os #Bibliopteca para tratar com o Sistema Operacional
from collections import deque

# --- 1. CONFIGURAÇÃO INICIAL ---
URL_BASE = "https://pt.wikipedia.org"
PAGINA_INICIAL = "/wiki/Wikip%C3%A9dia:P%C3%A1gina_principal"
PASTA_SALVAR = "paginas_salvas" # Pasta onde os arquivos HTML serão salvos

# Cria a pasta para salvar os arquivos se ela não existir
os.makedirs(PASTA_SALVAR, exist_ok=True)

header = {'User-agent': 'Mozilla/5.0'}

# --- 2. ESTRUTURAS DE DADOS DO CRAWLER ---
# Fila de links para visitar. Começamos com a página principal.
fila_links = deque([PAGINA_INICIAL]) 
# Conjunto (set) para guardar os links já visitados.
links_visitados = {PAGINA_INICIAL}

contador_pessoas_encontradas = 0

# --- 3. LOOP PRINCIPAL DO CRAWLER ---
# O crawler continua enquanto houver links na fila e o limite não for atingido.
while fila_links and contador_pessoas_encontradas < 50:
    
    # Passo 7: Escolha um link não visitado para ser a próxima página.
    url_relativo = fila_links.popleft() # Pega o próximo link da fila (o mais antigo)
    
    pagina_completa = URL_BASE + url_relativo
    
    try:
        # Passo 1: Obtenha uma página.
        resposta = requests.get(pagina_completa, headers=header, timeout=1)
        resposta.raise_for_status()#indica o status da requisição
        soup = BeautifulSoup(resposta.content, "html.parser")
        
        # Passo 2: Verifique se a página se refere à uma pessoa.
        infobox = soup.find("table", class_="infobox")
        e_uma_pessoa = False
        if infobox:
            label_nascimento = infobox.find("th", class_="infobox-label", string=re.compile(r"Nascimento"))
            if not label_nascimento:
                label_nascimento = infobox.find("td", scope="row", string=re.compile(r"Nascimento"))
            
            if label_nascimento:
                e_uma_pessoa = True

        if e_uma_pessoa:
            # Passo 3: Salve a página como um arquivo html.
            titulo_verbete = url_relativo.split('/')[-1] # Pega o nome do verbete pela URL
            nome_arquivo = f"{titulo_verbete}.html"
            caminho_arquivo = os.path.join(PASTA_SALVAR, nome_arquivo)
            
            with open(caminho_arquivo, "wb") as f: # "wb" para escrever em modo binário, preservando a codificação
                f.write(resposta.content)
            print(pagina_completa)
            print(f"Pessoa encontrada! Página salva em: {caminho_arquivo}\n")
           
        else:
            print(pagina_completa)
            print("Não é uma pessoa. \n")
        area_conteudo = soup.find("div", {"id": "bodyContent"})
        if area_conteudo:
            regex_links_validos = re.compile(r"^(/wiki/)((?!:).)*$")
            links_encontrados = area_conteudo.find_all("a", href=regex_links_validos)
            
            novos_links_adicionados = 0
            for link in links_encontrados:
                href = link.get('href')
                if href:
                    # Passo 5: Filtre os links... dos verbetes que já foram visitados.
                    if href not in links_visitados:
                        # Passo 6: Guarde esses links em uma lista (nossa fila e conjunto de visitados).
                        links_visitados.add(href)
                        fila_links.append(href)
                        novos_links_adicionados += 1
    
    except requests.exceptions.RequestException as e:
        print("\n")
    except Exception as e:
        print("\n")
    
    # Pausa para não sobrecarregar o servidor
    time.sleep(0.5)

print(f"Total de páginas de pessoas encontradas e salvas: {contador_pessoas_encontradas}")