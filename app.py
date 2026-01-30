from fpdf import FPDF
import base64

def criar_contrato_locacao_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="CONTRATO DE LOCAÇÃO RESIDENCIAL", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    
    # Texto do contrato com armadilhas
    texto = """Pelo presente instrumento particular de locação, de um lado, MARIA DA SILVA SANTOS, 
    brasileira, solteira, empresária, portadora do CPF nº 123.456.789-00, 
    residente e domiciliada na Rua das Flores, 100, Centro, São Paulo-SP, 
    doravante denominada LOCADORA; e de outro lado, JOÃO PEREIRA OLIVEIRA, 
    brasileiro, casado, engenheiro, portador do CPF nº 987.654.321-00, 
    residente e domiciliado na Rua das Palmeiras, 200, Jardins, São Paulo-SP, 
    doravante denominado LOCATÁRIO, têm entre si justo e acertado o presente 
    contrato de locação, que se regerá pelas cláusulas seguintes:

    CLÁUSULA PRIMEIRA - DO OBJETO
    A LOCADORA dá em locação ao LOCATÁRIO, que aceita, o imóvel residencial 
    situado à Avenida Paulista, 1000, apartamento 101, Bela Vista, São Paulo-SP.

    CLÁUSULA SEGUNDA - DO PRAZO
    O presente contrato terá vigência de 30 meses, iniciando-se em 01/01/2024.

    CLÁUSULA TERCEIRA - DO VALOR DO ALUGUEL
    O aluguel mensal será de R$ 3.000,00. O reajuste será trimestral, 
    conforme índices oficiais. [ARMADILHA 1: Reajuste trimestral é ilegal]

    CLÁUSULA QUARTA - DAS GARANTIAS
    Para garantia do fiel cumprimento, o LOCATÁRIO deverá apresentar:
    a) 2 fiadores com renda comprovada;
    b) Depósito caução de 3 meses de aluguel.
    [ARMADILHA 2: Garantia dupla - fiador + caução é ilegal]

    CLÁUSULA QUINTA - DAS BENFEITORIAS
    O LOCATÁRIO renuncia a qualquer indenização por benfeitorias necessárias 
    realizadas no imóvel. [ARMADILHA 3: Renúncia a benfeitorias é nula]

    CLÁUSULA SEXTA - DAS VISITAS
    A LOCADORA poderá realizar visitas ao imóvel a qualquer tempo, sem aviso 
    prévio. [ARMADILHA 4: Violação de privacidade]

    CLÁUSULA SÉTIMA - DA MULTA
    Em caso de rescisão antecipada, será devida multa de 12 meses de aluguel.

    CLÁUSULA OITAVA - DOS ANIMAIS
    É vedada a permanência de quaisquer animais no imóvel.

    CLÁUSULA NONA - DA VENDA DO IMÓVEL
    Em caso de venda, o contrato estará automaticamente rescindido.

    CLÁUSULA DÉCIMA - DO FORO
    Fica eleito o foro da Comarca de São Paulo.

    São Paulo, 15 de dezembro de 2023

    ___________________________
    LOCADORA

    ___________________________
    LOCATÁRIO

    ___________________________
    Testemunha 1

    ___________________________
    Testemunha 2"""
    
    for linha in texto.split('\n'):
        pdf.multi_cell(0, 10, txt=linha)
    
    # Salvar em memória
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

# Criar o PDF e disponibilizar para download
pdf_bytes = criar_contrato_locacao_pdf()

st.download_button(
    label="📥 Baixar Contrato de Locação (com armadilhas)",
    data=pdf_bytes,
    file_name="contrato_locacao_armadilhas.pdf",
    mime="application/pdf",
    help="Clique para baixar um contrato de locação com 4 armadilhas para testar o sistema"
)
