import os
import re
from bs4 import BeautifulSoup
from collections import deque

PASTA_HTML = "paginas_salvas"

def listar_pessoas_disponiveis(pasta):
    """Lê a pasta e retorna um conjunto com os nomes de todas as pessoas disponíveis (sem a extensão .html)."""
    if not os.path.isdir(pasta):
        return None
    
    # Pega todos os arquivos, remove a extensão .html e guarda em um conjunto (set) para busca rápida
    pessoas = {arquivo.replace(".html", "") for arquivo in os.listdir(pasta) if arquivo.endswith(".html")}
    return pessoas

def encontrar_grau_separacao(pessoa_inicio, pessoa_fim, pasta_html, todas_as_pessoas):
    """
    Encontra o caminho mais curto entre duas pessoas usando a busca em largura (BFS).
    """
    # Passo 1: Inicialização do BFS
    # A fila guarda tuplas: (pessoa_atual, caminho_ate_aqui)
    fila = deque([(pessoa_inicio, [pessoa_inicio])]) 
    # O conjunto de visitados evita que entremos em loops e refaçamos trabalho
    visitados = {pessoa_inicio}

    # Passo 2: Loop principal do BFS
    # Continua enquanto houver pessoas na fila para explorar
    while fila:
        pessoa_atual, caminho = fila.popleft()
        
        print(f"Explorando a partir de: {pessoa_atual}...")

        # Abre e parseia o arquivo HTML da pessoa atual
        caminho_arquivo = os.path.join(pasta_html, f"{pessoa_atual}.html")
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
        except FileNotFoundError:
            # Se o arquivo de uma pessoa no caminho não existir, pula.
            continue
        
        # Passo 3: Encontrar todos os links para outras pessoas na página
        area_conteudo = soup.find("div", {"id": "bodyContent"})
        if not area_conteudo:
            continue
            
        # Regex para encontrar links válidos de verbetes
        regex_links_validos = re.compile(r"^/wiki/((?!:).)*$")
        links_encontrados = area_conteudo.find_all("a", href=regex_links_validos)

        for link in links_encontrados:
            href = link.get('href')
            if not href:
                continue
                
            # Extrai o nome do verbete do link (ex: /wiki/Santos_Dumont -> Santos_Dumont)
            nome_vizinho = href.split('/')[-1]

            # Passo 4: Processar o vizinho encontrado
            # Verifica se o link é para uma pessoa que temos em nossa base de dados
            if nome_vizinho in todas_as_pessoas:
                # Se o vizinho é a pessoa que estamos procurando, encontramos o caminho!
                if nome_vizinho == pessoa_fim:
                    caminho_final = caminho + [nome_vizinho]
                    return caminho_final # Retorna a lista de pessoas no caminho

                # Se for um vizinho que ainda não visitamos...
                if nome_vizinho not in visitados:
                    visitados.add(nome_vizinho) # Marca como visitado
                    novo_caminho = caminho + [nome_vizinho] # Cria o novo caminho
                    fila.append((nome_vizinho, novo_caminho)) # Adiciona à fila para explorar depois
    
    # Se o loop terminar e não encontrarmos a pessoa, não há conexão
    return None

# --- Bloco Principal de Execução ---
if _name_ == "_main_":
    # Carrega a lista de todas as pessoas que temos salvas
    pessoas_disponiveis = listar_pessoas_disponiveis(PASTA_HTML)
    
    if pessoas_disponiveis is None:
        print(f"Erro: A pasta '{PASTA_HTML}' não foi encontrada. Certifique-se de que ela existe e contém os arquivos .html.")
    elif not pessoas_disponiveis:
        print(f"A pasta '{PASTA_HTML}' está vazia. Rode o crawler primeiro para coletar as páginas.")
    else:
        print("--- Grau de Separação na Wikipédia ---")
        print(f"Encontradas {len(pessoas_disponiveis)} pessoas na sua base de dados.")
        
        # Pede a entrada do usuário
        pessoa_a = input("Digite o nome da primeira pessoa (ex: Santos_Dumont): ").strip()
        pessoa_b = input("Digite o nome da segunda pessoa (ex: Machado_de_Assis): ").strip()

        # Valida a entrada
        if pessoa_a not in pessoas_disponiveis or pessoa_b not in pessoas_disponiveis:
            print("Erro: Uma ou ambas as pessoas não foram encontradas na sua base de dados.")
            print("Verifique se o nome está escrito exatamente como no nome do arquivo .html.")
        else:
            print("\nIniciando a busca pelo caminho mais curto...")
            caminho_encontrado = encontrar_grau_separacao(pessoa_a, pessoa_b, PASTA_HTML, pessoas_disponiveis)
            
            print("\n--- Resultado ---")
            if caminho_encontrado:
                grau = len(caminho_encontrado) - 1
                print(f"✅ Conexão encontrada com Grau de Separação {grau}!")
                print(" -> ".join(caminho_encontrado))
            else:
                print(f"❌ Não foi encontrada uma conexão entre {pessoa_a} e {pessoa_b} na sua base de dados.")