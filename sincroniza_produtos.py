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
        
    # URL Base oficial extraída do seu bloco de código da Tray
    url_base_tray = "https://391250.commercesuite.com.br/web_api/products"
    
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
        
        # Mapeamento ajustado rigorosamente para evitar a rejeição 400 do servidor da Tray
        payload_produto = {
            "Product": {
                "code": str(sku),
                "name": str(nome),
                "price": str(preco),
                "cost_price": str(preco),
                "stock": "0",
                "weight": str(int(peso * 1000)) if peso else "0"
            }
        }
        
        url_post = f"{url_base_tray}?access_token={token_tray}"
        
        try:
            response = requests.post(url_post, headers=headers, data=json.dumps(payload_produto))
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Produto cadastrado com sucesso na Tray!")
            elif response.status_code == 400:
                # Se der erro 400, verificamos se é porque já existe ou se precisa forçar o PUT
                print(f"  ⚠️ Verificando se o produto já existe no catálogo para atualizar...")
                url_busca = f"{url_base_tray}?access_token={token_tray}&code={sku}"
                res_busca = requests.get(url_busca, headers=headers)
                
                if res_busca.status_code == 200 and res_busca.json().get("Products"):
                    id_tray = res_busca.json()["Products"][0]["Product"]["id"]
                    url_put = f"{url_base_tray}/{id_tray}?access_token={token_tray}"
                    response_put = requests.put(url_put, headers=headers, data=json.dumps(payload_produto))
                    
                    if response_put.status_code in [200, 204]:
                        print(f"  ✅ Dados atualizados com sucesso na Tray (ID: {id_tray})!")
                    else:
                        print(f"  ❌ Erro ao atualizar: {response_put.status_code}")
                else:
                    print(f"  ❌ Falha no formato do cadastro. Retorno do servidor: {response.status_code}")
            else:
                print(f"  ❌ Resposta inesperada do servidor: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Falha de comunicação: {str(e)}")
            
        time.sleep(0.5)

if __name__ == "__main__":
    token, lista_de_produtos = buscar_produtos_omie()
    enviar_para_tray(token, lista_de_produtos)
