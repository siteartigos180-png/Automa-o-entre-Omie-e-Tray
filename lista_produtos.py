import requests
import os
import time

def auditoria_catalogo_completo_tray():
    url_base = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
    
    consumer_key = os.getenv('CONSUMER_KEY', '').strip()
    consumer_secret = os.getenv('CONSUMER_SECRET', '').strip()
    
    pagina = 1
    total_produtos = 0
    
    print("🚀 INICIANDO SUPER AUDITORIA: LOGÍSTICA + ESTOQUE + PREÇO (OMIE <-> TRAY)")
    print("-" * 135)
    print(f"{'ID':<6} | {'SKU (Ref)':<15} | {'EAN (Barras)':<15} | {'Peso':<10} | {'Estoque':<8} | {'Preço':<10} | {'Nome do Produto'}")
    print("-" * 135)
    
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
            
            if not produtos_pagina:
                break
                
            for p in produtos_pagina:
                prod = p.get('Product', p)
                
                # Dados Logísticos
                sku = prod.get('reference')
                sku_exibir = sku if sku and str(sku).strip() != "" else "Sem SKU"
                
                ean = prod.get('ean')
                ean_exibir = ean if ean and str(ean).strip() != "" else "Sem EAN"
                
                peso = prod.get('weight')
                peso_exibir = f"{peso}g" if peso and str(peso) != "0" else "0g"
                
                # Novos Dados Comerciais e de Estoque
                estoque = prod.get('stock', 0)
                preco = prod.get('price', 0.0)
                preco_exibir = f"R$ {float(preco):.2f}"
                
                nome_reduzido = prod.get('name', '')[:40]
                
                print(f"{prod.get('id'):<6} | {sku_exibir:<15} | {ean_exibir:<15} | {peso_exibir:<10} | {estoque:<8} | {preco_exibir:<10} | {nome_reduzido}")
                total_produtos += 1
                
            pagina += 1
            time.sleep(0.2)
        else:
            print(f"\n❌ Erro ao acessar a página {pagina}. Status: {resposta.status_code}")
            break
            
    print("-" * 135)
    print(f"🎉 AUDITORIA CONCLUÍDA! {total_produtos} produtos verificados no ecossistema.")

if __name__ == "__main__":
    auditoria_catalogo_completo_tray()
