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
    <h2>Login JOSE VALDO</h2>
    <form method='post'>
        <label>Senha</label>
        <input type='password' name='senha'>
        <button type='submit'>Entrar</button>
    </form>
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

    # HTML INLINE
    HTML = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Orçamento Elétrico</title>
    <style>
    body{font-family:Arial;background:#f4f4f4;padding:20px}
    form{background:#fff;padding:20px;border-radius:6px;box-shadow:0 0 10px rgba(0,0,0,0.1);}
    label{display:block;margin-top:10px}
    input,select{width:100%;padding:8px;margin-top:5px;border:1px solid #ccc;border-radius:4px}
    button{width:100%;padding:12px;margin-top:15px;border:none;border-radius:6px;font-weight:bold;cursor:pointer;transition:0.3s}
    #addBtn{background:#0D47A1;color:#fff}
    #addBtn:hover{background:#1976D2}
    #pdfBtn{background:#FF9800;color:#fff}
    #pdfBtn:hover{background:#FB8C00}
    table{width:100%;border-collapse:collapse;margin-top:10px}
    th,td{border:1px solid #ccc;padding:6px;text-align:center}
    </style>
    </head>
    <body>

    <h2>⚡ Orçamento JVSN-VALDO</h2>

    <form method="POST">

    <label>Cliente</label>
    <input name="cliente" required>

    <label>Telefone</label>
    <input name="telefone">

    <label>Tipo</label>
    <select name="tipo">
    <option>Residencial</option>
    <option>Predial</option>
    </select>

    <hr>

    <label>Serviço padrão</label>
    <select id="padrao" onchange="autoFill()">
    <option value="">Selecione</option>
    {% for s,v in servicos.items() %}
    <option value="{{s}}|{{v}}">{{s}} - R$ {{v}}</option>
    {% endfor %}
    </select>

    <label>Descrição</label>
    <input id="desc">

    <label>Qtd</label>
    <input id="qtd" type="number" value="1">

    <label>Valor</label>
    <input id="val" type="number" value="0">

    <button type="button" id="addBtn" onclick="add()">➕ Adicionar Serviço</button>

    <table id="tab">
    <tr><th>Serviço</th><th>Qtd</th><th>Valor</th><th>Total</th></tr>
    </table>

    <input type="hidden" name="itens" id="itens">

    <hr>

    <label>Subtotal</label>
    <input id="subtotal" name="subtotal" readonly>

    <label>Desconto</label>
    <input id="desconto" name="desconto" value="0" oninput="calc()">

    <label>Total</label>
    <input id="total" name="total" readonly>
    
    <label>Pagamento</label>
    <select name="pagamento" multiple size="4">
    <option>Pix (11921733556)</option>
    <option>Cartão de Crédito</option>
    <option>Cartão de Débito</option>
    <option>Dinheiro</option>
    </select>

    <button type="submit" id="pdfBtn">💾 Gerar PDF</button>

    </form>

    <script>
    let itens=[], subtotal=0;

    function autoFill(){
     let v=document.getElementById("padrao").value;
     if(!v)return;
     let p=v.split("|");
     desc.value=p[0]; val.value=p[1];
    }

    function add(){
     let d=desc.value, q=Number(qtd.value), v=Number(val.value);
     if(!d||q<=0||v<=0)return;
     let t=q*v; subtotal+=t;
     itens.push({descricao:d,qtd:q,valor:v,total:t});

     let r=tab.insertRow();
     r.insertCell(0).innerText=d;
     r.insertCell(1).innerText=q;
     r.insertCell(2).innerText=v.toFixed(2);
     r.insertCell(3).innerText=t.toFixed(2);

     subtotalEl(); desc.value=""; val.value=0; qtd.value=1;
    }

    function subtotalEl(){
     subtotal.value=subtotal.toFixed(2);
     calc();
     itensField();
    }

    function calc(){
     total.value=(subtotal - Number(desconto.value || 0)).toFixed(2);
    }

    function itensField(){
     document.getElementById("itens").value=JSON.stringify(itens);
    }
    </script>

    </body>
    </html>
    """
    return render_template_string(HTML, servicos=SERVICOS_PADRAO)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



#if __name__ == "__main__":
    #app.run(debug=True)

