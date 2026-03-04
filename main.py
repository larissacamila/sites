from flask import Flask, render_template_string, request, send_file, session, redirect, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from datetime import date
import os, uuid, json

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_qualquer"

SENHA = "josevaldo123"

SERVICOS_PADRAO = {
    "INSTALAÇÃO DE IDR (INTERRUPTOR DIFERENCIAL RESIDUAL)": 150.50,
    "INSTALAÇÃO DE DPS - DISPOSITIVO DE PROTEÇÃO CONTRA SURTOS": 129.50,
    "INSTALAÇÃO DE HASTE ATERRAMENTO": 210.50,
    "INSTALAÇÃO CARREGADOR VEICULAR": 1881.50,
    "INSTALAÇÃO DE AR SPLIT 12000 BTUS": 581.00,
}

def to_float(v):
    try: return float(v)
    except: return 0.0

def gerar_pdf(d, itens):
    nome = f"orcamento_{uuid.uuid4().hex}.pdf"
    c = canvas.Canvas(nome, pagesize=A4)

    AZUL = HexColor("#0D47A1")
    LARANJA = HexColor("#FF9800")
    CINZA = HexColor("#444")

    if os.path.exists("static/logo.jpeg"):
        c.drawImage("static/logo.jpeg", 40, 780, 120, 50)

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(AZUL)
    c.drawString(180, 800, "ORÇAMENTO JVSN-VALDO")

    c.setFont("Helvetica", 10)
    c.drawString(180, 780, "Email: valdo.soares@jvsn.com.br")

    c.setStrokeColor(LARANJA)
    c.setLineWidth(2)
    c.line(40, 760, 550, 760)

    c.setFont("Helvetica", 11)
    c.setFillColor(CINZA)
    c.drawString(40, 735, f"Cliente: {d['cliente']}")
    c.drawString(40, 718, f"Telefone: {d['telefone']}")
    c.drawString(40, 701, f"Email Cliente: {d['email_cliente']}")
    c.drawString(400, 735, f"Data: {d['data']}")

    y = 660
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Serviço")
    c.drawString(300, y, "Qtd")
    c.drawString(360, y, "Valor")
    c.drawString(450, y, "Total")
    y -= 15

    c.setFont("Helvetica", 11)
    for i in itens:
        c.drawString(40, y, i["descricao"])
        c.drawString(300, y, str(i["qtd"]))
        c.drawString(360, y, f"R$ {i['valor']:.2f}")
        c.drawString(450, y, f"R$ {i['total']:.2f}")
        y -= 18

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(360, y, "TOTAL:")
    c.drawString(450, y, f"R$ {d['total']:.2f}")

    y -= 40
    c.setFont("Helvetica", 11)
    c.drawString(40, y, "Formas de Pagamento:")
    y -= 15
    for p in d["pagamentos"]:
        c.drawString(60, y, f"- {p}")
        y -= 14

    y -= 40
    c.line(40, y, 250, y)
    c.drawString(40, y-15, "Assinatura do Cliente")

    c.save()
    return nome

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST" and request.form.get("senha")==SENHA:
        session["logado"]=True
        return redirect("/")
    return """<form method='post'><input type='password' name='senha'><button>Entrar</button></form>"""

@app.route("/", methods=["GET","POST"])
def index():
    if not session.get("logado"): return redirect("/login")

    if request.method=="POST":
        itens=json.loads(request.form["itens"])
        d={
            "cliente":request.form["cliente"],
            "telefone":request.form["telefone"],
            "email_cliente":request.form.get("email_cliente",""),
            "total":to_float(request.form["total"]),
            "pagamentos":request.form.getlist("pagamento"),
            "data":date.today().strftime("%d/%m/%Y")
        }
        return send_file(gerar_pdf(d,itens), as_attachment=True)

    HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<style>
body{font-family:Arial;background:#f4f4f4;padding:15px}
form{background:#fff;padding:15px;border-radius:6px}
input,select{width:100%;padding:8px;margin:6px 0}
button{padding:12px;width:100%;margin-top:10px}
</style></head>
<body>

<h2>⚡ Orçamento JVSN-VALDO</h2>

<form method="post">
<input name="cliente" placeholder="Cliente" required>
<input name="telefone" placeholder="Telefone">
<input name="email_cliente" placeholder="Email do cliente (opcional)">

<label>Serviço</label>
<select id="padrao" onchange="autoFill()">
<option value="">Selecione</option>
{% for s,v in servicos.items() %}
<option value="{{s}}|{{v}}">{{s}}</option>
{% endfor %}
</select>

<input id="desc" placeholder="Descrição">
<input id="qtd" type="number" value="1">
<input id="val" type="number" value="0">

<button type="button" onclick="add()">Adicionar</button>

<table id="tab"></table>
<input type="hidden" name="itens" id="itens">

<input id="total" name="total" readonly>

<label>Pagamento</label>
<label><input type="checkbox" name="pagamento" value="Pix"> Pix</label><br>
<label><input type="checkbox" name="pagamento" value="Cartão Crédito"> Crédito</label><br>
<label><input type="checkbox" name="pagamento" value="Cartão Débito"> Débito</label><br>
<label><input type="checkbox" name="pagamento" value="Dinheiro"> Dinheiro</label>

<button>Gerar PDF</button>
</form>

<script>
let itens=[], total=0;
function autoFill(){
 let p=padrao.value.split("|");
 desc.value=p[0]; val.value=p[1];
}
function add(){
 let q=+qtd.value,v=+val.value,t=q*v;
 itens.push({descricao:desc.value,qtd:q,valor:v,total:t});
 total+=t; totalEl();
 let r=tab.insertRow(); r.insertCell(0).innerText=desc.value;
}
function totalEl(){
 total.value=total.toFixed(2);
 itensField();
}
function itensField(){
 itensInput.value=JSON.stringify(itens);
}
</script>

</body></html>
"""
    return render_template_string(HTML, servicos=SERVICOS_PADRAO)

app.run(host="0.0.0.0", port=10000)
