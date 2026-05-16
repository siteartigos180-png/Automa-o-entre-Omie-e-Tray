import requests
import os
import json

def consultar_detalhes_na_omie():
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    
    app_key = os.getenv('APP_KEY_OMIE', '').strip()
    app_secret = os.getenv('APP_SECRET_OMIE', '').strip()
    
    # Payload estruturado exatamente como os métodos da documentação da Omie exigem
    payload = {
        "call": "ListarProdutos",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 10,
                "apenas_importado_api": "N"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🔍 Tentando ler dados estruturados de EAN/SKU direto na API da Omie...")
    
    resposta = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if respost_code := resposta.status_code == 200:
        dados = resposta.json()
        produtos = dados.get('produto_servico_cadastro', [])
        
        if produtos:
            print(f"🎉 CONEXÃO ESTABELECIDA COM A DOCUMENTAÇÃO! Dados encontrados:")
            print("-" * 90)
            for p in produtos:
                # Mapeando os nomes exatos das variáveis internas da Omie
                codigo_fabrica = p.get('codigo_produto')
                sku_integracao = p.get('codigo_produto_integracao')
                ean_barras = p.get('codigo_barras')
                peso_liq = p.get('peso_liquido')
                
                print(f"ID Omie: {codigo_fabrica} | SKU: {sku_integracao} | EAN: {ean_barras} | Peso: {peso_liq}kg | {p.get('descricao')}")
        else:
            print("✅ Conectado à Omie, mas o retorno veio sem itens cadastrados.")
    else:
        print(f"❌ Status da Resposta: {resposta.status_code}")
        print("Retorno do Servidor Omie:")
        print(resposta.text)

if __name__ == "__main__":
    consultar_detalhes_na_omie()
