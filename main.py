from flask import Flask, render_template_string, request, send_file, session, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from datetime import date
import os, uuid, json

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_qualquer"

SENHA = "josevaldo123"

SERVICOS_PADRAO = {
    "INSTALAÇÃO DE IDR": 150.50,
    "INSTALAÇÃO DE DPS": 129.50,
    "INSTALAÇÃO DE HASTE ATERRAMENTO": 210.50,
    "INSTALAÇÃO CARREGADOR VEICULAR": 1881.50,
    "INSTALAÇÃO AR SPLIT 12000 BTUS": 581.00
}

def f(v):
    try: return float(v)
    except: return 0.0

# ================= PDF =================
def gerar_pdf(d, itens):
    nome = f"orcamento_{uuid.uuid4().hex}.pdf"
    c = canvas.Canvas(nome, pagesize=A4)

    if os.path.exists("static/logo.jpeg"):
        c.drawImage("static/logo.jpeg", 40, 780, 120, 50)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(170, 800, "ORÇAMENTO JVSN-VALDO")
    c.setFont("Helvetica", 10)
    c.drawString(170, 782, "Email: valdo.soares@jvsn.com.br")

    c.setFont("Helvetica", 11)
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

    y -= 15
    c.drawString(360, y, f"Subtotal: R$ {d['subtotal']:.2f}")
    y -= 15
    c.drawString(360, y, f"Desconto: R$ {d['desconto']:.2f}")
    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(360, y, f"TOTAL: R$ {d['total']:.2f}")

    y -= 35
    c.setFont("Helvetica", 11)
    c.drawString(40, y, "Formas de Pagamento:")
    y -= 15
    for p in d["pagamentos"]:
        c.drawString(60, y, f"- {p}")
        y -= 14

    c.line(40, 120, 250, 120)
    c.drawString(40, 105, "Assinatura do Cliente")

    c.save()
    return nome

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST" and request.form.get("senha") == SENHA:
        session["logado"] = True
        return redirect("/")
    return "<form method='post'><input type='password' name='senha'><button>Entrar</button></form>"

# ================= APP =================
@app.route("/", methods=["GET","POST"])
def index():
    if not session.get("logado"):
        return redirect("/login")

    if request.method == "POST":
        itens_raw = request.form.get("itens","[]")
        try:
            itens = json.loads(itens_raw)
        except:
            itens = []

        d = {
            "cliente": request.form.get("cliente",""),
            "telefone": request.form.get("telefone",""),
            "email_cliente": request.form.get("email_cliente",""),
            "subtotal": f(request.form.get("subtotal")),
            "desconto": f(request.form.get("desconto")),
            "total": f(request.form.get("total")),
            "pagamentos": request.form.getlist("pagamento"),
            "data": date.today().strftime("%d/%m/%Y")
        }

        return send_file(gerar_pdf(d, itens), as_attachment=True)

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width">
<style>
body{font-family:Arial;background:#f4f4f4;padding:15px}
form{background:#fff;padding:15px;border-radius:6px}
input,select{width:100%;padding:8px;margin:6px 0}
button{width:100%;padding:12px;margin-top:10px}
table{width:100%;margin-top:10px}
</style>
</head>
<body>

<h2>⚡ Orçamento JVSN-VALDO</h2>

<form method="post">
<input name="cliente" placeholder="Cliente" required>
<input name="telefone" placeholder="Telefone">
<input name="email_cliente" placeholder="Email do cliente">

<select id="padrao" onchange="autoFill()">
<option value="">Serviço padrão</option>
{% for s,v in servicos.items() %}
<option value="{{s}}|{{v}}">{{s}}</option>
{% endfor %}
</select>

<input id="desc" placeholder="Descrição">
<input id="qtd" type="number" value="1">
<input id="val" type="number" value="0">

<button type="button" onclick="add()">Adicionar Serviço</button>

<table id="tab"></table>

<input type="hidden" name="itens" id="itens">
<input id="subtotal" name="subtotal" readonly>
<input id="desconto" name="desconto" value="0" oninput="calc()">
<input id="total" name="total" readonly>

<label><input type="checkbox" name="pagamento" value="Pix"> Pix</label>
<label><input type="checkbox" name="pagamento" value="Crédito"> Crédito</label>
<label><input type="checkbox" name="pagamento" value="Débito"> Débito</label>
<label><input type="checkbox" name="pagamento" value="Dinheiro"> Dinheiro</label>

<button>Gerar PDF</button>
</form>

<script>
let itens=[], subtotal=0;

function autoFill(){
 if(!padrao.value) return;
 let p=padrao.value.split("|");
 desc.value=p[0]; val.value=p[1];
}

function add(){
 let q=+qtd.value, v=+val.value;
 if(!desc.value||q<=0||v<=0) return;
 let t=q*v;
 itens.push({descricao:desc.value,qtd:q,valor:v,total:t});
 subtotal+=t;
 let r=tab.insertRow();
 r.insertCell(0).innerText=desc.value;
 r.insertCell(1).innerText=q;
 r.insertCell(2).innerText=v.toFixed(2);
 r.insertCell(3).innerText=t.toFixed(2);
 calc();
}

function calc(){
 subtotalInput = document.getElementById("subtotal");
 totalInput = document.getElementById("total");
 subtotalInput.value=subtotal.toFixed(2);
 totalInput.value=(subtotal-(+desconto.value||0)).toFixed(2);
 document.getElementById("itens").value=JSON.stringify(itens);
}
</script>

</body>
</html>
""", servicos=SERVICOS_PADRAO)

app.run(host="0.0.0.0", port=10000)
