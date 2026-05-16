import requests
import os
import time

def listar_catalogo_completo_com_detalhes():
    url_base = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
    
    consumer_key = os.getenv('CONSUMER_KEY', '').strip()
    consumer_secret = os.getenv('CONSUMER_SECRET', '').strip()
    
    pagina = 1
    total_produtos = 0
    
    print("🚀 INICIANDO AUDITORIA INTEGRADA: SKU, EAN, PESO BRUTO E LÍQUIDO...")
    print("-" * 110)
    # Cabeçalho formatado para leitura organizada das colunas
    print(f"{'ID':<6} | {'SKU (Ref)':<15} | {'EAN (Barras)':<15} | {'Peso Bruto':<10} | {'Peso Líq':<10} | {'Nome do Produto'}")
    print("-" * 110)
    
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
                
                # Coletando os novos campos solicitados
                sku = prod.get('reference') or prod.get('partner_id') or "Sem SKU"
                ean = prod.get('ean') or "Sem EAN"
                
                # Coletando as variações de peso
                peso_bruto = prod.get('weight')
                peso_liquido = prod.get('net_weight')
                
                p_bruto = f"{peso_bruto}g" if peso_bruto else "Sem Peso"
                p_liq = f"{peso_liquido}g" if peso_liquido else "Sem Peso"
                nome_reduzido = prod.get('name', '')[:40]
                
                # Exibe a linha alinhada como uma tabela oficial de conferência
                print(f"{prod.get('id'):<6} | {sku:<15} | {ean:<15} | {p_bruto:<10} | {p_liq:<10} | {nome_reduzido}")
                total_produtos += 1
                
            pagina += 1
            time.sleep(0.2)
        else:
            print(f"\n❌ Erro ao ler a página {pagina}. Status: {resposta.status_code}")
            break
            
    print("-" * 110)
    print(f"🎉 FINALIZADO! {total_produtos} produtos auditados com SKU, EAN e Pesos na tela.")

if __name__ == "__main__":
    listar_catalogo_completo_com_detalhes()
