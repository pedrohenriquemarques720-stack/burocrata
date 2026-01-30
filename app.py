import streamlit as st
import pdfplumber
import re
import unicodedata
from datetime import datetime
import pandas as pd

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT PROFISSIONAL
# --------------------------------------------------
st.set_page_config(
    page_title="Burocrata de Bolso - Análise Jurídica de Documentos",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# ESTILOS CSS PERSONALIZADOS
# --------------------------------------------------
st.markdown("""
<style>
    /* Estilos gerais */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Cabeçalho profissional */
    .header-title {
        font-family: 'Georgia', serif;
        font-weight: 600;
        color: #1a365d;
        border-bottom: 2px solid #c9a96e;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    
    .header-subtitle {
        font-family: 'Helvetica', sans-serif;
        color: #4a5568;
        font-size: 16px;
        margin-top: -15px;
        margin-bottom: 30px;
    }
    
    /* Cards e containers */
    .analysis-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #2c5282;
        margin-bottom: 15px;
    }
    
    .info-card {
        background-color: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    /* Métricas e indicadores */
    .metric-container {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    .score-excellent {
        color: #276749;
        font-weight: 700;
    }
    
    .score-moderate {
        color: #d69e2e;
        font-weight: 700;
    }
    
    .score-critical {
        color: #c53030;
        font-weight: 700;
    }
    
    /* Botões */
    .stButton button {
        background-color: #2c5282;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-weight: 500;
        transition: background-color 0.3s;
    }
    
    .stButton button:hover {
        background-color: #1a365d;
    }
    
    /* Tabelas e expanders */
    .stExpander {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
    }
    
    .stExpander > div:first-child {
        background-color: #f7fafc;
        padding: 12px 15px;
        font-weight: 500;
        color: #2d3748;
    }
    
    /* Console profissional */
    .console-header {
        background-color: #2d3748;
        color: white;
        padding: 12px 15px;
        border-radius: 6px 6px 0 0;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 14px;
    }
    
    .console-body {
        background-color: #1a202c;
        color: #a0aec0;
        padding: 15px;
        border-radius: 0 0 6px 6px;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        border: 1px solid #2d3748;
    }
    
    /* Sidebar profissional */
    .sidebar-title {
        color: #2c5282;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active {
        background-color: #38a169;
    }
    
    .status-inactive {
        background-color: #cbd5e0;
    }
    
    /* Tags de tipo de problema */
    .tag-critico {
        background-color: #fed7d7;
        color: #9b2c2c;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .tag-medio {
        background-color: #feebc8;
        color: #9c4221;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .tag-leve {
        background-color: #c6f6d5;
        color: #276749;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Ícones específicos para cada tipo de documento */
    .doc-icon-locacao {
        color: #2c5282;
    }
    
    .doc-icon-nfe {
        color: #38a169;
    }
    
    .doc-icon-servico {
        color: #d69e2e;
    }
    
    .doc-icon-compra-venda {
        color: #9b2c2c;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SISTEMA DE DETECÇÃO DE TIPO DE DOCUMENTO
# --------------------------------------------------

class DocumentTypeDetector:
    """Detecta automaticamente o tipo de documento"""
    
    @staticmethod
    def detectar_tipo(texto):
        texto_lower = texto.lower()
        
        indicadores = {
            'contrato_locacao': ['contrato de locação', 'locador', 'locatário', 'aluguel', 'imóvel', 
                                 'termos de locação', 'cláusula', 'vigência', 'fiador', 'caução',
                                 'valor do aluguel', 'reajuste anual'],
            'nota_fiscal': ['nota fiscal', 'nfe', 'nf-e', 'chave de acesso', 'emitente', 'destinatário',
                           'cnpj', 'icms', 'ipi', 'danfe', 'número da nota', 'modelo 55', 'valor total'],
            'contrato_servico': ['contrato de prestação de serviços', 'contratante', 'contratada', 
                                'objeto do contrato', 'escopo dos serviços', 'fornecimento de serviços',
                                'prestador de serviços', 'tomador de serviços', 'serviços contratados',
                                'cláusulas do contrato', 'prazo de execução', 'valor dos serviços'],
            'contrato_compra_venda': ['contrato de compra e venda', 'contrato de compra e venda de imóvel',
                                     'vendedor', 'comprador', 'alienante', 'adquirente', 
                                     'imóvel objeto deste contrato', 'matrícula', 'registro do imóvel',
                                     'preço total', 'sinal', 'entrada', 'financiamento', 'cartório',
                                     'itbi', 'escritura pública', 'registro de imóveis']
        }
        
        contagem = {tipo: 0 for tipo in indicadores.keys()}
        
        for tipo, palavras in indicadores.items():
            for palavra in palavras:
                if palavra in texto_lower:
                    contagem[tipo] += 1
        
        tipo_detectado = max(contagem.items(), key=lambda x: x[1])
        
        if tipo_detectado[1] < 2:
            return 'desconhecido'
        
        return tipo_detectado[0]

# --------------------------------------------------
# LEITORES DE DOCUMENTOS ESPECÍFICOS
# --------------------------------------------------

class NotaFiscalReader:
    """Lê e analisa Notas Fiscais Eletrônicas"""
    
    def __init__(self):
        self.tipo = "nota_fiscal"
        self.padroes = {
            'numero': r'N[º°]\s*[:]?\s*(\d+)',
            'serie': r'S[ÉE]RIE\s*[:]?\s*(\d+)',
            'chave_acesso': r'CHAVE\s+DE\s+ACESSO\s*[:]?\s*([0-9]{44})',
            'cnpj_emitente': r'CNPJ\s*[:]?\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
            'nome_emitente': r'EMITENTE\s*(?:.*?\n)?(?:RAZÃO SOCIAL|NOME)?\s*[:]?\s*(.+)',
            'cnpj_destinatario': r'DESTINATÁRIO.*?CNPJ\s*[:]?\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
            'valor_total': r'VALOR\s+TOTAL\s+(?:R\$|\$)?\s*([\d.,]+)',
            'data_emissao': r'DATA\s+(?:DA\s+)?EMISSÃO\s*[:]?\s*(\d{2}/\d{2}/\d{4})',
            'valor_icms': r'VALOR\s+DO\s+ICMS\s*(?:R\$|\$)?\s*([\d.,]+)',
            'valor_ipi': r'VALOR\s+DO\s+IPI\s*(?:R\$|\$)?\s*([\d.,]+)',
            'cfop': r'CFOP\s*[:]?\s*(\d{4})',
            'natureza_operacao': r'NATUREZA\s+DA\s+OPERAÇÃO\s*[:]?\s*(.+)',
            'protocolo_autorizacao': r'PROTOCOLO\s+DE\s+AUTORIZAÇÃO\s*[:]?\s*(\d+)'
        }
        
        self.padroes_auditoria = [
            {
                "id": "nfe_chave_invalida",
                "regex": r"CHAVE\s+DE\s+ACESSO\s*[:]?\s*([0-9]{43}|[0-9]{45})",
                "nome": "Chave de Acesso Inválida",
                "exp": "A chave de acesso deve conter exatamente 44 dígitos.",
                "lei": "Portaria CAT 142/2018"
            },
            {
                "id": "nfe_data_vencida",
                "regex": r"DATA\s+DE\s+EMISSÃO.*?(\d{2}/\d{2}/\d{4})",
                "nome": "Nota Fiscal Vencida",
                "exp": "Verifique se a data de emissão não ultrapassa 5 anos para fins fiscais.",
                "lei": "Art. 198, RICMS/SP"
            },
            {
                "id": "nfe_cnpj_invalido",
                "regex": r"CNPJ\s*[:]?\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{1}|\d{2}\.\d{3}\.\d{3}/\d{3}-\d{2})",
                "nome": "CNPJ com Formato Inválido",
                "exp": "Formato de CNPJ incorreto. Deve seguir o padrão XX.XXX.XXX/XXXX-XX.",
                "lei": "Instrução Normativa RFB 1.863/2018"
            }
        ]
    
    def extrair_informacoes(self, texto):
        resultados = {}
        for campo, padrao in self.padroes.items():
            match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                resultados[campo] = match.group(1)
            else:
                padrao_flex = padrao.replace(r'\s*[:]?\s*', r'.*?')
                match_flex = re.search(padrao_flex, texto, re.IGNORECASE | re.MULTILINE)
                resultados[campo] = match_flex.group(1) if match_flex else None
        return resultados
    
    def auditoria_nfe(self, texto):
        problemas = []
        texto_normalizado = normalizar_texto(texto)
        
        for regra in self.padroes_auditoria:
            matches = list(re.finditer(regra["regex"], texto, re.IGNORECASE | re.MULTILINE))
            
            if matches:
                for match in matches:
                    inicio = max(0, match.start() - 50)
                    fim = min(len(texto_normalizado), match.end() + 50)
                    contexto = texto_normalizado[inicio:fim]
                    
                    problemas.append({
                        **regra,
                        "contexto": f"...{contexto}..." if contexto else "",
                        "pagina": 1
                    })
        
        info = self.extrair_informacoes(texto)
        
        if info.get('chave_acesso'):
            chave = info['chave_acesso']
            if len(chave) != 44 or not chave.isdigit():
                problemas.append({
                    "id": "nfe_chave_erro",
                    "nome": "Chave de Acesso com Erro",
                    "exp": f"Chave '{chave}' não possui 44 dígitos numéricos.",
                    "lei": "Portaria CAT 142/2018",
                    "contexto": f"Chave encontrada: {chave}",
                    "pagina": 1
                })
        
        if info.get('data_emissao'):
            try:
                data_emissao = datetime.strptime(info['data_emissao'], '%d/%m/%Y')
                if (datetime.now() - data_emissao).days > 365 * 5:
                    problemas.append({
                        "id": "nfe_muito_antiga",
                        "nome": "Nota Fiscal Muito Antiga",
                        "exp": f"Nota emitida em {info['data_emissao']} - pode estar prescrita para créditos fiscais.",
                        "lei": "Art. 198, RICMS/SP",
                        "contexto": f"Data de emissão: {info['data_emissao']}",
                        "pagina": 1
                    })
            except:
                pass
        
        return problemas, info

# --------------------------------------------------
# ANALISADOR DE CONTRATOS DE SERVIÇOS
# --------------------------------------------------

class ContratoServicoAnalyser:
    """Analisa contratos de prestação de serviços"""
    
    def __init__(self):
        self.tipo = "contrato_servico"
        
        # Regras de auditoria específicas para contratos de serviços
        self.regras = [
            {
                "id": "serv_clausula_aberta",
                "regex": r"(a criterio|a juizo|exclusivamente|unicamente).*?(contratada|prestador|fornecedor)",
                "nome": "Cláusula Excessivamente Aberta",
                "gravidade": "critico",
                "exp": "Cláusulas que deixam decisões importantes 'a critério' de uma das partes podem ser abusivas.",
                "lei": "Art. 51, X, Código de Defesa do Consumidor (CDC)"
            },
            {
                "id": "serv_prazo_aberto",
                "regex": r"(prazo indeterminado|por tempo indeterminado|prazo ilimitado)",
                "nome": "Prazo Indeterminado",
                "gravidade": "critico",
                "exp": "Contratos de serviços não podem ter prazo indeterminado para prestação contínua.",
                "lei": "Art. 2º, Lei 8.078/90 (CDC)"
            },
            {
                "id": "serv_rescisao_unilateral",
                "regex": r"(contratada|prestador).*?(resolver|rescisao|rescindir).*?(unilateralmente|por si|sozinha)",
                "nome": "Rescisão Unilateral para Prestador",
                "gravidade": "critico",
                "exp": "Cláusula que permite apenas ao prestador rescindir o contrato unilateralmente é abusiva.",
                "lei": "Art. 51, IV, CDC"
            },
            {
                "id": "serv_multas_desproporcionais",
                "regex": r"(multa.*?(100|cem|integral|total).*?valor.*?servico)|(multa.*?superior.*?30.*?por cento)",
                "nome": "Multas Desproporcionais",
                "gravidade": "critico",
                "exp": "Multas superiores a 30% do valor do serviço ou multas integrais são consideradas abusivas.",
                "lei": "Art. 52, CDC e Súmula 421 STJ"
            },
            {
                "id": "serv_juros_abusivos",
                "regex": r"(juros.*?(superior|maior|acima).*?(1|2|3).*?por cento.*?mes)|(juros.*?(30|40|50).*?ano)",
                "nome": "Juros Abusivos",
                "gravidade": "critico",
                "exp": "Juros superiores a 1% ao mês (ou 12,68% ao ano) podem ser considerados abusivos em contratos consumeristas.",
                "lei": "Lei 8.078/90 (CDC) e jurisprudência do STJ"
            },
            {
                "id": "serv_indenizacao_ilimitada",
                "regex": r"(indenizacao|ressarcimento|responsabilidade).*?(integral|total|ilimitada|sem limite)",
                "nome": "Responsabilidade Civil Ilimitada",
                "gravidade": "medio",
                "exp": "Cláusulas que estabelecem responsabilidade civil ilimitada para o contratante são abusivas.",
                "lei": "Art. 51, I, CDC"
            },
            {
                "id": "serv_obrigacoes_desproporcionais",
                "regex": r"(obrigacoes|responsabilidades).*?(desproporcionais|excessivas|desmedidas)",
                "nome": "Obrigações Desproporcionais",
                "gravidade": "medio",
                "exp": "Cláusulas que criam obrigações desproporcionais ao contratante são nulas.",
                "lei": "Art. 51, IV, CDC"
            },
            {
                "id": "serv_alteracao_unilateral",
                "regex": r"(alterar|modificar|mudar).*?(unilateralmente|por si|sozinha|a seu criterio).*?(contrato|termos|condicoes)",
                "nome": "Alteração Unilateral do Contrato",
                "gravidade": "critico",
                "exp": "O prestador não pode alterar unilateralmente as condições contratuais.",
                "lei": "Art. 51, V, CDC"
            },
            {
                "id": "serv_renuncia_direitos",
                "regex": r"(renuncia|abdicacao|desistencia).*?(direitos|garantias|beneficios).*?(legais|contratuais)",
                "nome": "Renúncia a Direitos Legais",
                "gravidade": "critico",
                "exp": "Cláusula que obriga renúncia a direitos legais é nula de pleno direito.",
                "lei": "Art. 51, XIV, CDC"
            },
            {
                "id": "serv_foro_inacessivel",
                "regex": r"(foro|comarca|jurisdicao).*?(municipio|cidade|local).*?(distante|inacessivel|outro estado)",
                "nome": "Foro de Eleição Inacessível",
                "gravidade": "medio",
                "exp": "Cláusula que estabelece foro em local distante da residência do consumidor é abusiva.",
                "lei": "Art. 51, VII, CDC"
            },
            {
                "id": "serv_objeto_indefinido",
                "regex": r"(objeto.*?contrato|servicos.*?contratados).*?(vago|indefinido|amplo|generico)",
                "nome": "Objeto do Contrato Indefinido",
                "gravidade": "medio",
                "exp": "O objeto do contrato deve ser claramente especificado, com escopo bem definido.",
                "lei": "Art. 46, CDC e Art. 112, Código Civil"
            },
            {
                "id": "serv_penhora_salario",
                "regex": r"(penhora|onera).*?(salario|ordenado|remuneracao|vencimentos)",
                "nome": "Penhora de Salário",
                "gravidade": "critico",
                "exp": "Cláusula que autoriza penhora de salário é abusiva e ilegal.",
                "lei": "Lei 8.009/90 (Impenhorabilidade do Bem de Família)"
            },
            {
                "id": "serv_confissao_divida",
                "regex": r"(confissao).*?(divida|debito)",
                "nome": "Confissão Antecipada de Dívida",
                "gravidade": "critico",
                "exp": "Cláusula de confissão de dívida é nula em contratos de adesão.",
                "lei": "Art. 52, §2º, CDC"
            }
        ]
        
        # Padrões para extração de informações
        self.padroes_extracao = {
            'partes_contratantes': r'(CONTRATANTE|TOMADOR).*?(?::|\n)\s*(.+?)\n',
            'prestador_servicos': r'(CONTRATADA|PRESTADOR).*?(?::|\n)\s*(.+?)\n',
            'valor_contrato': r'(VALOR|PREÇO).*?(?::|\n)\s*R?\$?\s*([\d.,]+)',
            'prazo_execucao': r'(PRAZO.*?EXECUÇÃO|DURAÇÃO.*?SERVIÇOS).*?(?::|\n)\s*(.+?)\n',
            'objeto_contrato': r'(OBJETO).*?(?::|\n)\s*(.+?)(?:\n|\.)',
            'forma_pagamento': r'(FORMA.*?PAGAMENTO|PAGAMENTO).*?(?::|\n)\s*(.+?)\n'
        }
    
    def extrair_informacoes_contrato(self, texto):
        """Extrai informações importantes do contrato"""
        info = {}
        
        for campo, padrao in self.padroes_extracao.items():
            match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                info[campo] = match.group(2).strip()
            else:
                info[campo] = None
        
        # Extrair cláusulas numeradas
        clausulas = re.findall(r'CL[ÁA]USULA\s+(\w+)[\.:]\s*(.+?)(?=\nCL[ÁA]USULA|\n\d|\Z)', 
                              texto, re.IGNORECASE | re.DOTALL)
        info['total_clausulas'] = len(clausulas)
        
        return info
    
    def analisar_contrato(self, texto_completo):
        """Realiza análise completa do contrato de serviços"""
        problemas = []
        problemas_ja_encontrados = set()
        
        texto_normalizado = normalizar_texto(texto_completo)
        
        # Análise por regras
        for regra in self.regras:
            matches = list(re.finditer(regra["regex"], texto_normalizado, re.IGNORECASE))
            
            if matches:
                for match in matches:
                    chave_duplicata = f"{regra['id']}_{match.start()}"
                    if chave_duplicata not in problemas_ja_encontrados:
                        inicio = max(0, match.start() - 80)
                        fim = min(len(texto_normalizado), match.end() + 80)
                        contexto = texto_normalizado[inicio:fim]
                        
                        problema = {
                            "id": regra["id"],
                            "nome": regra["nome"],
                            "gravidade": regra["gravidade"],
                            "exp": regra["exp"],
                            "lei": regra["lei"],
                            "contexto": f"...{contexto}..." if contexto else "",
                            "pagina": 1  # Em análise simplificada
                        }
                        
                        problemas.append(problema)
                        problemas_ja_encontrados.add(chave_duplicata)
        
        # Ordenar por gravidade (crítico primeiro)
        problemas.sort(key=lambda x: 0 if x['gravidade'] == 'critico' else 1 if x['gravidade'] == 'medio' else 2)
        
        # Extrair informações do contrato
        info_contrato = self.extrair_informacoes_contrato(texto_completo)
        
        return problemas, info_contrato

# --------------------------------------------------
# ANALISADOR DE CONTRATOS DE COMPRA E VENDA DE IMÓVEIS
# --------------------------------------------------

class ContratoCompraVendaAnalyser:
    """Analisa contratos de compra e venda de imóveis"""
    
    def __init__(self):
        self.tipo = "contrato_compra_venda"
        
        # Regras de auditoria específicas para contratos de compra e venda
        self.regras = [
            {
                "id": "cv_imovel_nao_identificado",
                "regex": r"(im[oó]vel|propriedade|bem).*?(indefinido|n[ãa]o identificado|n[ãa]o descrito|gen[ée]rico)",
                "nome": "Imóvel Não Identificado",
                "gravidade": "critico",
                "exp": "O imóvel deve ser perfeitamente identificado com matrícula, endereço completo, metragem e confrontações.",
                "lei": "Art. 108, I, Código Civil e Art. 1º, Lei 6.015/73 (Lei de Registros Públicos)"
            },
            {
                "id": "cv_sem_matricula",
                "regex": r"(matr[íi]cula|registro|n[úu]mero).*?(n[ãa]o informado|ausente|omitido)",
                "nome": "Falta de Número de Matrícula",
                "gravidade": "critico",
                "exp": "Todo imóvel deve ter número de matrícula no Registro de Imóveis. Contrato sem essa informação é inválido.",
                "lei": "Art. 167, Lei 6.015/73"
            },
            {
                "id": "cv_preco_nao_definido",
                "regex": r"(pre[çc]o|valor).*?(a combinar|a definir|ser[áa] definido|posteriormente)",
                "nome": "Preço Não Definido",
                "gravidade": "critico",
                "exp": "O preço deve ser certo e determinado. Cláusulas que deixam para definir posteriormente tornam o contrato nulo.",
                "lei": "Art. 426, Código Civil"
            },
            {
                "id": "cv_multa_penal_desproporcional",
                "regex": r"(multa.*?penal|cl[áa]usula.*?penal).*?(50|60|70|80|90|100).*?por cento",
                "nome": "Multa Penal Desproporcional",
                "gravidade": "critico",
                "exp": "Multas superiores a 30% do valor do imóvel podem ser consideradas abusivas e passíveis de revisão judicial.",
                "lei": "Art. 413, Código Civil e jurisprudência do STJ"
            },
            {
                "id": "cv_renuncia_direitos_essenciais",
                "regex": r"(renuncia|abdica).*?(direito.*?(evic[çc][ãa]o|vicio.*?oculto|garantia))",
                "nome": "Renúncia a Direitos Essenciais",
                "gravidade": "critico",
                "exp": "O comprador não pode renunciar aos direitos de evicção e vícios ocultos. Cláusula é nula.",
                "lei": "Art. 441, Código Civil"
            },
            {
                "id": "cv_entrega_chaves_nao_definida",
                "regex": r"(entrega.*?chaves|posse).*?(indefinida|a combinar|quando.*?poss[íi]vel)",
                "nome": "Entrega de Chaves Indefinida",
                "gravidade": "medio",
                "exp": "A data de entrega das chaves e da posse deve ser certa e determinada.",
                "lei": "Art. 426, Código Civil"
            },
            {
                "id": "cv_responsabilidade_tributaria_ambigua",
                "regex": r"(tributos|impostos|taxas).*?(ambos|comprador.*?vendedor|partilhado)",
                "nome": "Responsabilidade Tributária Ambígua",
                "gravidade": "medio",
                "exp": "Deve estar claro quem paga cada tributo (ITBI, Registro, etc.). Ambiguidades geram conflitos.",
                "lei": "Art. 1.078, Código Civil"
            },
            {
                "id": "cv_clausula_arrocho",
                "regex": r"(arrocho|vincula|obriga).*?(terceiro|familiares|herdeiros)",
                "nome": "Cláusula de Arrocho",
                "gravidade": "critico",
                "exp": "Cláusulas que vinculam terceiros não signatários do contrato são nulas.",
                "lei": "Art. 426, Código Civil e Princípio da Relatividade Contratual"
            },
            {
                "id": "cv_foro_distante",
                "regex": r"(foro|comarca|ju[íi]zo).*?(distante|inacess[íi]vel|outro.*?munic[íi]pio)",
                "nome": "Foro de Eleição Inacessível",
                "gravidade": "medio",
                "exp": "Foro em local distante da situação do imóvel pode ser considerado abusivo.",
                "lei": "Art. 78, Código de Processo Civil"
            },
            {
                "id": "cv_financiamento_condicionado",
                "regex": r"(financiamento|empr[ée]stimo).*?(condicionado|incerto|n[ãa]o garantido)",
                "nome": "Financiamento Não Garantido",
                "gravidade": "medio",
                "exp": "Se a compra depende de financiamento, deve haver cláusula resolutiva expressa caso seja negado.",
                "lei": "Art. 474, Código Civil"
            },
            {
                "id": "cv_pendencia_nao_resolvida",
                "regex": r"(pend[êe]ncia|[ôo]nus|gravame).*?(n[ãa]o resolvido|pendente|existente)",
                "nome": "Pendências Não Resolvidas",
                "gravidade": "critico",
                "exp": "O imóvel deve estar livre de ônus, gravames e ações judiciais na data da escritura.",
                "lei": "Art. 1.345, Código Civil"
            },
            {
                "id": "cv_sem_laudo_vistoria",
                "regex": r"(vistoria|laudo|avalia[çc][ãa]o).*?(n[ãa]o.*?realizada|dispensada|n[ãa]o necess[áa]ria)",
                "nome": "Ausência de Vistoria Prévia",
                "gravidade": "leve",
                "exp": "Recomenda-se sempre vistoria técnica prévia para identificar possíveis vícios.",
                "lei": "Art. 441, Código Civil"
            },
            {
                "id": "cv_prazo_escritura_indefinido",
                "regex": r"(escritura|registro).*?(prazo|data).*?(indefinido|a combinar|flex[íi]vel)",
                "nome": "Prazo para Escritura Indefinido",
                "gravidade": "medio",
                "exp": "O prazo para lavratura da escritura pública deve ser determinado.",
                "lei": "Art. 426, Código Civil"
            }
        ]
        
        # Padrões para extração de informações
        self.padroes_extracao = {
            'vendedor': r'VENDEDOR.*?(?::|\n)\s*(.+?)(?:\n|\.)',
            'comprador': r'COMPRADOR.*?(?::|\n)\s*(.+?)(?:\n|\.)',
            'valor_imovel': r'VALOR.*?(?::|\n)\s*R?\$?\s*([\d.,]+)',
            'matricula': r'MATR[ÍI]CULA.*?(?::|\n)\s*(\w+.*?)(?:\n|\.)',
            'endereco_imovel': r'ENDERE[ÇC]O.*?(?::|\n)\s*(.+?)(?:\n|\.)',
            'sinal': r'SINAL.*?(?::|\n)\s*R?\$?\s*([\d.,]+)',
            'prazo_escritura': r'PRAZO.*?ESCRITURA.*?(?::|\n)\s*(.+?)(?:\n|\.)',
            'data_entrega': r'ENTREGA.*?CHAVES.*?(?::|\n)\s*(.+?)(?:\n|\.)'
        }
    
    def extrair_informacoes_contrato(self, texto):
        """Extrai informações importantes do contrato"""
        info = {}
        
        for campo, padrao in self.padroes_extracao.items():
            match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                info[campo] = match.group(1).strip()
            else:
                info[campo] = None
        
        # Verificar se é contrato com financiamento
        financiamento_match = re.search(r'FINANCIAMENTO|EMPR[ÉE]STIMO', texto, re.IGNORECASE)
        info['tem_financiamento'] = bool(financiamento_match)
        
        # Extrair cláusulas numeradas
        clausulas = re.findall(r'CL[ÁA]USULA\s+(\w+)[\.:]\s*(.+?)(?=\nCL[ÁA]USULA|\n\d|\Z)', 
                              texto, re.IGNORECASE | re.DOTALL)
        info['total_clausulas'] = len(clausulas)
        
        return info
    
    def analisar_contrato(self, texto_completo):
        """Realiza análise completa do contrato de compra e venda"""
        problemas = []
        problemas_ja_encontrados = set()
        
        texto_normalizado = normalizar_texto(texto_completo)
        
        # Análise por regras
        for regra in self.regras:
            matches = list(re.finditer(regra["regex"], texto_normalizado, re.IGNORECASE))
            
            if matches:
                for match in matches:
                    chave_duplicata = f"{regra['id']}_{match.start()}"
                    if chave_duplicata not in problemas_ja_encontrados:
                        inicio = max(0, match.start() - 100)
                        fim = min(len(texto_normalizado), match.end() + 100)
                        contexto = texto_normalizado[inicio:fim]
                        
                        problema = {
                            "id": regra["id"],
                            "nome": regra["nome"],
                            "gravidade": regra["gravidade"],
                            "exp": regra["exp"],
                            "lei": regra["lei"],
                            "contexto": f"...{contexto}..." if contexto else "",
                            "pagina": 1
                        }
                        
                        problemas.append(problema)
                        problemas_ja_encontrados.add(chave_duplicata)
        
        # Análises contextuais adicionais
        info_contrato = self.extrair_informacoes_contrato(texto_completo)
        
        # Verificar se o preço está definido numericamente
        if info_contrato.get('valor_imovel'):
            if re.search(r'a combinar|a definir|ser[áa] definido', info_contrato['valor_imovel'], re.IGNORECASE):
                problemas.append({
                    "id": "cv_preco_textual",
                    "nome": "Preço em Formato Textual",
                    "gravidade": "critico",
                    "exp": "O preço deve ser expresso em valor numérico, não em descrição textual.",
                    "lei": "Art. 426, Código Civil",
                    "contexto": f"Preço encontrado: {info_contrato['valor_imovel']}",
                    "pagina": 1
                })
        
        # Verificar se há matrícula
        if not info_contrato.get('matricula'):
            problemas.append({
                "id": "cv_sem_matricula_detectado",
                "nome": "Matrícula Não Encontrada",
                "gravidade": "critico",
                "exp": "Não foi possível identificar o número de matrícula do imóvel no contrato.",
                "lei": "Art. 167, Lei 6.015/73",
                "contexto": "Verifique se a matrícula está mencionada no documento",
                "pagina": 1
            })
        
        # Verificar sinal vs valor total
        if info_contrato.get('sinal') and info_contrato.get('valor_imovel'):
            try:
                sinal_valor = float(info_contrato['sinal'].replace('.', '').replace(',', '.'))
                valor_total = float(info_contrato['valor_imovel'].replace('.', '').replace(',', '.'))
                percentual_sinal = (sinal_valor / valor_total) * 100
                
                if percentual_sinal > 30:
                    problemas.append({
                        "id": "cv_sinal_excessivo",
                        "nome": "Sinal Excessivo",
                        "gravidade": "medio",
                        "exp": f"Sinal de {percentual_sinal:.1f}% do valor total. Valores acima de 30% podem ser considerados excessivos.",
                        "lei": "Jurisprudência consumerista",
                        "contexto": f"Sinal: R$ {sinal_valor:.2f} | Valor total: R$ {valor_total:.2f}",
                        "pagina": 1
                    })
            except:
                pass
        
        # Ordenar por gravidade (crítico primeiro)
        problemas.sort(key=lambda x: 0 if x['gravidade'] == 'critico' else 1 if x['gravidade'] == 'medio' else 2)
        
        return problemas, info_contrato

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def normalizar_texto(t):
    if t:
        t = "".join(ch for ch in unicodedata.normalize('NFKD', t) if not unicodedata.combining(ch))
        return " ".join(t.lower().split())
    return ""

def obter_cor_gravidade(gravidade):
    if gravidade == 'critico':
        return '#c53030'  # Vermelho
    elif gravidade == 'medio':
        return '#d69e2e'  # Amarelo/laranja
    else:
        return '#38a169'  # Verde

def obter_icone_documento(tipo_doc):
    icones = {
        'contrato_locacao': '🏠',
        'nota_fiscal': '🧾',
        'contrato_servico': '⚖️',
        'contrato_compra_venda': '💰',
        'desconhecido': '📄'
    }
    return icones.get(tipo_doc, '📄')

# --------------------------------------------------
# LÓGICA DE AUDITORIA PARA CONTRATO DE LOCAÇÃO
# --------------------------------------------------

def realizar_auditoria_contrato_locacao(arquivo_pdf):
    problemas_detectados = []
    problemas_ja_encontrados = set()
    
    regras = [
        {"id": "readjust", "regex": r"reajuste.*?(trimestral|mensal|semestral|3|tres|6|seis|bianual|bimestral|4|quatro)", 
         "nome": "Reajuste Ilegal", 
         "exp": "O reajuste de aluguel deve ser ANUAL (12 meses). Períodos menores são ilegais.", 
         "lei": "Lei 10.192/01"},
        
        {"id": "improvements", "regex": r"(renuncia|nao indeniza|sem direito|nao tem direito|nao recebera).*?(benfeitoria|reforma|obra|melhoria|investimento)", 
         "nome": "Cláusula de Benfeitorias", 
         "exp": "O inquilino tem direito a indenização por reformas necessárias. Cláusula de renúncia é nula.", 
         "lei": "Art. 35, Lei 8.245/91"},
        
        {"id": "proportion", "regex": r"(multa.*?(12|doze|integral|total|cheia|completa).*?(aluguel|meses))|(pagar.*?(12|doze).*?meses.*?multa)", 
         "nome": "Multa s/ Proporcionalidade", 
         "exp": "A multa deve ser proporcional ao tempo que resta de contrato. Multa integral de 12 meses é abusiva.", 
         "lei": "Art. 4º, Lei 8.245/91 e Art. 51, CDC"},
        
        {"id": "privacy", "regex": r"(qualquer|sem aviso|independente|livre|a qualquer).*?(visita|vistoria|ingresso|entrar|acesso|inspecao)", 
         "nome": "Violação de Privacidade", 
         "exp": "O locador não pode entrar no imóvel sem aviso prévio e hora combinada.", 
         "lei": "Art. 23, IX, Lei 8.245/91"},
        
        {"id": "guarantee_dupla", "regex": r"(fiador.*?(caucao|deposito|seguro|aval))|((caucao|deposito|seguro|aval).*?fiador)|(exige.*?(fiador.*?caucao|caucao.*?fiador))", 
         "nome": "Garantia Dupla Ilegal", 
         "exp": "É proibido exigir mais de uma garantia no mesmo contrato (ex: fiador E caução).", 
         "lei": "Art. 37, Lei 8.245/91"},
        
        {"id": "summary_eviction", "regex": r"(despejo|desocupacao).*?(imediata|sumario|automatico|sem notificacao)", 
         "nome": "Despejo Sumário Ilegal", 
         "exp": "O despejo requer processo judicial e não pode ser automático por cláusula contratual.", 
         "lei": "Art. 9º, Lei 8.245/91"},
        
        {"id": "sale_eviction", "regex": r"(venda|alienacao).*?(rescindir|terminar|desocupar|despejo)", 
         "nome": "Cláusula 'Venda Despeja'", 
         "exp": "A venda do imóvel não rescinde automaticamente o contrato. Inquilino tem preferência.", 
         "lei": "Art. 27, Lei 8.245/91"},
        
        {"id": "no_pets", "regex": r"(proibido|nao permitido|vedado).*?(animais|pet|cao|gato|animal)", 
         "nome": "Proibição Total de Animais", 
         "exp": "Cláusula que proíbe qualquer animal pode ser considerada abusiva, exceto por justa causa.", 
         "lei": "Art. 51, CDC e Súmula 482 STJ"},
    ]

    with pdfplumber.open(arquivo_pdf) as pdf:
        texto_completo = ""
        
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text() or ""
            texto_completo += texto_pag + "\n"
        
        texto_normalizado = normalizar_texto(texto_completo)
        
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text() or ""
            texto_limpo = normalizar_texto(texto_pag)
            
            for r in regras:
                matches_pagina = list(re.finditer(r["regex"], texto_limpo, re.IGNORECASE))
                
                if matches_pagina:
                    for match in matches_pagina:
                        chave_duplicata = f"{r['id']}_{i+1}_{match.start()}"
                        if chave_duplicata not in problemas_ja_encontrados:
                            inicio = max(0, match.start() - 50)
                            fim = min(len(texto_limpo), match.end() + 50)
                            contexto = texto_limpo[inicio:fim]
                            
                            problemas_detectados.append({
                                **r, 
                                "pagina": i + 1,
                                "contexto": f"...{contexto}..." if contexto else "",
                                "posicao": match.start()
                            })
                            problemas_ja_encontrados.add(chave_duplicata)
    
    problemas_detectados.sort(key=lambda x: (x['pagina'], x.get('posicao', 0)))
    return problemas_detectados

# --------------------------------------------------
# FUNÇÃO PRINCIPAL DE AUDITORIA
# --------------------------------------------------

def realizar_auditoria_total(arquivo_pdf):
    with pdfplumber.open(arquivo_pdf) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto = pagina.extract_text() or ""
            texto_completo += texto + "\n"
    
    detector = DocumentTypeDetector()
    tipo_documento = detector.detectar_tipo(texto_completo)
    
    st.session_state['tipo_documento'] = tipo_documento
    st.session_state['texto_completo'] = texto_completo[:1000] + "..."
    
    if tipo_documento == 'contrato_locacao':
        return realizar_auditoria_contrato_locacao(arquivo_pdf), tipo_documento
    
    elif tipo_documento == 'nota_fiscal':
        leitor_nf = NotaFiscalReader()
        problemas, informacoes = leitor_nf.auditoria_nfe(texto_completo)
        st.session_state['informacoes_nf'] = informacoes
        return problemas, tipo_documento
    
    elif tipo_documento == 'contrato_servico':
        analisador_servico = ContratoServicoAnalyser()
        problemas, info_contrato = analisador_servico.analisar_contrato(texto_completo)
        st.session_state['info_contrato_servico'] = info_contrato
        return problemas, tipo_documento
    
    elif tipo_documento == 'contrato_compra_venda':
        analisador_compra_venda = ContratoCompraVendaAnalyser()
        problemas, info_contrato = analisador_compra_venda.analisar_contrato(texto_completo)
        st.session_state['info_contrato_cv'] = info_contrato
        return problemas, tipo_documento
    
    elif tipo_documento == 'desconhecido':
        return [], tipo_documento
    
    else:
        return [], tipo_documento

# --------------------------------------------------
# CABEÇALHO PROFISSIONAL
# --------------------------------------------------
st.markdown('<h1 class="header-title">Burocrata de Bolso</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Sistema de Análise Jurídica e Fiscal de Documentos</p>', unsafe_allow_html=True)

# --------------------------------------------------
# LAYOUT PRINCIPAL
# --------------------------------------------------
col_upload, col_status = st.columns([2, 1])

with col_upload:
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.subheader("Análise de Documento")
    
    arquivo = st.file_uploader(
        "Selecione um documento em formato PDF",
        type=["pdf"],
        help="Documentos suportados: Contratos de locação, Notas Fiscais Eletrônicas, Contratos de Serviços, Contratos de Compra e Venda"
    )
    
    if arquivo:
        if st.button("Iniciar Análise Jurídica", type="primary", use_container_width=True):
            with st.spinner("Realizando análise técnica..."):
                achados, tipo_doc = realizar_auditoria_total(arquivo)
                
                st.session_state['achados'] = achados
                st.session_state['tipo_doc'] = tipo_doc
                st.session_state['analisado'] = True
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_status:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    
    if st.session_state.get('analisado', False):
        achados = st.session_state.get('achados', [])
        tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
        
        # Cálculo de score adaptado ao tipo de documento
        if tipo_doc == 'contrato_compra_venda':
            # Contratos de compra e venda são mais críticos
            penalidade_critico = sum(1 for a in achados if a.get('gravidade') == 'critico') * 25
            penalidade_medio = sum(1 for a in achados if a.get('gravidade') == 'medio') * 15
            penalidade_leve = sum(1 for a in achados if a.get('gravidade') == 'leve') * 5
            penalidade = min(penalidade_critico + penalidade_medio + penalidade_leve, 100)
        else:
            penalidade = min(len(achados) * 15, 100)
        
        score = max(100 - penalidade, 0)
        
        st.markdown("**Índice de Conformidade**")
        
        if score >= 80:
            st.markdown(f'<h2 class="score-excellent">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Conforme")
        elif score >= 60:
            st.markdown(f'<h2 class="score-moderate">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Atenção Necessária")
        else:
            st.markdown(f'<h2 class="score-critical">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Não Conforme")
        
        st.progress(score / 100)
        
        icone = obter_icone_documento(tipo_doc)
        st.markdown(f"**Documento:** {icone} {tipo_doc.replace('_', ' ').title()}")
        st.markdown(f"**Problemas:** {len(achados)}")
    else:
        st.markdown("**Índice de Conformidade**")
        st.markdown('<h2>--/100</h2>', unsafe_allow_html=True)
        st.markdown("**Status:** Aguardando análise")
        st.progress(0)
        st.markdown("**Documento:** Não analisado")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# RESULTADOS DA ANÁLISE
# --------------------------------------------------
if st.session_state.get('analisado', False):
    achados = st.session_state.get('achados', [])
    tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
    
    if achados:
        st.markdown("---")
        st.subheader("Resultados da Auditoria")
        
        # Sumário executivo
        col_summary, col_details = st.columns([1, 2])
        
        with col_summary:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**Sumário Executivo**")
            
            icone = obter_icone_documento(tipo_doc)
            st.markdown(f"- Tipo: {icone} {tipo_doc.replace('_', ' ').title()}")
            st.markdown(f"- Total de problemas: {len(achados)}")
            
            if tipo_doc == 'contrato_locacao':
                st.markdown("- Área: Direito Imobiliário")
                st.markdown("- Legislação: Lei 8.245/91 (Lei do Inquilinato)")
            elif tipo_doc == 'nota_fiscal':
                st.markdown("- Área: Direito Tributário")
                st.markdown("- Legislação: Legislação Tributária Federal")
            elif tipo_doc == 'contrato_servico':
                st.markdown("- Área: Direito Civil e Consumerista")
                st.markdown("- Legislação: Código Civil e CDC")
            elif tipo_doc == 'contrato_compra_venda':
                st.markdown("- Área: Direito Imobiliário e Registral")
                st.markdown("- Legislação: Código Civil e Lei 6.015/73")
            
            # Estatísticas por gravidade (para documentos com sistema de gravidade)
            if tipo_doc in ['contrato_servico', 'contrato_compra_venda']:
                criticos = sum(1 for a in achados if a.get('gravidade') == 'critico')
                medios = sum(1 for a in achados if a.get('gravidade') == 'medio')
                leves = sum(1 for a in achados if a.get('gravidade') == 'leve')
                
                if criticos > 0:
                    st.markdown(f"- <span style='color: #c53030;'>Críticos: {criticos}</span>", unsafe_allow_html=True)
                if medios > 0:
                    st.markdown(f"- <span style='color: #d69e2e;'>Médios: {medios}</span>", unsafe_allow_html=True)
                if leves > 0:
                    st.markdown(f"- <span style='color: #38a169;'>Leves: {leves}</span>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Informações específicas do contrato (quando aplicável)
            if tipo_doc == 'contrato_servico' and 'info_contrato_servico' in st.session_state:
                info = st.session_state['info_contrato_servico']
                with st.expander("📋 Informações do Contrato"):
                    if info.get('partes_contratantes'):
                        st.markdown(f"**Contratante:** {info['partes_contratantes']}")
                    if info.get('prestador_servicos'):
                        st.markdown(f"**Prestador:** {info['prestador_servicos']}")
                    if info.get('valor_contrato'):
                        st.markdown(f"**Valor:** R$ {info['valor_contrato']}")
                    if info.get('prazo_execucao'):
                        st.markdown(f"**Prazo:** {info['prazo_execucao']}")
                    if info.get('total_clausulas'):
                        st.markdown(f"**Cláusulas:** {info['total_clausulas']}")
            
            elif tipo_doc == 'contrato_compra_venda' and 'info_contrato_cv' in st.session_state:
                info = st.session_state['info_contrato_cv']
                with st.expander("🏠 Informações do Imóvel"):
                    if info.get('vendedor'):
                        st.markdown(f"**Vendedor:** {info['vendedor']}")
                    if info.get('comprador'):
                        st.markdown(f"**Comprador:** {info['comprador']}")
                    if info.get('valor_imovel'):
                        st.markdown(f"**Valor do Imóvel:** R$ {info['valor_imovel']}")
                    if info.get('matricula'):
                        st.markdown(f"**Matrícula:** {info['matricula']}")
                    if info.get('endereco_imovel'):
                        st.markdown(f"**Endereço:** {info['endereco_imovel']}")
                    if info.get('sinal'):
                        st.markdown(f"**Sinal:** R$ {info['sinal']}")
                    if info.get('tem_financiamento'):
                        st.markdown("**Financiamento:** Sim")
        
        with col_details:
            for a in achados:
                # Determinar estilo baseado na gravidade
                if a.get('gravidade') == 'critico':
                    border_color = '#c53030'
                    tag_html = '<span class="tag-critico">CRÍTICO</span>'
                elif a.get('gravidade') == 'medio':
                    border_color = '#d69e2e'
                    tag_html = '<span class="tag-medio">MÉDIO</span>'
                elif a.get('gravidade') == 'leve':
                    border_color = '#38a169'
                    tag_html = '<span class="tag-leve">LEVE</span>'
                else:
                    border_color = '#2c5282'
                    tag_html = ''
                
                with st.expander(f"{a['nome']} {tag_html}", unsafe_allow_html=True):
                    st.markdown(f"**Descrição:** {a['exp']}")
                    st.markdown(f"**Fundamento Legal:** {a.get('lei', 'Não especificado')}")
                    
                    if a.get('contexto'):
                        st.markdown("**Contexto Encontrado:**")
                        st.markdown(f'<div style="background-color: #f7fafc; padding: 10px; border-radius: 4px; border-left: 3px solid {border_color}; font-size: 14px; font-family: monospace;">{a["contexto"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"**Localização:** Página {a.get('pagina', 1)}")
    
    else:
        st.markdown("---")
        st.markdown('<div class="analysis-card" style="border-left-color: #38a169;">', unsafe_allow_html=True)
        st.markdown("**Resultado da Análise**")
        
        if tipo_doc == 'nota_fiscal':
            st.markdown("✅ A nota fiscal analisada está conforme os padrões verificados.")
            
            if 'informacoes_nf' in st.session_state:
                info = st.session_state['informacoes_nf']
                with st.expander("Informações da Nota Fiscal"):
                    cols = st.columns(2)
                    with cols[0]:
                        if info.get('numero'):
                            st.markdown(f"**Número:** {info.get('numero')}")
                        if info.get('data_emissao'):
                            st.markdown(f"**Data de Emissão:** {info.get('data_emissao')}")
                    with cols[1]:
                        if info.get('valor_total'):
                            st.markdown(f"**Valor Total:** R$ {info.get('valor_total')}")
                        if info.get('chave_acesso'):
                            st.markdown(f"**Chave de Acesso:**")
                            st.code(info.get('chave_acesso'), language="text")
        
        elif tipo_doc == 'contrato_locacao':
            st.markdown("✅ O contrato de locação analisado não apresenta irregularidades nas cláusulas verificadas.")
        
        elif tipo_doc == 'contrato_servico':
            st.markdown("✅ O contrato de serviços analisado não apresenta irregularidades críticas nas cláusulas verificadas.")
            
            if 'info_contrato_servico' in st.session_state:
                info = st.session_state['info_contrato_servico']
                with st.expander("📋 Informações do Contrato"):
                    if info.get('partes_contratantes'):
                        st.markdown(f"**Contratante:** {info['partes_contratantes']}")
                    if info.get('prestador_servicos'):
                        st.markdown(f"**Prestador:** {info['prestador_servicos']}")
                    if info.get('valor_contrato'):
                        st.markdown(f"**Valor:** R$ {info['valor_contrato']}")
                    if info.get('prazo_execucao'):
                        st.markdown(f"**Prazo:** {info['prazo_execucao']}")
        
        elif tipo_doc == 'contrato_compra_venda':
            st.markdown("✅ O contrato de compra e venda analisado não apresenta irregularidades críticas nas cláusulas verificadas.")
            
            if 'info_contrato_cv' in st.session_state:
                info = st.session_state['info_contrato_cv']
                with st.expander("🏠 Informações do Imóvel"):
                    if info.get('vendedor'):
                        st.markdown(f"**Vendedor:** {info['vendedor']}")
                    if info.get('comprador'):
                        st.markdown(f"**Comprador:** {info['comprador']}")
                    if info.get('valor_imovel'):
                        st.markdown(f"**Valor do Imóvel:** R$ {info['valor_imovel']}")
                    if info.get('matricula'):
                        st.markdown(f"**Matrícula:** {info['matricula']}")
        
        else:
            st.markdown("✅ O documento analisado não apresenta irregularidades nos padrões verificados.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# CONSOLE TÉCNICO
# --------------------------------------------------
st.markdown("---")
st.subheader("Console Técnico")

col_console, col_assist = st.columns([2, 1])

with col_console:
    st.markdown('<div class="console-header">Log da Análise</div>', unsafe_allow_html=True)
    st.markdown('<div class="console-body">', unsafe_allow_html=True)
    
    if st.session_state.get('analisado', False):
        achados = st.session_state.get('achados', [])
        tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
        
        icone = obter_icone_documento(tipo_doc)
        st.markdown(f"[INFO] Tipo de documento: {icone} {tipo_doc}")
        st.markdown(f"[INFO] Problemas encontrados: {len(achados)}")
        
        if tipo_doc in ['contrato_servico', 'contrato_compra_venda']:
            # Estatísticas detalhadas para documentos com sistema de gravidade
            criticos = sum(1 for a in achados if a.get('gravidade') == 'critico')
            medios = sum(1 for a in achados if a.get('gravidade') == 'medio')
            leves = sum(1 for a in achados if a.get('gravidade') == 'leve')
            
            st.markdown(f"[STATS] Críticos: {criticos} | Médios: {medios} | Leves: {leves}")
            
            if tipo_doc == 'contrato_compra_venda' and 'info_contrato_cv' in st.session_state:
                info = st.session_state['info_contrato_cv']
                if info.get('matricula'):
                    st.markdown(f"[INFO] Matrícula identificada: {info['matricula'][:50]}...")
                if info.get('valor_imovel'):
                    st.markdown(f"[INFO] Valor do imóvel: R$ {info['valor_imovel']}")
        
        if achados:
            for a in achados:
                gravidade = a.get('gravidade', 'N/A')
                if gravidade == 'critico':
                    prefix = "[ALERTA CRÍTICO]"
                elif gravidade == 'medio':
                    prefix = "[ALERTA MÉDIO]"
                elif gravidade == 'leve':
                    prefix = "[ALERTA LEVE]"
                else:
                    prefix = "[ALERTA]"
                
                st.markdown(f"{prefix} {a['nome']} - Página {a.get('pagina', 1)}")
                st.markdown(f"       Lei: {a.get('lei', 'N/A')}")
        else:
            st.markdown("[INFO] Auditoria concluída sem alertas")
        
        st.markdown(f"[STATUS] Análise concluída às {datetime.now().strftime('%H:%M:%S')}")
    
    else:
        st.markdown("[INFO] Sistema inicializado")
        st.markdown("[INFO] Aguardando upload de documento")
        st.markdown("[STATUS] Pronto para análise")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_assist:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("**Assistente Jurídico**")
    
    if prompt := st.text_input("Consultar orientação:", placeholder="Digite sua dúvida sobre o documento..."):
        with st.spinner("Analisando consulta..."):
            st.markdown("---")
            
            if st.session_state.get('tipo_doc'):
                tipo_doc = st.session_state.get('tipo_doc')
                
                if tipo_doc == 'nota_fiscal':
                    if any(termo in prompt.lower() for termo in ['chave', 'acesso', 'validação']):
                        st.markdown("**Orientação:** A chave de acesso da NF-e possui 44 dígitos e pode ser validada no portal da Receita Federal através do DANFE.")
                    elif any(termo in prompt.lower() for termo in ['validade', 'prescrição', 'prazo']):
                        st.markdown("**Orientação:** Notas fiscais devem ser arquivadas por 5 anos para fins fiscais. Para créditos de ICMS, o prazo prescricional é de 5 anos.")
                    else:
                        st.markdown("**Orientação:** Para dúvidas específicas sobre NF-e, consulte a legislação tributária aplicável ou contate um contador especializado.")
                
                elif tipo_doc == 'contrato_locacao':
                    if any(termo in prompt.lower() for termo in ['reajuste', 'aumento']):
                        st.markdown("**Orientação:** Reajustes de aluguel em contratos residenciais devem ser anuais, conforme Lei do Inquilinato (Lei 8.245/91).")
                    elif any(termo in prompt.lower() for termo in ['multa', 'rescisão']):
                        st.markdown("**Orientação:** Multas rescisórias devem ser proporcionais ao tempo restante de contrato. Multas integrais são consideradas abusivas.")
                    else:
                        st.markdown("**Orientação:** Para questões contratuais complexas, recomenda-se consulta a advogado especializado em direito imobiliário.")
                
                elif tipo_doc == 'contrato_servico':
                    if any(termo in prompt.lower() for termo in ['multa', 'penalidade']):
                        st.markdown("**Orientação:** Em contratos de serviços, multas superiores a 30% do valor do contrato podem ser consideradas abusivas (CDC Art. 52).")
                    elif any(termo in prompt.lower() for termo in ['juros', 'moratória']):
                        st.markdown("**Orientação:** Juros em contratos consumeristas não devem exceder 1% ao mês. Valores superiores podem ser revisados judicialmente.")
                    elif any(termo in prompt.lower() for termo in ['rescisão', 'cancelar']):
                        st.markdown("**Orientação:** Contratos de serviços podem ser rescindidos com 30 dias de antecedência, conforme CDC. Multas devem ser proporcionais.")
                    elif any(termo in prompt.lower() for termo in ['responsabilidade', 'indenização']):
                        st.markdown("**Orientação:** Cláusulas de responsabilidade civil ilimitada são nulas em contratos de adesão (CDC Art. 51, I).")
                    else:
                        st.markdown("**Orientação:** Para contratos de serviços, atenção especial às cláusulas abusivas listadas no Art. 51 do Código de Defesa do Consumidor.")
                
                elif tipo_doc == 'contrato_compra_venda':
                    if any(termo in prompt.lower() for termo in ['matrícula', 'registro']):
                        st.markdown("**Orientação:** A matrícula do imóvel é essencial. Verifique no Cartório de Registro de Imóveis se está regular e sem ônus.")
                    elif any(termo in prompt.lower() for termo in ['sinal', 'arras']):
                        st.markdown("**Orientação:** O sinal (arras) confirmatórias em geral fica entre 5% e 30% do valor. Acima de 30% pode ser considerado excessivo.")
                    elif any(termo in prompt.lower() for termo in ['multa', 'desistência']):
                        st.markdown("**Orientação:** Multas por desistência em compra e venda geralmente são de 30% do valor. Valores superiores podem ser revisados.")
                    elif any(termo in prompt.lower() for termo in ['itbi', 'imposto']):
                        st.markdown("**Orientação:** O ITBI é de responsabilidade do comprador. As taxas de registro são divididas entre as partes, mas é negociável.")
                    elif any(termo in prompt.lower() for termo in ['escritura', 'cartório']):
                        st.markdown("**Orientação:** A escritura pública deve ser lavrada em cartório dentro do prazo contratual. Atrasos podem gerar multas.")
                    elif any(termo in prompt.lower() for termo in ['vício', 'defeito']):
                        st.markdown("**Orientação:** O vendedor responde por vícios ocultos por 1 ano após a entrega do imóvel, mesmo que não mencionado no contrato.")
                    else:
                        st.markdown("**Orientação:** Para contratos de compra e venda, verifique sempre a matrícula, ônus reais e a escrituração. Consulte um advogado especializado.")
                
                else:
                    st.markdown("**Orientação:** Recomenda-se análise jurídica especializada para este tipo de documento.")
            else:
                st.markdown("**Orientação:** Faça o upload e análise do documento para obter orientações específicas.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# BARRA LATERAL
# --------------------------------------------------
with st.sidebar:
    st.markdown('<p class="sidebar-title">Módulos Disponíveis</p>', unsafe_allow_html=True)
    
    modulos = {
        "🏠 Contratos de Locação": {
            "status": "ativo",
            "desc": "Análise de 8 cláusulas problemáticas com base na Lei do Inquilinato",
            "clausulas": "Reajuste, Benfeitorias, Multa, Privacidade, Garantia, Despejo, Venda, Animais",
            "icon": "🏠"
        },
        "🧾 Notas Fiscais": {
            "status": "ativo", 
            "desc": "Validação de dados fiscais e conformidade tributária",
            "clausulas": "Chave de acesso, CNPJ, Data, Valores",
            "icon": "🧾"
        },
        "⚖️ Contratos de Serviços": {
            "status": "ativo",
            "desc": "Análise de 13 cláusulas críticas em contratos de prestação de serviços",
            "clausulas": "Prazo aberto, Multas, Juros, Responsabilidade, Rescisão, Foro, Renúncia",
            "icon": "⚖️"
        },
        "💰 Contratos de Compra e Venda": {
            "status": "ativo",
            "desc": "Análise de 13 cláusulas críticas em contratos de compra e venda de imóveis",
            "clausulas": "Matrícula, Preço, Multa, Evicção, Tributos, Financiamento",
            "icon": "💰"
        }
    }
    
    for modulo, info in modulos.items():
        st.markdown(f"{info['icon']} **{modulo}**")
        st.markdown(f'<div style="font-size: 12px; color: #4a5568; margin-bottom: 10px;">{info["desc"]}</div>', unsafe_allow_html=True)
        
        if info.get("clausulas"):
            with st.expander(f"📋 Cláusulas analisadas"):
                st.markdown(f'<div style="font-size: 11px; color: #718096;">{info["clausulas"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**Legenda de Gravidade**")
    st.markdown("""
    <div style="font-size: 12px;">
    <span style="color: #c53030; font-weight: bold;">● Crítico:</span> Cláusula nula ou ilegal<br>
    <span style="color: #d69e2e; font-weight: bold;">● Médio:</span> Cláusula potencialmente abusiva<br>
    <span style="color: #38a169; font-weight: bold;">● Leve:</span> Recomendação de ajuste
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**Dicas para Contratos de Compra e Venda**")
    st.markdown("""
    <div style="font-size: 12px;">
    1. Verifique a matrícula no Cartório<br>
    2. Confirme ônus e ações judiciais<br>
    3. Defina prazos certos para escritura<br>
    4. Estabeleça responsabilidades tributárias<br>
    5. Inclua cláusula de financiamento<br>
    6. Faça vistoria técnica prévia
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**Informações do Sistema**")
    st.markdown(f'<div style="font-size: 12px; color: #4a5568;">Versão: 10.0</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size: 12px; color: #4a5568;">Última atualização: {datetime.now().strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**Aviso Legal**")
    st.markdown("""
    <div style="font-size: 11px; color: #718096;">
    Este sistema fornece análise automática com base em padrões predefinidos. 
    Não substitui a consulta a profissional qualificado. 
    Os resultados são informativos e não constituem orientação jurídica formal.
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# RODAPÉ
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 12px; padding: 20px;">
    Burocrata de Bolso | Sistema de Análise Jurídica de Documentos © 2024<br>
    Todos os direitos reservados | Processamento realizado localmente
</div>
""", unsafe_allow_html=True)
