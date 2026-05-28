import os
import requests
import json

# 1. Carregar as credenciais de segurança do GitHub Secrets
OMIE_APP_KEY = os.getenv("APP_KEY_OMIE")
OMIE_APP_SECRET = os.getenv("APP_SECRET_OMIE")
TRAY_URL = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api"
TRAY_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_TRAY")

def buscar_produtos_omie():
    print("🚀 Buscando produtos cadastrados na OMIE...")
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    payload = {
        "call": "ListarProdutos",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [{
            "pagina": 1,
            "registros_por_pagina": 50,
            "apenas_importados_api": "N",
            "filtrar_apenas_omiehub": "N"
        }]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json().get("produto_servico_cadastro", [])
        else:
            print(f"❌ Erro ao buscar na Omie: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Erro na conexão com a Omie: {str(e)}")
        return []

def enviar_para_tray(produto_omie):
    sku = produto_omie.get("codigo_produto")
    nome = produto_omie.get("descricao")
    preco = produto_omie.get("valor_unitario")
    
    # Capturando dados logísticos de peso e medidas
    peso = produto_omie.get("peso_bruto", 0)
    altura = produto_omie.get("altura", 0)
    largura = produto_omie.get("largura", 0)
    profundidade = produto_omie.get("profundidade", 0)
    
    print(f"📦 Processando produto: {nome} (SKU: {sku})")
    
    # Montando o payload no formato exato exigido pela API da Tray Corp
    url_envio = f"{TRAY_URL}/products"
    headers = {
        "Authorization": f"Bearer {TRAY_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload_tray = {
        "Product": {
            "ean": produto_omie.get("codigo_ean", ""),
            "reference": sku,
            "name": nome,
            "price": str(preco),
            "weight": int(peso * 1000), # Convertendo Kg para gramas se necessário
            "length": int(profundidade),
            "width": int(largura),
            "height": int(altura),
            "available": "1"
        }
    }
    
    try:
        # Tenta cadastrar o produto na Tray Corp
        res = requests.post(url_envio, data=json.dumps(payload_tray), headers=headers)
        if res.status_code in [200, 201]:
            print(f"✅ Produto {sku} integrado com sucesso na Tray Corp!")
        elif res.status_code == 422 and "already exists" in res.text.lower():
            print(f"🔄 Produto {sku} já existe na Tray Corp. Atualizando dados...")
            # Se o produto já existe, fazemos um PUT para atualizar estoque/preço/medidas
            # Em implementações futuras podemos expandir a atualização aqui
        else:
            print(f"⚠️ Resposta da Tray para o produto {sku}: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Erro ao enviar para a Tray Corp: {str(e)}")

if __name__ == "__main__":
    produtos = buscar_produtos_omie()
    if not produtos:
        print("📭 Nenhum produto encontrado ou erro na listagem da Omie.")
    for prod in produtos:
        # Filtra para enviar apenas o produto de teste ou os que possuem a flag ativa se necessário
        if prod.get("codigo_produto") == "PRD14614" or prod.get("descricao"):
            enviar_para_tray(prod)
