import os
import json
import requests
import time

def gerar_novo_token_tray():
    # URL Corrigida: Removido o ponto extra antes de commercesuite
    url_auth = "https://siteartigos180comercio.commercesuite.com.br/web_api/auth"
    payload_form = {
        "consumer_key": os.environ.get("CONSUMER_KEY"),
        "consumer_secret": os.environ.get("CONSUMER_SECRET"),
        "code": os.environ.get("CODE_TRAY")
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(url_auth, headers=headers, data=payload_form)
        if response.status_code in [200, 201]:
            dados = response.json()
            return dados.get("access_token")
        else:
            print(f"⚠️ Erro ao gerar token Tray: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro de conexão com API da Tray: {str(e)}")
        return None

def puxar_produtos_omie():
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    payload = {
        "call": "ListarProdutos",
        "app_key": os.environ.get("APP_KEY_OMIE", "").strip(),
        "app_secret": os.environ.get("APP_SECRET_OMIE", "").strip(),
        "param": [{
            "pagina": 1,
            "registros_por_pagina": 10,
            "apenas_importado_api": "N"
        }]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            dados = response.json()
            return dados.get("produto_service_cadastro", [])
        else:
            print(f"⚠️ Erro ao puxar dados da Omie: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro de conexão com Omie: {str(e)}")
        return []

def enviar_para_tray():
    print("🚀 Iniciando Motor de Integração Customizado...")
    
    # 1. Pega o token da Tray
    token_tray = gerar_novo_token_tray()
    if not token_tray:
        print("❌ Interrompendo: Não foi possível obter o Token da Tray.")
        return
        
    # 2. Puxa os produtos cadastrados na Omie
    produtos_omie = puxar_produtos_omie()
    if not produtos_omie:
        print("⚠️ Nenhum produto encontrado na Omie para sincronizar.")
        return
        
    print(f"📦 Encontrados {len(produtos_omie)} produtos na Omie. Iniciando envio para a Tray...")
    
    # URL Corrigida aqui também
    url_post_tray = f"https://siteartigos180comercio.commercesuite.com.br/web_api/products?access_token={token_tray}"
    headers_tray = {"Content-Type": "application/json"}
    
    # 3. Varre os produtos da Omie e cadastra um por um na Tray
    for p in sorted(produtos_omie, key=lambda x: x.get('codigo_produto', 0)):
        payload_tray = {
            "Product": {
                "ean": p.get('codigo_barras', ''),
                "name": p.get('descricao', 'Produto Sem Nome'),
                "reference": p.get('codigo_produto_integracao', ''),
                "weight": str(p.get('peso_liquido', '0'))
            }
        }
        
        try:
            print(f"⚡ Enviando ID Omie {p.get('codigo_produto')} - {p.get('descricao')}...")
            response = requests.post(url_post_tray, data=json.dumps(payload_tray), headers=headers_tray)
            
            if response.status_code in [200, 201]:
                print(f"✅ Sucesso absoluto! Produto cadastrado na Tray.")
            else:
                print(f"🔴 A API da Tray rejeitou este item. Status: {response.status_code} - Retorno: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao disparar requisição para a Tray: {str(e)}")
            
        time.sleep(0.5)

if __name__ == "__main__":
    enviar_para_tray()
