import streamlit as st
import pdfplumber
import re
import unicodedata
from datetime import datetime
import pandas as pd
import io

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------
st.set_page_config(
    page_title="Burocrata de Bolso - Detector de Armadilhas",
    page_icon="⚖️",
    layout="wide"
)

# --------------------------------------------------
# ESTILOS
# --------------------------------------------------
st.markdown("""
<style>
    .header-title {
        font-family: 'Georgia', serif;
        font-weight: 600;
        color: #1a365d;
        border-bottom: 2px solid #c9a96e;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    
    .problem-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .critico { border-left-color: #c53030; }
    .medio { border-left-color: #d69e2e; }
    .leve { border-left-color: #38a169; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SISTEMA DE DETECÇÃO SIMPLES MAS EFETIVO
# --------------------------------------------------

class DetectorArmadilhas:
    """Sistema simples de detecção baseado em palavras-chave"""
    
    def __init__(self):
        self.problemas_detectados = []
    
    def normalizar_texto(self, texto):
        """Remove acentos e padroniza texto"""
        if not texto:
            return ""
        
        # Remove acentos
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])
        
        # Converte para minúsculas
        texto = texto.lower()
        
        # Substitui caracteres problemáticos
        texto = texto.replace('ç', 'c').replace('ã', 'a').replace('õ', 'o')
        texto = texto.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        texto = texto.replace('ó', 'o').replace('ú', 'u')
        
        return texto
    
    def extrair_texto_pdf(self, arquivo_pdf):
        """Extrai texto do PDF"""
        try:
            with pdfplumber.open(arquivo_pdf) as pdf:
                texto_completo = ""
                for pagina in pdf.pages:
                    texto = pagina.extract_text() or ""
                    texto_completo += texto + "\n"
                return texto_completo
        except Exception as e:
            st.error(f"Erro ao ler PDF: {e}")
            return ""
    
    def buscar_armadilhas(self, texto):
        """Busca todas as armadilhas conhecidas"""
        texto_normalizado = self.normalizar_texto(texto)
        
        # DEBUG: Mostrar texto normalizado
        with st.expander("🔍 Ver texto processado (para debug)"):
            st.text_area("Texto normalizado:", texto_normalizado[:1500], height=300)
        
        # Lista de armadilhas a serem detectadas
        armadilhas = [
            {
                "nome": "Reajuste Ilegal",
                "id": "reajuste",
                "gravidade": "critico",
                "exp": "Reajuste deve ser ANUAL (12 meses). Trimestral/mensal é ilegal.",
                "lei": "Lei 10.192/01",
                "palavras_chave": [
                    "reajuste trimestral",
                    "reajuste mensal",
                    "reajuste a cada 3 meses",
                    "reajuste a cada 6 meses",
                    "reajuste semestral",
                    "reajuste bimestral",
                    "reajuste bianual",
                    "trimestralmente",
                    "mensalmente",
                    "cada trimestre"
                ]
            },
            {
                "nome": "Garantia Dupla Ilegal",
                "id": "garantia_dupla",
                "gravidade": "critico",
                "exp": "Não pode exigir fiador E caução simultaneamente.",
                "lei": "Art. 37, Lei 8.245/91",
                "palavras_chave": [
                    "fiador e caucao",
                    "caucao e fiador",
                    "fiador deposito",
                    "fiador mais caucao",
                    "fiador alem de caucao",
                    "fiador junto com caucao",
                    "fiador, caucao",
                    "fiador; caucao",
                    "fiador caucao",
                    "caucao fiador"
                ]
            },
            {
                "nome": "Renúncia a Benfeitorias",
                "id": "benfeitorias",
                "gravidade": "critico",
                "exp": "Inquilino tem direito a indenização por benfeitorias necessárias.",
                "lei": "Art. 35, Lei 8.245/91",
                "palavras_chave": [
                    "renuncia benfeitoria",
                    "nao indeniza benfeitoria",
                    "sem direito benfeitoria",
                    "nao tem direito benfeitoria",
                    "renuncia reforma",
                    "nao indeniza reforma",
                    "sem direito reforma",
                    "renuncia obra",
                    "nao recebera benfeitoria",
                    "abre mao benfeitoria"
                ]
            },
            {
                "nome": "Violação de Privacidade",
                "id": "privacidade",
                "gravidade": "medio",
                "exp": "Locador não pode entrar sem aviso prévio e hora combinada.",
                "lei": "Art. 23, IX, Lei 8.245/91",
                "palavras_chave": [
                    "qualquer visita",
                    "sem aviso visita",
                    "a qualquer visita",
                    "livre visita",
                    "qualquer vistoria",
                    "sem aviso vistoria",
                    "qualquer entrar",
                    "sem aviso entrar",
                    "visita sem aviso",
                    "vistoria sem aviso"
                ]
            },
            {
                "nome": "Multa Desproporcional",
                "id": "multa",
                "gravidade": "critico",
                "exp": "Multa deve ser proporcional ao tempo restante. 12 meses é abusivo.",
                "lei": "Art. 4º, Lei 8.245/91",
                "palavras_chave": [
                    "multa 12 meses",
                    "multa doze meses",
                    "12 meses multa",
                    "doze meses multa",
                    "multa integral",
                    "multa total",
                    "multa completa",
                    "pagar 12 meses multa",
                    "multa correspondente 12 meses"
                ]
            },
            {
                "nome": "Venda Despeja Inquilino",
                "id": "venda",
                "gravidade": "medio",
                "exp": "Venda não rescinde automaticamente. Inquilino tem preferência.",
                "lei": "Art. 27, Lei 8.245/91",
                "palavras_chave": [
                    "venda rescindido",
                    "venda rescisao",
                    "venda terminar",
                    "venda desocupar",
                    "alienacao rescindir",
                    "venda automaticamente",
                    "venda automatico"
                ]
            },
            {
                "nome": "Proibição de Animais",
                "id": "animais",
                "gravidade": "leve",
                "exp": "Proibição total pode ser abusiva. Apenas por justa causa.",
                "lei": "Art. 51, CDC",
                "palavras_chave": [
                    "proibido animais",
                    "vedado animais",
                    "nao permitido animais",
                    "proibicao animais",
                    "nao animais",
                    "proibido pet",
                    "vedado pet",
                    "proibido animal"
                ]
            }
        ]
        
        problemas_encontrados = []
        
        for armadilha in armadilhas:
            encontrado = False
            contexto = ""
            
            for palavra_chave in armadilha["palavras_chave"]:
                if palavra_chave in texto_normalizado:
                    encontrado = True
                    
                    # Extrair contexto
                    idx = texto_normalizado.find(palavra_chave)
                    inicio = max(0, idx - 100)
                    fim = min(len(texto_normalizado), idx + len(palavra_chave) + 100)
                    contexto = f"...{texto_normalizado[inicio:fim]}..."
                    
                    break
            
            if encontrado:
                problemas_encontrados.append({
                    "nome": armadilha["nome"],
                    "id": armadilha["id"],
                    "gravidade": armadilha["gravidade"],
                    "exp": armadilha["exp"],
                    "lei": armadilha["lei"],
                    "contexto": contexto
                })
                st.success(f"✅ Detectado: {armadilha['nome']}")
        
        return problemas_encontrados

# --------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------

st.markdown('<h1 class="header-title">🔍 Detector de Armadilhas em Contratos</h1>', unsafe_allow_html=True)
st.markdown("**Versão 6.0 - Sistema Aprimorado**")

# Upload
st.subheader("📤 Upload do Contrato")
arquivo = st.file_uploader(
    "Selecione o contrato em PDF",
    type=["pdf"],
    help="Contratos de locação residencial"
)

# Texto de teste
st.subheader("📝 Contrato de Teste (para copiar)")
texto_teste = """CONTRATO DE LOCAÇÃO RESIDENCIAL

CLÁUSULA 1 - DO OBJETO
A LOCADORA dá em locação ao LOCATÁRIO o imóvel residencial.

CLÁUSULA 2 - DO PRAZO
Contrato com vigência de 30 meses.

CLÁUSULA 3 - DO VALOR DO ALUGUEL
O aluguel mensal será de R$ 3.000,00. O reajuste será trimestral.

CLÁUSULA 4 - DAS GARANTIAS
O LOCATÁRIO deverá apresentar fiadores e depósito caução.

CLÁUSULA 5 - DAS BENFEITORIAS
O LOCATÁRIO renuncia a qualquer indenização por benfeitorias.

CLÁUSULA 6 - DAS VISITAS
A LOCADORA poderá visitar o imóvel a qualquer tempo, sem aviso.

CLÁUSULA 7 - DA MULTA
Multa de 12 meses de aluguel em caso de rescisão.

CLÁUSULA 8 - DOS ANIMAIS
Proibida a permanência de animais.

CLÁUSULA 9 - DA VENDA
Em caso de venda, contrato rescindido automaticamente.

CLÁUSULA 10 - DO FORO
Foro da Comarca de São Paulo."""
st.code(texto_teste, language="text")

st.info("""
**🎯 Armadilhas que DEVEM ser detectadas:**
1. 🚨 **Reajuste trimestral** (Cláusula 3)
2. 🚨 **Fiador E caução** (Cláusula 4) 
3. 🚨 **Renúncia a benfeitorias** (Cláusula 5)
4. ⚠️ **Visitas sem aviso** (Cláusula 6)
5. 🚨 **Multa de 12 meses** (Cláusula 7)
""")

if arquivo:
    if st.button("🔍 ANALISAR CONTRATO", type="primary", use_container_width=True):
        with st.spinner("Analisando..."):
            # Inicializar detector
            detector = DetectorArmadilhas()
            
            # Extrair texto
            texto = detector.extrair_texto_pdf(arquivo)
            
            if texto:
                # Buscar armadilhas
                problemas = detector.buscar_armadilhas(texto)
                
                # Mostrar resultados
                st.subheader("📊 Resultados da Análise")
                
                if problemas:
                    # Contadores
                    criticos = sum(1 for p in problemas if p["gravidade"] == "critico")
                    medios = sum(1 for p in problemas if p["gravidade"] == "medio")
                    leves = sum(1 for p in problemas if p["gravidade"] == "leve")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🚨 Críticos", criticos)
                    with col2:
                        st.metric("⚠️ Médios", medios)
                    with col3:
                        st.metric("ℹ️ Leves", leves)
                    
                    # Lista de problemas detectados
                    st.subheader("🔎 Problemas Encontrados")
                    
                    for problema in problemas:
                        classe = problema["gravidade"]
                        
                        st.markdown(f"""
                        <div class="problem-card {classe}">
                            <h4>{'🚨' if classe == 'critico' else '⚠️' if classe == 'medio' else 'ℹ️'} 
                            {problema['nome']}</h4>
                            <p><strong>Descrição:</strong> {problema['exp']}</p>
                            <p><strong>Base Legal:</strong> {problema['lei']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if problema.get("contexto"):
                            with st.expander("📄 Ver trecho do contrato"):
                                st.text(problema["contexto"])
                    
                    # Resumo
                    st.success(f"✅ **Total de problemas detectados: {len(problemas)}**")
                    
                    # Verificar se detectou todos os esperados
                    problemas_ids = [p["id"] for p in problemas]
                    esperados = ["reajuste", "garantia_dupla", "benfeitorias", "privacidade", "multa"]
                    
                    faltando = [id for id in esperados if id not in problemas_ids]
                    if faltando:
                        st.warning(f"⚠️ **Não detectado:** {', '.join(faltando)}")
                    
                else:
                    st.success("✅ Nenhuma armadilha detectada!")
            else:
                st.error("❌ Não foi possível ler o texto do PDF")

# Sidebar com informações
with st.sidebar:
    st.markdown("### 📋 Armadilhas Detectáveis")
    
    st.markdown("""
    **🚨 Críticas (ilegais):**
    1. Reajuste não-anual
    2. Garantia dupla
    3. Renúncia a benfeitorias
    4. Multa de 12 meses
    
    **⚠️ Problemas médios:**
    1. Violação de privacidade
    2. Venda despeja inquilino
    
    **ℹ️ Atenção:**
    1. Proibição total de animais
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Como testar")
    st.markdown("""
    1. Copie o texto do contrato de teste
    2. Cole no Word/Bloco de Notas
    3. Salve como PDF
    4. Faça upload aqui
    5. Clique em ANALISAR
    """)

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 12px;">
    Burocrata de Bolso v6.0 | Sistema de Detecção de Armadilhas © 2024
</div>
""", unsafe_allow_html=True)
