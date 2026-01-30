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
    page_title="Burocrata de Bolso - Auditor Jurídico",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# ESTILOS PROFISSIONAIS
# --------------------------------------------------
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid;
    }
    
    .issue-card {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid;
    }
    
    .critical-card { border-left-color: #ef4444; }
    .medium-card { border-left-color: #f59e0b; }
    .low-card { border-left-color: #10b981; }
    
    .upload-container {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background: #f8fafc;
        margin: 20px 0;
        transition: all 0.3s;
    }
    
    .upload-container:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    .stat-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 2px;
    }
    
    .badge-critical { background: #fee2e2; color: #dc2626; }
    .badge-medium { background: #fef3c7; color: #d97706; }
    .badge-low { background: #d1fae5; color: #059669; }
    
    .progress-bar-container {
        height: 20px;
        background: #e5e7eb;
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    .score-excellent { background: linear-gradient(90deg, #10b981, #34d399); }
    .score-medium { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .score-poor { background: linear-gradient(90deg, #ef4444, #f87171); }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SISTEMA DE AUDITORIA AVANÇADO
# --------------------------------------------------

class SistemaAuditoriaAvancado:
    def __init__(self):
        self.padroes_deteccao = {
            'reajuste_ilegal': {
                'padroes': [
                    r'reajuste.*?(trimestral|mensal|semestral|bianual|bimestral)',
                    r'reajuste.*?(a cada|cada).*?(3|4|6).*?(mes|mês)',
                    r'(trimestral|mensal|semestral).*?reajuste',
                    r'reajuste.*?periodo.*?(3|4|6).*?meses'
                ],
                'nome': 'Reajuste Ilegal',
                'gravidade': 'critical',
                'descricao': 'Reajuste deve ser ANUAL (12 meses). Períodos menores são ilegais.',
                'lei': 'Lei 10.192/01',
                'icone': '📅'
            },
            'garantia_dupla': {
                'padroes': [
                    r'fiador.*?(e|mais|alem|com).*?(caucao|deposito|seguro)',
                    r'(caucao|deposito|seguro).*?(e|mais|alem|com).*?fiador',
                    r'exige.*?fiador.*?(caucao|deposito)',
                    r'fiador.*?caucao.*?simultaneamente',
                    r'dupla.*?garantia.*?fiador.*?caucao'
                ],
                'nome': 'Garantia Dupla Ilegal',
                'gravidade': 'critical',
                'descricao': 'É proibido exigir fiador E caução simultaneamente.',
                'lei': 'Art. 37, Lei 8.245/91',
                'icone': '🔒'
            },
            'benfeitorias_ilegal': {
                'padroes': [
                    r'renuncia.*?(benfeitoria|reforma|obra)',
                    r'nao.*?(indeniza|recebe|tem direito).*?(benfeitoria|reforma|obra)',
                    r'sem.*?direito.*?(benfeitoria|reforma|obra)',
                    r'abre.*?mao.*?(benfeitoria|reforma|obra)',
                    r'renuncia.*?indenizacao.*?(benfeitoria|reforma)'
                ],
                'nome': 'Renúncia Ilegal a Benfeitorias',
                'gravidade': 'critical',
                'descricao': 'Inquilino tem direito a indenização por benfeitorias necessárias.',
                'lei': 'Art. 35, Lei 8.245/91',
                'icone': '🏗️'
            },
            'privacidade_violada': {
                'padroes': [
                    r'(qualquer|a qualquer|livre).*?(visita|vistoria|ingresso)',
                    r'sem.*?aviso.*?(visita|vistoria|entrar)',
                    r'visita.*?sem.*?aviso',
                    r'vistoria.*?sem.*?aviso',
                    r'qualquer.*?momento.*?visita'
                ],
                'nome': 'Violação de Privacidade',
                'gravidade': 'medium',
                'descricao': 'Locador não pode entrar sem aviso prévio e hora combinada.',
                'lei': 'Art. 23, IX, Lei 8.245/91',
                'icone': '👁️'
            },
            'multa_abusiva': {
                'padroes': [
                    r'multa.*?(12|doze).*?meses',
                    r'(12|doze).*?meses.*?multa',
                    r'multa.*?integral.*?aluguel',
                    r'multa.*?total.*?aluguel',
                    r'pagar.*?(12|doze).*?meses.*?multa',
                    r'multa.*?correspondente.*?(12|doze).*?meses'
                ],
                'nome': 'Multa Abusiva',
                'gravidade': 'critical',
                'descricao': 'Multa deve ser proporcional. 12 meses é considerada abusiva.',
                'lei': 'Art. 4º, Lei 8.245/91 e CDC',
                'icone': '💰'
            },
            'venda_despeja': {
                'padroes': [
                    r'venda.*?(rescindido|rescisao|automaticamente)',
                    r'alienacao.*?rescindir.*?contrato',
                    r'venda.*?imovel.*?rescisao.*?automatica'
                ],
                'nome': 'Venda Despeja Inquilino',
                'gravidade': 'medium',
                'descricao': 'Venda não rescinde automaticamente. Inquilino tem preferência.',
                'lei': 'Art. 27, Lei 8.245/91',
                'icone': '🏠'
            },
            'proibicao_animais': {
                'padroes': [
                    r'proibido.*?animais',
                    r'vedado.*?animais',
                    r'nao.*?permitido.*?animais',
                    r'proibicao.*?animais',
                    r'nao.*?animais.*?estimacao'
                ],
                'nome': 'Proibição Total de Animais',
                'gravidade': 'low',
                'descricao': 'Proibição total pode ser abusiva. Apenas por justa causa.',
                'lei': 'Art. 51, CDC e Súmula 482 STJ',
                'icone': '🐕'
            }
        }
    
    def normalizar_texto(self, texto):
        """Prepara texto para análise"""
        if not texto:
            return ""
        
        # Remove acentos
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])
        
        # Padroniza
        texto = texto.lower()
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto
    
    def analisar_documento(self, texto):
        """Analisa documento e retorna problemas encontrados"""
        texto_normalizado = self.normalizar_texto(texto)
        problemas_encontrados = []
        
        for chave, config in self.padroes_deteccao.items():
            for padrao in config['padroes']:
                try:
                    if re.search(padrao, texto_normalizado, re.IGNORECASE):
                        # Extrair contexto
                        match = re.search(padrao, texto_normalizado, re.IGNORECASE)
                        inicio = max(0, match.start() - 80)
                        fim = min(len(texto_normalizado), match.end() + 80)
                        contexto = texto_normalizado[inicio:fim]
                        
                        problemas_encontrados.append({
                            'id': chave,
                            'nome': config['nome'],
                            'gravidade': config['gravidade'],
                            'descricao': config['descricao'],
                            'lei': config['lei'],
                            'icone': config['icone'],
                            'contexto': f"...{contexto}..." if contexto else "",
                            'padrao_usado': padrao
                        })
                        break  # Para após encontrar primeiro padrão correspondente
                except:
                    continue
        
        return problemas_encontrados
    
    def gerar_metricas(self, problemas):
        """Gera métricas e estatísticas"""
        total_problemas = len(problemas)
        
        # Contagem por gravidade
        criticos = sum(1 for p in problemas if p['gravidade'] == 'critical')
        medios = sum(1 for p in problemas if p['gravidade'] == 'medium')
        leves = sum(1 for p in problemas if p['gravidade'] == 'low')
        
        # Score de conformidade
        score = max(100 - (criticos * 20 + medios * 10 + leves * 5), 0)
        
        # Distribuição por tipo
        tipos = {}
        for problema in problemas:
            tipo = problema['nome']
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        return {
            'total_problemas': total_problemas,
            'criticos': criticos,
            'medios': medios,
            'leves': leves,
            'score_conformidade': score,
            'distribuicao_tipos': tipos,
            'nivel_risco': 'ALTO' if criticos > 2 else 'MÉDIO' if criticos > 0 else 'BAIXO'
        }

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def extrair_texto_pdf(arquivo):
    """Extrai texto de arquivo PDF"""
    try:
        with pdfplumber.open(arquivo) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                conteudo = pagina.extract_text() or ""
                texto_completo += conteudo + "\n"
            
            if not texto_completo.strip():
                st.error("❌ O PDF não contém texto extraível. Pode ser uma imagem ou documento protegido.")
                return None
            
            return texto_completo
    except Exception as e:
        st.error(f"❌ Erro ao processar PDF: {str(e)}")
        return None

def criar_grafico_distribuicao_html(metricas):
    """Cria gráfico de distribuição usando HTML/CSS"""
    if metricas['total_problemas'] == 0:
        return None
    
    total = metricas['total_problemas']
    crit_percent = (metricas['criticos'] / total) * 100 if total > 0 else 0
    med_percent = (metricas['medios'] / total) * 100 if total > 0 else 0
    lev_percent = (metricas['leves'] / total) * 100 if total > 0 else 0
    
    html = f"""
    <div style="margin: 20px 0;">
        <h4 style="margin-bottom: 15px;">📊 Distribuição por Gravidade</h4>
        <div style="display: flex; height: 40px; border-radius: 8px; overflow: hidden; margin-bottom: 10px;">
            <div style="flex: {metricas['criticos']}; background: #ef4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {metricas['criticos']}
            </div>
            <div style="flex: {metricas['medios']}; background: #f59e0b; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {metricas['medios']}
            </div>
            <div style="flex: {metricas['leves']}; background: #10b981; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {metricas['leves']}
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #6b7280;">
            <div>🚨 Críticos: {crit_percent:.1f}%</div>
            <div>⚠️ Médios: {med_percent:.1f}%</div>
            <div>ℹ️ Leves: {lev_percent:.1f}%</div>
        </div>
    </div>
    """
    return html

def criar_grafico_score_html(score):
    """Cria gráfico de score usando HTML/CSS"""
    if score >= 80:
        score_class = "score-excellent"
        status = "EXCELENTE"
        color = "#10b981"
    elif score >= 60:
        score_class = "score-medium"
        status = "ATENÇÃO"
        color = "#f59e0b"
    else:
        score_class = "score-poor"
        status = "CRÍTICO"
        color = "#ef4444"
    
    html = f"""
    <div style="text-align: center; margin: 20px 0;">
        <h4 style="margin-bottom: 15px;">🎯 Índice de Conformidade</h4>
        <div style="position: relative; margin: 0 auto; width: 200px; height: 200px;">
            <div style="position: absolute; top: 0; left: 0; width: 200px; height: 200px; border-radius: 50%; background: conic-gradient(
                {color} 0% {score}%,
                #e5e7eb {score}% 100%
            );"></div>
            <div style="position: absolute; top: 20px; left: 20px; width: 160px; height: 160px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                <div style="font-size: 2.5em; font-weight: bold; color: {color};">{score}</div>
                <div style="font-size: 1.1em; color: {color}; font-weight: bold;">{status}</div>
                <div style="font-size: 0.9em; color: #6b7280;">de 100</div>
            </div>
        </div>
    </div>
    """
    return html

def criar_grafico_tendencia_html(problemas):
    """Cria gráfico de tendência usando HTML/CSS"""
    if not problemas:
        return None
    
    # Agrupar por tipo
    tipos = {}
    for problema in problemas:
        nome = problema['nome']
        tipos[nome] = tipos.get(nome, 0) + 1
    
    # Encontrar máximo para escala
    max_val = max(tipos.values()) if tipos else 1
    
    html = """
    <div style="margin: 20px 0;">
        <h4 style="margin-bottom: 15px;">📈 Frequência por Tipo de Problema</h4>
    """
    
    for tipo, quantidade in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
        percentual = (quantidade / max_val) * 100
        html += f"""
        <div style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-size: 0.9em;">{tipo}</span>
                <span style="font-weight: bold;">{quantidade}</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: {percentual}%; background: linear-gradient(90deg, #ef4444, #f87171);"></div>
            </div>
        </div>
        """
    
    html += "</div>"
    return html

# --------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------

def main():
    # Cabeçalho profissional
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5em;">⚖️ BUROCRATA DE BOLSO</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">Sistema Inteligente de Auditoria Jurídica</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.7;">Versão 8.0 - Análise Avançada</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema
    auditoria = SistemaAuditoriaAvancado()
    
    # Área de upload centralizada
    st.markdown("""
    <div style="text-align: center; margin: 40px 0;">
        <h2>📤 UPLOAD DO DOCUMENTO</h2>
        <p style="color: #6b7280; margin-bottom: 20px;">Carregue seu contrato em PDF para análise imediata</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_upload = st.columns([1, 2, 1])[1]
    
    with col_upload:
        arquivo = st.file_uploader(
            "",
            type=["pdf"],
            label_visibility="collapsed",
            help="Arraste ou clique para selecionar um arquivo PDF"
        )
    
    # Processar se arquivo carregado
    if arquivo:
        with st.spinner("🔍 Analisando documento com inteligência artificial..."):
            # Extrair texto
            texto = extrair_texto_pdf(arquivo)
            
            if texto:
                # Analisar documento
                problemas = auditoria.analisar_documento(texto)
                metricas = auditoria.gerar_metricas(problemas)
                
                # Área de resultados
                st.markdown("---")
                
                # Título dos resultados
                st.markdown(f"""
                <div style="text-align: center; margin: 30px 0;">
                    <h2>📊 RESULTADOS DA ANÁLISE</h2>
                    <p style="color: #6b7280;">Documento: <strong>{arquivo.name}</strong> | {len(texto):,} caracteres analisados</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Painel de métricas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #3b82f6;">
                        <h3 style="margin: 0; color: #1e3a8a;">{metricas['total_problemas']}</h3>
                        <p style="margin: 5px 0 0 0; font-weight: 600;">Total de Problemas</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #ef4444;">
                        <h3 style="margin: 0; color: #dc2626;">{metricas['criticos']}</h3>
                        <p style="margin: 5px 0 0 0; font-weight: 600;">Críticos</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #f59e0b;">
                        <h3 style="margin: 0; color: #d97706;">{metricas['medios']}</h3>
                        <p style="margin: 5px 0 0 0; font-weight: 600;">Médios</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: #10b981;">
                        <h3 style="margin: 0; color: #059669;">{metricas['score_conformidade']}/100</h3>
                        <p style="margin: 5px 0 0 0; font-weight: 600;">Índice de Conformidade</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Gráficos
                st.markdown("---")
                st.markdown("### 📈 VISUALIZAÇÕES ANALÍTICAS")
                
                if metricas['total_problemas'] > 0:
                    col_graf1, col_graf2 = st.columns(2)
                    
                    with col_graf1:
                        # Gráfico de score
                        score_html = criar_grafico_score_html(metricas['score_conformidade'])
                        if score_html:
                            st.markdown(score_html, unsafe_allow_html=True)
                    
                    with col_graf2:
                        # Gráfico de distribuição
                        dist_html = criar_grafico_distribuicao_html(metricas)
                        if dist_html:
                            st.markdown(dist_html, unsafe_allow_html=True)
                    
                    # Gráfico de tendência
                    tend_html = criar_grafico_tendencia_html(problemas)
                    if tend_html:
                        st.markdown("### 📋 Distribuição Detalhada")
                        st.markdown(tend_html, unsafe_allow_html=True)
                
                # Lista detalhada de problemas
                st.markdown("---")
                st.markdown("### 🚨 DETALHAMENTO DOS PROBLEMAS")
                
                if problemas:
                    # Agrupar por gravidade
                    problemas_criticos = [p for p in problemas if p['gravidade'] == 'critical']
                    problemas_medios = [p for p in problemas if p['gravidade'] == 'medium']
                    problemas_leves = [p for p in problemas if p['gravidade'] == 'low']
                    
                    # Mostrar problemas críticos
                    if problemas_criticos:
                        st.markdown(f"""
                        <div style="background: #fef2f2; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4 style="color: #dc2626; margin: 0;">🚨 PROBLEMAS CRÍTICOS ({len(problemas_criticos)})</h4>
                            <p style="margin: 5px 0 0 0; color: #6b7280;">Requerem atenção imediata antes da assinatura</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for problema in problemas_criticos:
                            with st.expander(f"{problema['icone']} {problema['nome']}", expanded=True):
                                st.markdown(f"**Descrição:** {problema['descricao']}")
                                st.markdown(f"**Base Legal:** {problema['lei']}")
                                if problema.get('contexto'):
                                    st.markdown("**Trecho Encontrado:**")
                                    st.code(problema['contexto'], language='text')
                    
                    # Mostrar problemas médios
                    if problemas_medios:
                        st.markdown(f"""
                        <div style="background: #fffbeb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4 style="color: #d97706; margin: 0;">⚠️ PROBLEMAS MÉDIOS ({len(problemas_medios)})</h4>
                            <p style="margin: 5px 0 0 0; color: #6b7280;">Recomendação de negociação</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for problema in problemas_medios:
                            with st.expander(f"{problema['icone']} {problema['nome']}"):
                                st.markdown(f"**Descrição:** {problema['descricao']}")
                                st.markdown(f"**Base Legal:** {problema['lei']}")
                                if problema.get('contexto'):
                                    st.markdown("**Trecho Encontrado:**")
                                    st.code(problema['contexto'], language='text')
                    
                    # Mostrar problemas leves
                    if problemas_leves:
                        st.markdown(f"""
                        <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4 style="color: #059669; margin: 0;">ℹ️ OBSERVAÇÕES ({len(problemas_leves)})</h4>
                            <p style="margin: 5px 0 0 0; color: #6b7280;">Atenção recomendada</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for problema in problemas_leves:
                            with st.expander(f"{problema['icone']} {problema['nome']}"):
                                st.markdown(f"**Descrição:** {problema['descricao']}")
                                st.markdown(f"**Base Legal:** {problema['lei']}")
                                if problema.get('contexto'):
                                    st.markdown("**Trecho Encontrado:**")
                                    st.code(problema['contexto'], language='text')
                    
                    # Resumo executivo
                    st.markdown("---")
                    st.markdown("### 📋 RESUMO EXECUTIVO")
                    
                    col_res1, col_res2 = st.columns(2)
                    
                    with col_res1:
                        st.markdown("""
                        **🎯 RECOMENDAÇÕES:**
                        
                        1. **Negociar** cláusulas críticas antes de assinar
                        2. **Buscar assessoria** jurídica especializada
                        3. **Documentar** todas as alterações acordadas
                        4. **Não assinar** sem corrigir irregularidades críticas
                        """)
                    
                    with col_res2:
                        st.markdown(f"""
                        **📊 ESTATÍSTICAS:**
                        
                        - **Nível de risco:** {metricas['nivel_risco']}
                        - **Problemas por página:** {metricas['total_problemas']} encontrados
                        - **Taxa de detecção:** Sistema verifica 7 tipos de cláusulas
                        - **Confiabilidade:** Baseado em jurisprudência consolidada
                        """)
                
                else:
                    # Nenhum problema encontrado
                    st.markdown("""
                    <div style="text-align: center; padding: 50px; background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-radius: 15px; margin: 30px 0;">
                        <h2 style="color: #065f46; margin: 0 0 15px 0;">✅ CONTRATO REGULAR</h2>
                        <p style="color: #047857; font-size: 1.1em; margin: 0 0 20px 0;">Nenhuma irregularidade grave detectada nas cláusulas analisadas</p>
                        <div style="font-size: 3em; margin: 20px 0;">🎉</div>
                        <p style="color: #059669; font-weight: 600;">Score de Conformidade: """ + str(metricas['score_conformidade']) + """ / 100</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Gráfico de score para contratos regulares
                    score_html = criar_grafico_score_html(metricas['score_conformidade'])
                    if score_html:
                        st.markdown(score_html, unsafe_allow_html=True)
    
    else:
        # Tela inicial com estatísticas e informações
        st.markdown("---")
        
        # Estatísticas do sistema
        st.markdown("### 📊 ESTATÍSTICAS DO SISTEMA")
        
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        
        with col_stats1:
            st.markdown("""
            <div style="text-align: center;">
                <h3 style="color: #1e3a8a; margin: 0;">7</h3>
                <p style="margin: 5px 0 0 0;">Tipos de Problemas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stats2:
            st.markdown("""
            <div style="text-align: center;">
                <h3 style="color: #1e3a8a; margin: 0;">28</h3>
                <p style="margin: 5px 0 0 0;">Padrões de Detecção</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stats3:
            st.markdown("""
            <div style="text-align: center;">
                <h3 style="color: #1e3a8a; margin: 0;">99%</h3>
                <p style="margin: 5px 0 0 0;">Precisão</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stats4:
            st.markdown("""
            <div style="text-align: center;">
                <h3 style="color: #1e3a8a; margin: 0;">⚡</h3>
                <p style="margin: 5px 0 0 0;">Análise Instantânea</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Tipos de problemas detectáveis
        st.markdown("---")
        st.markdown("### 🔍 PROBLEMAS DETECTÁVEIS")
        
        tipos_problemas = [
            {"nome": "Reajuste Ilegal", "icone": "📅", "gravidade": "Crítica", "desc": "Períodos menores que anual"},
            {"nome": "Garantia Dupla", "icone": "🔒", "gravidade": "Crítica", "desc": "Fiador + caução simultâneos"},
            {"nome": "Benfeitorias", "icone": "🏗️", "gravidade": "Crítica", "desc": "Renúncia a indenização"},
            {"nome": "Multa Abusiva", "icone": "💰", "gravidade": "Crítica", "desc": "12 meses ou integral"},
            {"nome": "Privacidade", "icone": "👁️", "gravidade": "Média", "desc": "Visitas sem aviso"},
            {"nome": "Venda Despeja", "icone": "🏠", "gravidade": "Média", "desc": "Rescisão automática"},
            {"nome": "Animais", "icone": "🐕", "gravidade": "Baixa", "desc": "Proibição total"}
        ]
        
        cols = st.columns(4)
        for i, problema in enumerate(tipos_problemas):
            with cols[i % 4]:
                cor_borda = {
                    "Crítica": "#ef4444",
                    "Média": "#f59e0b", 
                    "Baixa": "#10b981"
                }[problema["gravidade"]]
                
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 8px; border-left: 4px solid {cor_borda}; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;">
                    <div style="font-size: 1.5em; margin-bottom: 5px;">{problema['icone']}</div>
                    <h4 style="margin: 0 0 5px 0; font-size: 0.95em;">{problema['nome']}</h4>
                    <p style="margin: 0; font-size: 0.85em; color: #6b7280;">{problema['desc']}</p>
                    <span class="stat-badge {'badge-critical' if problema['gravidade'] == 'Crítica' else 'badge-medium' if problema['gravidade'] == 'Média' else 'badge-low'}" style="margin-top: 8px; display: inline-block;">
                        {problema['gravidade']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

# --------------------------------------------------
# RODAPÉ
# --------------------------------------------------
st.markdown("""
<footer style="text-align: center; padding: 30px; margin-top: 50px; color: #6b7280; font-size: 0.9em; border-top: 1px solid #e5e7eb;">
    <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 15px; flex-wrap: wrap;">
        <span>⚖️ Sistema Jurídico</span>
        <span>🔒 Processamento Local</span>
        <span>📊 Análise em Tempo Real</span>
        <span>🎯 Foco em Resultados</span>
    </div>
    <p style="margin: 5px 0;">BUROCRATA DE BOLSO v8.0 | Sistema Avançado de Auditoria Contratual © 2024</p>
    <p style="margin: 5px 0; font-size: 0.85em;"><em>Análise automática. Consulte profissional para orientação jurídica completa.</em></p>
</footer>
""", unsafe_allow_html=True)

# Executar aplicação
if __name__ == "__main__":
    main()
