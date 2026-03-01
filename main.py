from flask import Flask, render_template_string, request, send_file, session, redirect, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from datetime import date
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_qualquer"  # necessário para session

# ======================
# CONFIGURAÇÃO LOGIN
# ======================
SENHA = "josevaldo123"  # altere para a senha desejada

# ======================
# TABELA PADRÃO COMPLETA (preço médio)
# ======================
SERVICOS_PADRAO = {
    "INSTALAÇÃO DE IDR (INTERRUPTOR DIFERENCIAL RESIDUAL)": 150.50,
    "INSTALAÇÃO DE DPS - DISPOSITIVO DE PROTEÇÃO CONTRA SURTOS": 129.50,
    "INSTALAÇÃO DE BARRAMENTO PENTE MONOPOLAR NO QDC": 70.00,
    "INSTALAÇÃO DE BARRAMENTO PENTE BIPOLAR NO QDC": 81.00,
    "INSTALAÇÃO DE BARRAMENTO PENTE TRIPOLAR NO QDC": 92.00,
    "INSTALAÇÃO DE BARRAMENTO DE NEUTRO e OU TERRA": 92.00,
    "INSTALAÇÃO DE HASTE ATERRAMENTO": 210.50,
    "INSTALAÇÃO DE CONTATOR E OU RELÉ TÉRMICO": 231.50,
    "INSTALAÇÃO E MONTAGEM QDC (6 CIRCUITOS + DR + DPS)": 559.50,
    "INSTALAÇÃO E MONTAGEM QDC (12 CIRCUITOS + DR + DPS)": 833.50,
    "INSTALAÇÃO E MONTAGEM QDC (18 CIRCUITOS + DR + DPS)": 1038.00,
    "INSTALAÇÃO E MONTAGEM QDC (24 CIRCUITOS + DR + DPS)": 1387.00,
    "PASSAGEM DE CABOS ENTRADA MONOFÁSICA (QM PARA QDC)": 215.50,
    "PASSAGEM DE CABOS ENTRADA BIFÁSICA OU TRIFÁSICA (QM PARA QDC)": 285.50,
    "ALIMENTAÇÃO PARA MOTORES": 204.50,
    "CURTO CIRCUITO MONOFÁSICO": 172.50,
    "CURTO CIRCUITO BIFÁSICO": 204.50,
    "CURTO CIRCUITO TRIFÁSICO": 237.00,
    "INSTALAÇÃO DE MEDIDOR (Padrão de entrada - Monofásico 127V ou 220V)": 1494.50,
    "INSTALAÇÃO DE MEDIDOR (Padrão de entrada - Bifásico 220V)": 1736.50,
    "INSTALAÇÃO DE MEDIDOR (Padrão de entrada - Trifásico 220V)": 1962.50,
    "INSTALAÇÃO CARREGADOR VEICULAR": 1881.50,
    "ALIMENTAÇÃO ELÉTRICA PARA AR CONDICIONADO": 124.50,
    "INSTALAÇÃO DE AR Condicionado SPLIT INVERTER 9000 BTUS": 581.00,
    "INSTALAÇÃO DE AR Condicionado SPLIT INVERTER 12000 BTUS": 581.00,
    "INSTALAÇÃO DE AR Condicionado SPLIT INVERTER 18000 BTUS": 694.00,
    "INSTALAÇÃO DE AR Condicionado SPLIT INVERTER 24000 BTUS": 812.00,
    "INSTALAÇÃO DE AR Condicionado SPLIT INVERTER 30000 BTUS": 978.50,
    "INSTALAÇÃO DE AR Condicionado ON OFF convencional 9000 BTUS": 511.00,
    "INSTALAÇÃO DE AR Condicionado ON OFF convencional 12000 BTUS": 570.50,
    "INSTALAÇÃO DE AR Condicionado ON OFF convencional 18000 BTUS": 624.00,
    "INSTALAÇÃO DE AR Condicionado ON OFF convencional 24000 BTUS": 737.00,
    "INSTALAÇÃO DE AR Condicionado ON OFF convencional 30000 BTUS": 855.00,
    "LIMPEZA EM TUBULAÇÃO DE AR CONDICIONADO (existente no local)": 70.50,
    "INSTALAÇÃO DE PAINEL SOLAR (com Gerador Solar de 8kWp)": 9245.50,
    "ATENDIMENTO TÉCNICO EMERGENCIAL (Final de semana)": 274.50,
    "ATENDIMENTO TÉCNICO EMERGENCIAL (Durante a semana)": 204.50,
    "INSTALAÇÃO DE INTERRUPTOR INTELIGENTE": 205.00,
    "INSTALAÇÃO MINI RELE INTERRUPTOR": 231.00,
    "INSTALAÇÃO RELE DE IMPULSO": 188.50,
    "INSTALAÇÃO RELE DIMMER": 231.50,
    "INSTALAÇÃO E CONFIGURAÇÃO CONTROLE REMOTO UNIVERSAL": 178.00,
    "INSTALAÇÃO DE TOMADA INTELIGENTE": 108.00,
    "INSTALAÇÃO MINI RELE CONTROLE DE PERSIANA": 231.50,
    "INSTALAÇÃO E CONFIGURAÇÃO HUB": 204.50,
    "INSTALAÇÃO E CONFIGURAÇÃO ROTEADOR": 205.00,
    "INSTALAÇÃO E CONFIGURAÇÃO FECHADURA INTELIGENTE": 312.00,
    "INSTALAÇÃO E CONFIGURAÇÃO ASSISTENTE VIRTUAL (ALEXA)": 172.50
}

