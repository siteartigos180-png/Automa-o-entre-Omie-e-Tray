import requests
import os
import json

def listar_produtos_omie_autenticado():
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    
    app_key = os.getenv('APP_KEY_OMIE', '').strip()
    app_secret = os.getenv('APP_SECRET_OMIE', '').strip()
    
    # Payload com estrutura estrita de tipos de dados para chaves existentes
    payload = {
        "call": "ListarProdutos",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 20,
                "apenas_importado_api": "N",
                "filtrar_apenas_omiepdv": "N"
            }
        ]
    }
    
    # Cabeçalhos robustos imitando uma chamada de sistema homologado
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cache-Control": "no-cache"
    }
    
    print("🚀 Disparando requisição POST automatizada com emulação de agente...")
    
    # Forçando a codificação em UTF-8 sem caracteres de escape quebrados
    data_json = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    
    resposta = requests.post(url, data=data_json, headers=headers)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        produtos = dados.get('produto_servico_cadastro', [])
        
        if produtos:
            print(f"🎉 CONEXÃO AUTOMÁTICA ESTABELECIDA! Encontramos {len(produtos)} produtos:")
            print("-" * 60)
            for p in produtos:
                print(f"Código: {p.get('codigo_produto')} | Nome: {p.get('descricao')} | Peso: {p.get('peso_liquido')}kg")
        else:
            print("✅ Conectado à API, mas a resposta retornou vazia.")
            print(dados)
    else:
        print(f"❌ Resposta de erro do servidor Omie: {resposta.status_code}")
        print(resposta.text)

if __name__ == "__main__":
    listar_produtos_omie_autenticado()
