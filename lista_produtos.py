import requests
import os

def gerar_e_listar():
    url_auth = "https://391250.commercesuite.com.br/web_api/auth"
    
    # 1. Pega o código da tela da Tray que está no seu cofre
    payload_auth = {
        "consumer_key": os.getenv('CONSUMER_KEY').strip(),
        "consumer_secret": os.getenv('CONSUMER_SECRET').strip(),
        "code": os.getenv('CODE_TRAY').strip()
    }
    
    print("🔑 Passo 1: Solicitando um novo Access Token atualizado...")
    resposta_auth = requests.post(url_auth, data=payload_auth)
    
    if resposta_auth.status_code == 201 or resposta_auth.status_code == 200:
        dados_auth = resposta_auth.json()
        token_atualizado = dados_auth.get('access_token')
        print("✅ Token gerado com sucesso!")
        
        # 2. Usa o token que acabou de ser criado para listar os produtos na hora
        url_produtos = "https://391250.commercesuite.com.br/web_api/products"
        print("📦 Passo 2: Consultando a lista de produtos...")
        resposta_prod = requests.get(url_produtos, params={'access_token': token_atualizado})
        
        if resposta_prod.status_code == 200:
            dados_prod = resposta_prod.json()
            produtos = dados_prod.get('Products', [])
            print(f"🎉 SUCESSO! Encontramos {len(produtos)} produtos cadastrados:")
            print("-" * 50)
            for p in produtos:
                prod = p.get('Product')
                print(f"ID: {prod.get('id')} | Nome: {prod.get('name')} | Estoque: {prod.get('stock')}")
        else:
            print(f"❌ Erro ao listar produtos: {resposta_prod.status_code}")
            print(resposta_prod.text)
            
    else:
        print(f"❌ Erro na autorização (Passo 1): {resposta_auth.status_code}")
        print(resposta_auth.text)

if __name__ == "__main__":
    gerar_e_listar()
