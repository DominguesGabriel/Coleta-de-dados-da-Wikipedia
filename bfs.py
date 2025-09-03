import os
import re
from bs4 import BeautifulSoup
from collections import deque

PASTA_HTML = "paginas_salvas"

def listar_pessoas_disponiveis(pasta):
    # Lê a pasta e retorna um conjunto com os nomes de todas as pessoas disponíveis (sem a extensão .html).
    if not os.path.isdir(pasta):
        return None
    
    # Pega todos os arquivos, remove a extensão .html e guarda em um conjunto set
    pessoas = {arquivo.replace(".html", "") for arquivo in os.listdir(pasta) if arquivo.endswith(".html")}
    return pessoas

# Encontra o caminho mais curto entre duas pessoas usando bfs.
def encontrar_grau_separacao(pessoa_inicio, pessoa_fim, pasta_html, todas_as_pessoas):

    # Fila de busca: (pessoa_atual, caminho_ate_aqui)
    fila = deque([(pessoa_inicio, [pessoa_inicio])])
    # O conjunto de visitados evita que entremos em loops e refaçamos trabalho
    visitados = {pessoa_inicio}

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
                
            # Extrai o nome do verbete do link
            nome_vizinho = href.split('/')[-1]

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
if __name__ == "__main__":
    # Carrega a lista de todas as pessoas que temos salvas
    pessoas_disponiveis = listar_pessoas_disponiveis(PASTA_HTML)
    print("--------------------------------------------------")
    
    if pessoas_disponiveis is None:
        print(f"Erro: Não tem a pasta '{PASTA_HTML}'.")
    elif not pessoas_disponiveis:
        print(f"Erro: A pasta '{PASTA_HTML}' está vazia.")
    else:
        # Pede a entrada do usuário
        pessoa_a = input("Nome da primeira pessoa (igual na pasta): ").strip()
        pessoa_b = input("Nome da segunda pessoa (igual na pasta): ").strip()

        # Valida a entrada
        if pessoa_a not in pessoas_disponiveis or pessoa_b not in pessoas_disponiveis:
            print("Erro: Nome das pessoas não foi encontrado na base de dados")
        else:
            caminho_encontrado = encontrar_grau_separacao(pessoa_a, pessoa_b, PASTA_HTML, pessoas_disponiveis)
            
            print("\n--------- Resultado -----------------")
            if caminho_encontrado:
                grau = len(caminho_encontrado) - 1
                print(f"✅ Conexão encontrada com grau de separação {grau}!")
                print(" -> ".join(caminho_encontrado))
            else:
                print(f"❌ Não foi encontrada uma conexão entre {pessoa_a} e {pessoa_b}.")