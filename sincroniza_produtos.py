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
        
    # URL da API da Tray Corp para gerenciamento de produtos
    url_tray = "https://api.traycorp.com.br/v2/products"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token_tray}"
    }
    
    print(f"🔄 Iniciando envio de {len(produtos)} produtos para a Tray Corp...")
    
    for item in sorted(produtos, key=lambda x: x.get("codigo_produto", "")):
        # Coleta os dados essenciais da Omie para mapear na Tray
        sku = item.get("codigo_produto", "")
        nome = item.get("descricao", "")
        preco = item.get("valor_venda", 0)
        peso = item.get("peso_liquido", 0)
        
        print(f"\n📦 Processando: {nome} (SKU: {sku})")
        
        # Estrutura o payload padrão que a Tray Corp espera receber
        payload_produto = {
            "product": {
                "code": str(sku),
                "name": nome,
                "price": float(preco),
                "weight": float(peso)
            }
        }
        
        try:
            # Tenta enviar o produto para a Tray Corp
            response = requests.post(url_tray, headers=headers, data=json.dumps(payload_produto))
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Produto integrado com sucesso na Tray Corp!")
            elif response.status_code == 422:
                # Se o produto já existir, nós enviamos um comando de atualização (PUT)
                print(f"  ⚠️ Produto já existente. Atualizando dados na Tray...")
                url_update = f"{url_tray}/code/{sku}"
                response_put = requests.put(url_update, headers=headers, data=json.dumps(payload_produto))
                if response_put.status_code in [200, 204]:
                    print(f"  ✅ Dados atualizados com sucesso na Tray Corp!")
                else:
                    print(f"  ❌ Erro ao atualizar na Tray: {response_put.status_code} - {response_put.text}")
            else:
                print(f"  ❌ Erro ao cadastrar na Tray: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Falha de conexão ao enviar o produto: {str(e)}")
            
        # Pequena pausa de segurança para respeitar o limite de requisições por segundo da API
        time.sleep(0.5)

if __name__ == "__main__":
    token, lista_de_produtos = buscar_produtos_omie()
    enviar_para_tray(token, lista_de_produtos)
