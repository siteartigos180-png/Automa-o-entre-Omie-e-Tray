import requests
import os

def gerar_e_listar():
    # URL de autorização oficial usando o subdomínio da sua loja real
    url_auth = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/auth"
    
    payload_auth = {
        "consumer_key": os.getenv('CONSUMER_KEY').strip(),
        "consumer_secret": os.getenv('CONSUMER_SECRET').strip(),
        "code": os.getenv('CODE_TRAY').strip()
    }
    
    print("🔑 Passo 1: Solicitando um novo Access Token para a Loja Oficial da Tray...")
    resposta_auth = requests.post(url_auth, data=payload_auth)
    
    if resposta_auth.status_code in [200, 201]:
        dados_auth = resposta_auth.json()
        token_atualizado = dados_auth.get('access_token')
        print("✅ Token da loja oficial gerado com sucesso!")
        
        # URL de consulta de produtos oficial
        url_produtos = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
        print("📦 Passo 2: Consultando a lista de produtos reais da fábrica...")
        resposta_prod = requests.get(url_produtos, params={'access_token': token_atualizado})
        
        if resposta_prod.status_code == 200:
            dados_prod = resposta_prod.json()
            produtos = dados_prod.get('Products', [])
            print(f"🎉 SUCESSO! Encontramos {len(produtos)} produtos cadastrados na Loja Oficial:")
            print("-" * 60)
            for p in produtos:
                prod = p.get('Product')
                print(f"ID: {prod.get('id')} | Nome: {prod.get('name')} | Estoque: {prod.get('stock')}")
        else:
            print(f"❌ Erro ao listar produtos oficiais: {resposta_prod.status_code}")
            print(resposta_prod.text)
    else:
        print(f"❌ Erro na autorização oficial (Passo 1): {resposta_auth.status_code}")
        print(resposta_auth.text)

if __name__ == "__main__":
    gerar_e_listar()
