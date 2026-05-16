import requests
import os
import time

def listar_catalogo_limpo_tray():
    url_base = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
    
    # Buscando as credenciais salvas no seu GitHub
    consumer_key = os.getenv('CONSUMER_KEY', '').strip()
    consumer_secret = os.getenv('CONSUMER_SECRET', '').strip()
    
    pagina = 1
    total_produtos = 0
    
    print("🚀 INICIANDO LISTAGEM AUTOMATIZADA DO CATÁLOGO DE PRODUTOS...")
    print("-" * 80)
    print(f"{'ID':<6} | {'ESTOQUE':<8} | {'NOME DO PRODUTO'}")
    print("-" * 80)
    
    while True:
        params = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "page": pagina,
            "limit": 50
        }
        
        resposta = requests.get(url_base, params=params)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            produtos_pagina = dados.get('Products', [])
            
            # Se a página não trouxer mais produtos, o robô encerra a busca
            if not produtos_pagina:
                break
                
            for p in produtos_pagina:
                prod = p.get('Product', p)
                
                # Puxando apenas os dados preenchidos de forma limpa
                estoque = prod.get('stock') if prod.get('stock') is not None else 0
                nome_reduzido = prod.get('name', '')[:55]
                
                print(f"{prod.get('id'):<6} | {estoque:<8} | {nome_reduzido}")
                total_produtos += 1
                
            pagina += 1
            time.sleep(0.2)  # Pausa de segurança padrão
        else:
            print(f"\n❌ Erro ao acessar a página {pagina}. Status: {resposta.status_code}")
            break
            
    print("-" * 80)
    print(f"🎉 VARREDURA CONCLUÍDA! Total de produtos ativos listados: {total_produtos}")

if __name__ == "__main__":
    listar_catalogo_limpo_tray()
