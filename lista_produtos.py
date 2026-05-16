import requests
import os
import time

def listar_todo_o_catalogo_tray():
    url_base = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
    
    # Puxando as credenciais do seu cofre do GitHub
    consumer_key = os.getenv('CONSUMER_KEY', '').strip()
    consumer_secret = os.getenv('CONSUMER_SECRET', '').strip()
    
    pagina = 1
    total_produtos = 0
    
    print("🚀 INICIANDO VARREDURA AUTOMATIZADA DE TODO O CATÁLOGO DA FÁBRICA...")
    print("-" * 70)
    
    while True:
        # Passando a página atual e forçando o limite máximo de 50 por chamada
        params = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "page": pagina,
            "limit": 50
        }
        
        print(f"📦 Solicitando dados da Página {pagina} à API da Tray...")
        resposta = requests.get(url_base, params=params)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            produtos_pagina = dados.get('Products', [])
            
            # Se a página vier vazia, significa que o robô leu todo o catálogo e terminou
            if not produtos_pagina:
                print(f"✨ Sem mais produtos na página {pagina}. Varredura concluída!")
                break
                
            for p in produtos_pagina:
                prod = p.get('Product', p)
                print(f"ID: {prod.get('id')} | Nome: {prod.get('name')} | Peso Líq: {prod.get('weight')}g | Estoque: {prod.get('stock')}")
                total_produtos += 1
                
            pagina += 1
            time.sleep(0.3)  # Pausa de segurança para não travar o servidor da Tray
        else:
            print(f"❌ Erro ao ler a página {pagina}. Status: {resposta.status_code}")
            print(resposta.text)
            break
            
    print("-" * 70)
    print(f"🎉 INTEGRAÇÃO DE LEITURA FINALIZADA COM SUCESSO!")
    print(f"📋 Total de produtos localizados e listados na tela: {total_produtos}")

if __name__ == "__main__":
    listar_todo_o_catalogo_tray()