# ======================
# FUNÇÃO SEGURA PARA FLOAT
# ======================
def to_float(valor):
    try:
        return float(valor)
    except:
        return 0.0

# ======================
# FUNÇÃO GERAR PDF
# ======================
def gerar_pdf(dados, itens):
    nome = f"orcamento_{uuid.uuid4().hex}.pdf"
    c = canvas.Canvas(nome, pagesize=A4)

    AZUL = HexColor("#0D47A1")
    LARANJA = HexColor("#FF9800")
    CINZA = HexColor("#555555")

    # LOGO
    if os.path.exists("static/logo.jpeg"):
        c.drawImage("static/logo.jpeg", 40, 770, width=100, height=50, mask='auto')

    # TÍTULO
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(AZUL)
    c.drawString(160, 800, "ORÇAMENTO JVSN-VALDO")

    # LINHA HEADER
    c.setStrokeColor(LARANJA)
    c.setLineWidth(3)
    c.line(40, 760, 550, 760)

    # DADOS CLIENTE
    c.setFont("Helvetica", 11)
    c.setFillColor(CINZA)
    c.drawString(40, 730, f"Cliente: {dados['cliente']}")
    c.drawString(40, 710, f"Telefone: {dados['telefone']}")
    c.drawString(40, 690, f"Tipo: {dados['tipo']}")
    c.drawString(400, 730, f"Data: {dados['data']}")

    # TABELA SERVIÇOS
    y = 650
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Serviço")
    c.drawString(300, y, "Qtd")
    c.drawString(360, y, "Valor")
    c.drawString(450, y, "Total")
    c.line(40, y-5, 550, y-5)

    y -= 20
    c.setFont("Helvetica", 11)
    for i in itens:
        c.drawString(40, y, i["descricao"])
        c.drawString(310, y, str(i["qtd"]))
        c.drawString(360, y, f"R$ {i['valor']:.2f}")
        c.drawString(450, y, f"R$ {i['total']:.2f}")
        y -= 18

    # TOTAL
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(AZUL)
    c.drawString(360, y, "Subtotal:")
    c.drawString(450, y, f"R$ {dados['subtotal']:.2f}")
    y -= 20
    c.drawString(360, y, "Desconto:")
    c.drawString(450, y, f"R$ {dados['desconto']:.2f}")
    y -= 25
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(LARANJA)
    c.drawString(360, y, "TOTAL:")
    c.drawString(450, y, f"R$ {dados['total']:.2f}")

    # FORMA DE PAGAMENTO
    y -= 40
    c.setFont("Helvetica", 11)
    c.setFillColor(CINZA)
    c.drawString(40, y, f"Pagamento: {dados['pagamento']}")

    # CAMPO ASSINATURA CLIENTE
    y -= 60
    c.setStrokeColor(CINZA)
    c.line(40, y, 250, y)
    c.setFont("Helvetica", 10)
    c.drawString(40, y-15, "Assinatura do Cliente")

    # RODAPÉ
    c.setStrokeColor(LARANJA)
    c.line(40, 80, 550, 80)
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, 60, "Validade do orçamento: 7 dias")
    c.drawRightString(550, 60, "Manutenção Elétrica Residencial e Predial/Email:valdo.soares@jvsn.com.br")

    c.save()
    return nome

