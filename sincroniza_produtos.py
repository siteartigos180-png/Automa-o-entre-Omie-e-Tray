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
    if not token_tray or not whitespaces_produtos := produtos:
        print("📭 Nenhum produto para integrar ou Token da Tray ausente.")
        return
        
    # URL Base exata confirmada pelo suporte e pelo seu painel da Tray
    url_base_tray = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
    
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
        
        # Payload estruturado seguindo o padrão esperado pela API da Tray
        payload_produto = {
            "Product": {
                "code": str(sku),
                "name": nome,
                "price": str(preco),
                "weight": str(int(peso * 1000))  # Peso em gramas para a API padrão
            }
        }
        
        # Rota de POST (Criação) com o token na URL conforme indicado pelo Mateus
        url_post = f"{url_base_tray}?access_token={token_tray}"
        
        try:
            response = requests.post(url_post, headers=headers, data=json.dumps(payload_produto))
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Produto cadastrado com sucesso na Tray!")
            elif response.status_code == 400 and "já cadastrado" in response.text.lower():
                print(f"  ⚠️ Produto já existente. Buscando ID para atualizar...")
                
                # Se o produto já existe, precisamos achar o ID interno dele na Tray para atualizar
                url_busca = f"{url_base_tray}?access_token={token_tray}&code={sku}"
                res_busca = requests.get(url_busca, headers=headers)
                
                if res_busca.status_code == 200 and res_busca.json().get("Products"):
                    id_tray = res_busca.json()["Products"][0]["Product"]["id"]
                    
                    # Rota de PUT (Atualização) usando o ID do produto conforme indicado pelo Mateus
                    url_put = f"{url_base_tray}/{id_tray}?access_token={token_tray}"
                    response_put = requests.put(url_put, headers=headers, data=json.dumps(payload_produto))
                    
                    if response_put.status_code in [200, 204]:
                        print(f"  ✅ Dados atualizados com sucesso na Tray (ID: {id_tray})!")
                    else:
                        print(f"  ❌ Erro ao atualizar: {response_put.status_code} - {response_put.text}")
                else:
                    print(f"  ❌ Não foi possível recuperar o ID do produto para atualização.")
            else:
                print(f"  ❌ Resposta inesperada da Tray: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Falha de comunicação: {str(e)}")
            
        time.sleep(0.5)

if __name__ == "__main__":
    token, lista_de_produtos = buscar_produtos_omie()
    enviar_para_tray(token, lista_de_produtos)
