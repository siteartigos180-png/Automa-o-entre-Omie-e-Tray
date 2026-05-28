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
        
    url_base_tray = "https://391250.commercesuite.com.br/web_api/products"
    headers = {"Content-Type": "application/json"}
    
    print(f"🔄 Iniciando verificação e envio de {len(produtos)} produtos para a Tray...")
    
    for item in sorted(produtos, key=lambda x: x.get("codigo_produto", "")):
        sku = str(item.get("codigo_produto", ""))
        nome = str(item.get("descricao", ""))
        preco = str(item.get("valor_venda", 0))
        peso = item.get("peso_liquido", 0)
        peso_gramas = str(int(peso * 1000)) if peso else "0"
        
        print(f"\n📦 Analisando: {nome} (SKU: {sku})")
        
        # 1️⃣ PASSO: Consultar se o SKU já existe na Tray para pegar o ID correto
        url_busca = f"{url_base_tray}?access_token={token_tray}&code={sku}"
        id_tray = None
        
        try:
            res_busca = requests.get(url_busca, headers=headers)
            if res_busca.status_code == 200:
                dados_busca = res_busca.json()
                if dados_busca.get("Products"):
                    # Produto localizado! Capturamos o ID interno gerado pela Tray
                    id_tray = dados_busca["Products"][0]["Product"]["id"]
                    print(f"  🔍 Produto já existente na Tray com o ID Interno: {id_tray}")
        except Exception as e:
            print(f"  ⚠️ Falha ao verificar existência: {str(e)}")

        # Estrutura padrão de envio (Payload)
        payload_produto = {
            "Product": {
                "code": sku,
                "name": nome,
                "price": preco,
                "cost_price": preco,
                "weight": peso_gramas
            }
        }

        # 2️⃣ PASSO: Decidir se atualiza pelo ID ou se cria um novo comercialmente
        try:
            if id_tray:
                # Se temos o ID interno, atualizamos usando a rota correta do ID
                url_put = f"{url_base_tray}/{id_tray}?access_token={token_tray}"
                response = requests.put(url_put, headers=headers, data=json.dumps(payload_produto))
                if response.status_code in [200, 204]:
                    print(f"  ✅ Dados atualizados com sucesso (ID: {id_tray})!")
                else:
                    print(f"  ❌ Erro na atualização do ID {id_tray}: {response.status_code}")
            else:
                # Se não existe, criamos um novo usando o POST tradicional
                url_post = f"{url_base_tray}?access_token={token_tray}"
                response = requests.post(url_post, headers=headers, data=json.dumps(payload_produto))
                if response.status_code in [200, 201]:
                    print(f"  ✅ Novo produto cadastrado com sucesso na Tray!")
                else:
                    print(f"  ❌ Erro no cadastro do novo produto: {response.status_code}")
                    
        except Exception as e:
            print(f"  ❌ Falha de comunicação no envio: {str(e)}")
            
        time.sleep(0.6) # Evita estouro de requisições por segundo (Rate Limit)

if __name__ == "__main__":
    token, lista_de_produtos = buscar_produtos_omie()
    enviar_para_tray(token, lista_de_produtos)
