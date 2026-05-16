import requests
import os

def gerar_e_listar():
    # 1. Pega um token novinho em folha usando o CODE_TRAY fixo
    url_auth = "https://391250.commercesuite.com.br/web_api/auth"
    payload_auth = {
        "consumer_key": os.getenv('CONSUMER_KEY').strip(),
        "consumer_secret": os.getenv('CONSUMER_SECRET').strip(),
        "code": os.getenv('CODE_TRAY').strip()
    }
    
    print("🔑 Passo 1: Solicitando um novo Access Token atualizado para a Tray...")
    resposta_auth = requests.post(url_auth, data=payload_auth)
    
    # Se der 401 aqui, significa que a Tray exige que reajuste o app ou use refresh token. 
    # Mas se der 200/201, ele segue direto para os produtos.
    if resposta_auth.status_code in [200, 201]:
        dados_auth = resposta_auth.json()
        token_atualizado = dados_auth.get('access_token')
        print("✅ Token gerado com sucesso!")
        
        # 2. Usa o token gerado AGORA para listar os produtos no mesmo segundo
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
