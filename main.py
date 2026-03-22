from flask import Flask, render_template_string, request, send_file, session, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import date
from io import BytesIO
import os, json

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_qualquer"

SENHA = "josevaldo123"
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

def f(v):
    try: return float(v)
    except: return 0.0

# ================= PDF =================
def gerar_pdf(d, itens):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    if os.path.exists("static/logo.jpeg"):
        c.drawImage("static/logo.jpeg", 40, 780, 120, 50)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(170, 800, "ORÇAMENTO JVSN-VALDO")

    c.setFont("Helvetica", 10)
    c.drawString(170, 782, "Email: valdo.soares@jvsn.com.br")
    c.drawString(170, 768, "Telefone: (11) 92173 3556")

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
    c.drawString(360, y, f"Desconto: {d['desconto']}%")
    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(360, y, f"TOTAL: R$ {d['total']:.2f}")

    c.save()
    buffer.seek(0)
    return buffer

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form.get("senha") == SENHA:
            session["logado"] = True
            return redirect("/")
    return '''
    <h2>Login</h2>
    <form method="post">
    <input type="password" name="senha" placeholder="Senha">
    <button>Entrar</button>
    </form>
    '''

# ================= APP =================
@app.route("/", methods=["GET","POST"])
def index():
    if not session.get("logado"):
        return redirect("/login")

    if request.method == "POST":
        itens = json.loads(request.form.get("itens","[]"))

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

        return send_file(
            gerar_pdf(d, itens),
            as_attachment=True,
            download_name="orcamento.pdf",
            mimetype="application/pdf"
        )

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body{
  font-family:Arial;
  background:#0f172a;
  padding:10px;
  margin:0;
  color:#fff;
}

h2{text-align:center}

form{
  background:#1e293b;
  padding:15px;
  border-radius:10px;
}

input,select{
  width:100%;
  padding:12px;
  margin:6px 0;
  border:none;
  border-radius:6px;
  font-size:16px;
}

button{
  width:100%;
  padding:12px;
  margin-top:8px;
  border:none;
  border-radius:8px;
  background:#22c55e;
  color:#fff;
  font-size:16px;
  font-weight:bold;
}

table{
  width:100%;
  margin-top:10px;
  font-size:14px;
}

td{padding:6px}

table button{background:#ef4444}
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

<input id="subtotal" name="subtotal" readonly placeholder="Subtotal">
<input id="desconto" name="desconto" value="0" oninput="calc()" placeholder="Desconto (%)">
<input id="total" name="total" readonly placeholder="Total">

<label><input type="checkbox" name="pagamento" value="Pix"> Pix</label>
<label><input type="checkbox" name="pagamento" value="Crédito"> Crédito</label>
<label><input type="checkbox" name="pagamento" value="Débito"> Débito</label>
<label><input type="checkbox" name="pagamento" value="Dinheiro"> Dinheiro</label>

<button>Gerar PDF</button>
</form>

<script>
let itens = [];
let subtotal = 0;

function autoFill(){
 if(!padrao.value) return;
 let p = padrao.value.split("|");
 desc.value = p[0];
 val.value = p[1];
}

function add(){
 let q = +qtd.value, v = +val.value;
 if(!desc.value || q<=0 || v<=0) return;

 let t = q*v;
 itens.push({descricao:desc.value,qtd:q,valor:v,total:t});

 renderTabela();
}

function remover(i){
 itens.splice(i,1);
 renderTabela();
}

function renderTabela(){
 subtotal = 0;
 tab.innerHTML = "";

 itens.forEach((item,i)=>{
   subtotal += item.total;

   let r = tab.insertRow();
   r.insertCell(0).innerText = item.descricao;
   r.insertCell(1).innerText = item.qtd;
   r.insertCell(2).innerText = item.valor.toFixed(2);
   r.insertCell(3).innerText = item.total.toFixed(2);

   let btn = document.createElement("button");
   btn.innerText = "❌";
   btn.onclick = ()=> remover(i);

   r.insertCell(4).appendChild(btn);
 });

 calc();
}

function calc(){
 let descontoPercent = +document.getElementById("desconto").value || 0;
 let valorDesconto = subtotal * (descontoPercent / 100);

 document.getElementById("subtotal").value = subtotal.toFixed(2);
 document.getElementById("total").value = (subtotal - valorDesconto).toFixed(2);

 document.getElementById("itens").value = JSON.stringify(itens);
}
</script>

</body>
</html>
""", servicos=SERVICOS_PADRAO)

app.run(host="0.0.0.0", port=10000)
