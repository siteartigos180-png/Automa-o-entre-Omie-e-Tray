import requests
import os
import json

def listar_produtos_omie():
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    
    key_do_github = os.getenv('APP_KEY_OMIE', '').strip()
    secret_do_github = os.getenv('APP_SECRET_OMIE', '').strip()
    
    # Payload ajustado para usar filtros padrão de aplicativos integrados
    payload = {
        "call": "ListarProdutos",
        "app_key": key_do_github,
        "app_secret": secret_do_github,
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 20,
                "apenas_importado_api": "N"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🏢 Testando comunicação com a API da Omie usando parâmetros de compatibilidade...")
    resposta = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        produtos_cadastro = dados.get('produto_servico_cadastro', [])
        
        if produtos_cadastro:
            print(f"🎉 SUCESSO EXTREMO! Encontramos {len(produtos_cadastro)} produtos na Omie:")
            print("-" * 60)
            for p in produtos_cadastro:
                print(f"Código: {p.get('codigo_produto')} | Nome: {p.get('descricao')} | Peso Líq: {p.get('peso_liquido')}kg")
        else:
            print("✅ Conexão bem-sucedida, mas a resposta não trouxe itens.")
            print(dados)
    else:
        print(f"❌ Status da Omie: {resposta.status_code}")
        print("Resposta do servidor:")
        print(resposta.text)

if __name__ == "__main__":
    listar_produtos_omie()
