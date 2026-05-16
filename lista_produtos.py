import requests
import os

def listar_produtos_oficiais():
    # URL oficial de consulta de produtos da sua fábrica
    url_produtos = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
    
    # Pegando as chaves direto do cofre do GitHub
    consumer_key = os.getenv('CONSUMER_KEY').strip()
    consumer_secret = os.getenv('CONSUMER_SECRET').strip()
    
    # Parâmetros de autenticação direta aceitos pela Tray para apps integrados
    params = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret
    }
    
    print("📦 Consultando a lista de produtos diretamente na Loja Oficial da Tray...")
    resposta = requests.get(url_produtos, params=params)
    
    if resposta.status_code == 200:
        dados_prod = resposta.json()
        # A API pode retornar na raiz ou dentro de 'Products'
        produtos = dados_prod.get('Products', [])
        
        if produtos:
            print(f"🎉 SUCESSO! Conexão estabelecida. Encontramos {len(produtos)} produtos:")
            print("-" * 60)
            for p in produtos:
                prod = p.get('Product', p)
                print(f"ID: {prod.get('id')} | Nome: {prod.get('name')} | Estoque: {prod.get('stock')}")
        else:
            print("✅ Conexão bem-sucedida, mas nenhum produto foi retornado no catálogo ainda.")
            print(f"Resposta completa da Tray: {dados_prod}")
            
    elif resposta.status_code == 401:
        print("❌ Erro 401: Não autorizado. Vamos tentar o método alternativo por Headers...")
        headers = {
            "Consumer-Key": consumer_key,
            "Consumer-Secret": consumer_secret
        }
        resposta_headers = requests.get(url_produtos, headers=headers)
        if resposta_headers.status_code == 200:
            print("🎉 SUCESSO via Headers!")
            print(resposta_headers.json())
        else:
            print(f"❌ Falha em ambos os métodos de autenticação direta. Status: {resposta_headers.status_code}")
            print(resposta_headers.text)
            
    else:
        print(f"❌ Erro na requisição: {resposta.status_code}")
        print(resposta.text)

if __name__ == "__main__":
    listar_produtos_oficiais()
