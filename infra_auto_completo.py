import pandas as pd
import time
import os
import re
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
ARQUIVO_EXCEL = "AgenciaInfra_Historico.xlsx"

CATEGORIAS_SITE = {
    "Transporte": "https://agenciainfra.com/blog/category/infratransporte/",
    "Energia": "https://agenciainfra.com/blog/category/infraenergia/",
    "Mineração": "https://agenciainfra.com/blog/category/mineracao/",
    "Oleo_Gas": "https://agenciainfra.com/blog/category/oleo-gas/",
    "Cidades": "https://agenciainfra.com/blog/category/infra-cidades/", 
    "Na Transição": "https://agenciainfra.com/blog/category/infra-transicao/",
    "Saneamento": "https://agenciainfra.com/blog/category/infrasaneamento/", 
    "Giro": "https://agenciainfra.com/blog/category/giro-infra/",
    "Eventos": "https://agenciainfra.com/blog/category/infraliveventos/"
}

def configurar_driver():
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # NOVIDADE: User-Agent para evitar bloqueios do site
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extrair_data_limpa(texto):
    match = re.search(r'(\d{2}/\d{2}/\d{4})', str(texto))
    return match.group(1) if match else "S/D"

# ==============================================================================
# PROCESSO UNIFICADO
# ==============================================================================
driver = configurar_driver()
print("🚀 Iniciando Motor de Captura...")

try:
    links_existentes = []
    if os.path.exists(ARQUIVO_EXCEL):
        df_base = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Visão Geral")
        links_existentes = df_base['Link'].astype(str).tolist()
        print(f"📦 Base carregada: {len(links_existentes)} links já conhecidos.")
    else:
        df_base = pd.DataFrame(columns=["Data", "Título", "Link", "Categoria", "Fonte", "Conteúdo"])

    novos_dados = []

    for categoria, url_cat in CATEGORIAS_SITE.items():
        print(f"🔍 Varrendo: {categoria}...")
        try:
            driver.get(url_cat)
            time.sleep(5) # Aumentamos um pouco o tempo de espera
            
            # Seletores mais abrangentes para garantir a captura
            elementos = driver.find_elements(By.CSS_SELECTOR, "h2 a, h3 a, .elementor-post__title a, article a")
            links_na_pagina = list(set([el.get_attribute("href") for el in elementos if el.get_attribute("href")]))
            
            for link in links_na_pagina:
                # Filtro de segurança para pegar apenas notícias reais
                if link not in links_existentes and "/blog/" in link and "/category/" not in link:
                    print(f"   🆕 Nova notícia encontrada: {link}")
                    driver.get(link)
                    time.sleep(2)
                    
                    try:
                        titulo = driver.find_element(By.TAG_NAME, "h1").text.strip()
                        # Tenta pegar a data de várias formas possíveis
                        try:
                            data_bruta = driver.find_element(By.CLASS_NAME, "datas-noticia-inline").text
                        except:
                            data_bruta = driver.find_element(By.CSS_SELECTOR, ".elementor-post-info__item--type-date").text
                    except: 
                        titulo, data_bruta = "Título não localizado", ""

                    corpo = driver.find_elements(By.CSS_SELECTOR, ".elementor-widget-theme-post-content p, .entry-content p")
                    texto = "\n".join([p.text.strip() for p in corpo if p.text.strip()])
                    
                    novos_dados.append({
                        "Data": extrair_data_limpa(data_bruta),
                        "Título": titulo,
                        "Link": link,
                        "Categoria": categoria,
                        "Fonte": "Agência iNFRA",
                        "Conteúdo": texto if texto else "Texto não extraído"
                    })
                    links_existentes.append(link)
        except Exception as e:
            print(f"⚠️ Erro ao varrer {categoria}: {e}")
            continue

    if novos_dados:
        df_novos = pd.DataFrame(novos_dados)
        df_final = pd.concat([df_novos, df_base]).drop_duplicates(subset=['Link'])
        
        with pd.ExcelWriter(ARQUIVO_EXCEL, engine='openpyxl') as writer:
            df_final.to_excel(writer, sheet_name="Visão Geral", index=False)
            for cat in df_final['Categoria'].unique():
                df_cat = df_final[df_final['Categoria'] == cat].drop(columns=['Categoria'])
                df_cat.to_excel(writer, sheet_name=str(cat)[:30], index=False)
        
        print(f"✅ SUCESSO! {len(df_novos)} notícias foram salvas no Excel.")
    else:
        print("🙌 O site foi varrido, mas não foram encontradas notícias novas hoje.")

except Exception as e:
    print(f"❌ ERRO CRÍTICO NO PROCESSO: {e}")

finally:
    driver.quit()