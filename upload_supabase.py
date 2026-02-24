import os
import pandas as pd
from supabase import create_client
from tqdm import tqdm
import numpy as np

# 1. CREDENCIAIS (Pegue no seu NOVO projeto: Project Settings > API)
URL = os.environ.get("SUPABASE_URL") or "https://hqcqbrfnppoontberdul.supabase.co"
KEY = os.environ.get("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhxY3FicmZucHBvb250YmVyZHVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDgzMzg3NywiZXhwIjoyMDg2NDA5ODc3fQ.ICyQE_YZSexKGsH5xlv56zZ8W9YnRWWcg0yCpIiyqIM"

supabase = create_client(URL, KEY)

# 2. CARREGAR A BASE COMPLETA
ARQUIVO = r"AgenciaInfra_Historico.xlsx"
# Usamos a Visão Geral porque ela tem TODAS as categorias e o CONTEÚDO novo
df = pd.read_excel(ARQUIVO, sheet_name="Visão Geral")

# 3. PADRONIZAÇÃO PARA O BANCO (Alinhamento total)
# Transforma a data do Excel para o formato que o SQL entende (YYYY-MM-DD)
df['data_noticia'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

# Remove valores nulos (NaN) que o banco não aceita bem
df = df.replace({np.nan: None})

# Mapeia as colunas do Excel para os nomes exatos que criamos no SQL
df_upload = df.rename(columns={
    'Título': 'titulo',
    'Conteúdo': 'conteudo',
    'Link': 'link',
    'Categoria': 'categoria',
    'Fonte': 'fonte'
})

# Seleciona apenas o que o banco precisa
dados_finais = df_upload[['data_noticia', 'fonte', 'categoria', 'titulo', 'conteudo', 'link']].to_dict(orient='records')

print(f"Iniciando o envio de {len(dados_finais)} noticias para a nuvem...")

# 4. UPLOAD EM BLOCOS (Segurança para não travar)
LOTE = 50 
for i in tqdm(range(0, len(dados_finais), LOTE)):
    lote_atual = dados_finais[i:i + LOTE]
    try:
        # O 'upsert' garante que se o link já existir, ele não duplica!
        supabase.table("noticias_infra").upsert(lote_atual, on_conflict='link').execute()
    except Exception as e:
        print(f"\n⚠️ Erro no bloco {i}: {e}")

print("Missao cumprida! Seu monitor agora tem noticias na nuvem.")