import os
import json
import requests
import time

def buscar_produtos_omie():
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    app_key = os.environ.get("APP_KEY_OMIE")
    app_secret = os.environ.get("APP_SECRET_OMIE")
    
    headers = {"Content-Type": "application/json"}
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
        print("📭 Nenhum produto para integrar ou Token da Tray ausente.")
        return
        
    # Corrigido para o endpoint correto da API global da Tray Commerce
    url_base_tray = "https://api.tray.com.br/products"
    
    # Na API padrão da Tray, o token geralmente vai como query param 'access_token' ou no header editado
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🔄 Iniciando envio de {len(produtos)} produtos para a Tray...")
    
    for item in sorted(produtos, key=lambda x: x.get("codigo_produto", "")):
        sku = item.get("codigo_produto", "")
        nome = item.get("descricao", "")
        preco = item.get("valor_venda", 0)
        peso = item.get("peso_liquido", 0)
        
        print(f"\n📦 Processando: {nome} (SKU: {sku})")
        
        payload_produto = {
            "Product": {
                "code": str(sku),
                "name": nome,
                "price": str(preco),
                "weight": str(int(peso * 1000)) # Tray padrão costuma ler peso em gramas inteiras
            }
        }
        
        # Injetando o parâmetro de acesso direto na URL da requisição
        url_envio = f"{url_base_tray}?access_token={token_tray}"
        
        try:
            response = requests.post(url_envio, headers=headers, data=json.dumps(payload_produto))
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Produto integrado com sucesso na Tray!")
            elif response.status_code in [400, 422] or "já existe" in response.text.lower():
                print(f"  ⚠️ Produto possivelmente já existente. Tentando atualizar dados...")
                # Rota de atualização na Tray padrão usa o ID ou Code
                url_update = f"{url_base_tray}/code/{sku}?access_token={token_tray}"
                response_put = requests.put(url_update, headers=headers, data=json.dumps(payload_produto))
                if response_put.status_code in [200, 204]:
                    print(f"  ✅ Dados atualizados com sucesso na Tray!")
                else:
                    print(f"  ❌ Erro ao atualizar: {response_put.status_code} - {response_put.text}")
            else:
                print(f"  ❌ Erro ao cadastrar na Tray: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Falha de conexão: {str(e)}")
            
        time.sleep(0.6)

if __name__ == "__main__":
    token, lista_de_produtos = buscar_produtos_omie()
    enviar_para_tray(token, lista_de_produtos)
