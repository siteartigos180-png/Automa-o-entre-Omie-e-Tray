import os
import json
import requests
import time

def gerar_novo_token_tray():
    """Gera o Access Token oficial diretamente na nova loja vinculada pelo Mateus"""
    url_auth = "https://1501119.commercesuite.com.br/web_api/auth"
    
    # Puxa as credenciais do seu app que já estão salvas no GitHub
    consumer_key = os.environ.get("CONSUMER_KEY_TRAY")
    consumer_secret = os.environ.get("CONSUMER_SECRET_TRAY")
    
    # O Code oficial confirmado pelo suporte técnico hoje
    novo_code = "2a015d6992084e723cc9cd57fbf37790a2c9168b3e93bf526f53167ef62ba82e"
    
    payload = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "code": novo_code
    }
    headers = {"Content-Type": "application/json"}
    
    print("🔑 Autenticando o aplicativo Artigos180 na nova loja 1501119...")
    try:
        response = requests.post(url_auth, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            dados = response.json()
            token_gerado = dados.get("access_token")
            print("✅ Token de acesso gerado e validado com sucesso!")
            return token_gerado
        else:
            print(f"⚠️ Erro ao gerar token via API: {response.status_code} - {response.text}")
            print("💡 Tentando usar o Token reserva do ambiente...")
            return os.environ.get("ACCESS_TOKEN_TRAY")
    except Exception as e:
        print(f"❌ Falha crítica na autenticação: {str(e)}")
        return os.environ.get("ACCESS_TOKEN_TRAY")

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
        
        # Gera o token em tempo real para a nova loja ativa
        token_tray = gerar_novo_token_tray()
        return token_tray, produtos
    else:
        print(f"❌ Erro ao buscar na Omie: {response.status_code}")
        return None, []

def enviar_para_tray(token_tray, produtos):
    if not token_tray or not produtos:
        print("📭 Processo interrompido: Falha ao obter credenciais válidas da Tray.")
        return
        
    url_base_tray = "https://1501119.commercesuite.com.br/web_api/products"
    headers = {"Content-Type": "application/json"}
    
    print(f"🔄 Iniciando a carga dos produtos na loja homologada...")
    
    for item in sorted(produtos, key=lambda x: x.get("codigo_produto", "")):
        sku = str(item.get("codigo_produto", ""))
        nome = str(item.get("descricao", ""))
        preco = str(item.get("valor_venda", 0))
        peso = item.get("peso_liquido", 0)
        peso_gramas = str(int(peso * 1000)) if peso else "0"
        
        print(f"\n📦 Enviando: {nome} (SKU: {sku})")
        
        payload_produto = {
            "Product": {
                "code": sku,
                "name": nome,
                "price": preco,
                "cost_price": preco,
                "stock": "10",
                "weight": peso_gramas
            }
        }
        
        url_post = f"{url_base_tray}?access_token={token_tray}"
        
        try:
            response = requests.post(url_post, headers=headers, data=json.dumps(payload_produto))
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Produto cadastrado com sucesso na nova loja Tray!")
            elif response.status_code == 400 and "já cadastrado" in response.text.lower():
                print(f"  ⚠️ Produto já existente. Sincronizando dados...")
                url_busca = f"{url_base_tray}?access_token={token_tray}&code={sku}"
                res_busca = requests.get(url_busca, headers=headers)
                if res_busca.status_code == 200 and res_busca.json().get("Products"):
                    id_tray = res_busca.json()["Products"][0]["Product"]["id"]
                    url_put = f"{url_base_tray}/{id_tray}?access_token={token_tray}"
                    requests.put(url_put, headers=headers, data=json.dumps(payload_produto))
                    print(f"  ✅ Atualizado com sucesso (ID Interno: {id_tray})")
            else:
                print(f"  ❌ Erro no envio: {response.status_code} - Verifique a resposta do servidor.")
                
        except Exception as e:
            print(f"  ❌ Falha de comunicação: {str(e)}")
            
        time.sleep(0.6)

if __name__ == "__main__":
    token, lista_de_produtos = buscar_produtos_omie()
    enviar_para_tray(token, lista_de_produtos)
