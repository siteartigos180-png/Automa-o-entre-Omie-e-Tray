import requests
import os
import json

def listar_produtos_omie():
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    
    # Pegando as chaves fixas do seu cofre do GitHub
    app_key = os.getenv('APP_KEY_OMIE', '').strip()
    app_secret = os.getenv('APP_SECRET_OMIE', '').strip()
    
    # Estrutura padrão que a API da Omie exige para listar produtos
    payload = {
        "call": "ListarProdutos",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 50, # Vamos puxar os primeiros 50 para testar
                "apenas_importado_api": "N",
                "filtrar_apenas_omiepdv": "N"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🏢 Consultando a lista de produtos diretamente na API da Omie...")
    resposta = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        produtos_cadastro = dados.get('produto_servico_cadastro', [])
        
        if produtos_cadastro:
            print(f"🎉 SUCESSO! Conectamos com a Omie. Encontramos {len(produtos_cadastro)} produtos na primeira página:")
            print("-" * 60)
            for p in produtos_cadastro:
                # Na Omie, o código de integração e o código de barras ou descrição ditam o produto
                print(f"Código: {p.get('codigo_produto')} | Nome: {p.get('descricao')} | Peso Líq: {p.get('peso_liquido')}kg")
        else:
            print("✅ Conexão com a Omie deu certo, mas nenhum produto foi retornado nessa página.")
            print(dados)
            
    else:
        print(f"❌ Erro ao conectar com a Omie. Status: {resposta.status_code}")
        print(resposta.text)

if __name__ == "__main__":
    listar_produtos_omie()
