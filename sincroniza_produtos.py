import os
import json
import requests

def buscar_produtos_omie():
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    
    app_key = os.environ.get("APP_KEY_OMIE")
    app_secret = os.environ.get("APP_SECRET_OMIE")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "call": "ListarProdutos",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 50,
                "filtrar_apenas_omiepdv": "N"
            }
        ]
    }
    
    print("🚀 Buscando produtos cadastrados na OMIE...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        dados = response.json()
        produtos = dados.get("produto_servico_cadastro", [])
        print(f"✅ Sucesso! Encontrados {len(produtos)} produtos na Omie.")
        return os.environ.get("ACCESS_TOKEN_TRAY"), produtos
    else:
        print(f"❌ Erro ao buscar na Omie: {response.status_code} - {response.text}")
        return None, []

def enviar_para_tray(token_tray, produtos):
    if not token_tray or not produtos:
        print("📭 Nenhum produto encontrado ou erro na listagem da Omie.")
        return
        
    print(f"🔄 Iniciando envio de {len(produtos)} produtos para a Tray Corp...")
    # Aqui o robô continuará a execução para cada produto encontrado

if __name__ == "__main__":
    token, lista_de_produtos = buscar_produtos_omie()
    enviar_para_tray(token, lista_de_produtos)