# ======================
# ROTA LOGIN
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        senha = request.form.get("senha", "")
        if senha == SENHA:
            session["logado"] = True
            return redirect(url_for("index"))
        else:
            return "<h3>Senha incorreta!</h3>", 401
    return """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login JOSE VALDO</title>
    <style>
    body{font-family:Arial;background:#f4f4f4;padding:15px;margin:0}
    h2{text-align:center;color:#0D47A1}
    form{max-width:400px;margin:0 auto;background:#fff;padding:20px;border-radius:6px;box-shadow:0 0 10px rgba(0,0,0,0.1)}
    label{display:block;margin-top:10px;font-weight:bold}
    input{width:100%;padding:10px;margin-top:5px;border:1px solid #ccc;border-radius:4px;box-sizing:border-box}
    button{width:100%;padding:12px;margin-top:15px;border:none;border-radius:6px;font-weight:bold;cursor:pointer;background:#FF9800;color:#fff}
    button:hover{background:#FB8C00}
    </style>
    </head>
    <body>
    <h2>Login JOSE VALDO</h2>
    <form method='post'>
        <label>Senha</label>
        <input type='password' name='senha' required>
        <button type='submit'>Entrar</button>
    </form>
    </body>
    </html>
    """

# ======================
# ROTA PRINCIPAL
# ======================
@app.route("/", methods=["GET","POST"])
def index():
    if not session.get("logado"):
        return redirect(url_for("login"))

    if request.method == "POST":
        itens_json = request.form.get("itens", "[]")
        if not itens_json.strip():
            itens_json = "[]"
        try:
            itens = json.loads(itens_json)
        except json.JSONDecodeError:
            itens = []

        if not itens:
            return "<h3>Adicione ao menos um serviço!</h3>", 400

        dados = {
            "cliente": request.form.get("cliente", ""),
            "telefone": request.form.get("telefone", ""),
            "tipo": request.form.get("tipo", ""),
            "subtotal": to_float(request.form.get("subtotal")),
            "desconto": to_float(request.form.get("desconto")),
            "total": to_float(request.form.get("total")),
            "pagamento": request.form.get("pagamento", ""),
            "data": date.today().strftime("%d/%m/%Y")
        }

        pdf = gerar_pdf(dados, itens)
        return send_file(pdf, as_attachment=True)

    # HTML ADAPTADO PARA CELULAR
    HTML = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orçamento Elétrico</title>
    <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:Arial,sans-serif;background:#f4f4f4;padding:15px}
    h2{text-align:center;color:#0D47A1;margin-bottom:20px}
    form{background:#fff;padding:20px;border-radius:8px;box-shadow:0 0 10px rgba(0,0,0,0.1);max-width:100%;overflow-x:auto}
    label{display:block;margin-top:15px;font-weight:bold;color:#333}
    input,select{width:100%;padding:12px;margin-top:5px;border:1px solid #ddd;border-radius:4px;font-size:16px}
    button{width:100%;padding:14px;margin-top:20px;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:16px;transition:background 0.3s}
    #addBtn{background:#0D47A1;color:#fff}
    #addBtn:hover{background:#1976D2}
    #pdfBtn{background:#FF9800;color:#fff;margin-top:25px}
    #pdfBtn:hover{background:#FB8C00}
    table{width:100%;border-collapse:collapse;margin-top:20px;min-width:400px}
    th,td{border:1px solid #ddd;padding:10px;text-align:left}
    th{background:#f8f8f8;color:#0D47A1}
    hr{margin:25px 0;border:none


