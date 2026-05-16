import requests
import os
import time

def listar_todos_produtos_tray():
    # URL oficial da sua loja
    url_base = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
    
    consumer_key = os.getenv('CONSUMER_KEY', '').strip()
    consumer_secret = os.getenv('CONSUMER_SECRET', '').strip()
    
    pagina = 1
    total_produtos = 0
    
    print("🚀 Iniciando Varredura Automatizada do Catálogo Oficial da Fábrica...")
    print("-" * 60)
    
    while True:
        params = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "page": pagina,
            "limit": 50  # Puxa o máximo permitido por página para ir mais rápido
        }
        
        print(f"📦 Lendo página {pagina}...")
        resposta = requests.get(url_base, params=params)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            produtos_pagina = dados.get('Products', [])
            
            if not produtos_pagina:
                break  # Se a página vier vazia, significa que chegamos ao fim do catálogo
                
            for p in produtos_pagina:
                prod = p.get('Product', p)
                print(f"ID: {prod.get('id')} | Nome: {prod.get('name')} | Peso Líq: {prod.get('weight')}g | Estoque: {prod.get('stock')}")
                total_produtos += 1
            
            pagina += 1
            time.sleep(0.5) # Pausa curta de segurança para respeitar o limite da API
        else:
            print(f"❌ Erro ao ler a página {pagina}. Status: {resposta.status_code}")
            print(resposta.text)
            break
            
    print("-" * 60)
    print(f"🎉 FIM DA VARREDURA! Automação concluída com sucesso.")
    print(f"📋 Total de produtos sincronizados e listados na tela: {total_produtos}")

if __name__ == "__main__":
    listar_todos_produtos_tray()
