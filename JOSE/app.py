from flask import Flask, render_template_string, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from datetime import date
import os
import uuid

app = Flask(__name__)

# ======================
# TABELA PADRÃO
# ======================
SERVICOS_PADRAO = {
    "Troca de tomada": 80,
    "Troca de interruptor": 70,
    "Instalação de disjuntor": 150,
    "Instalação de luminária": 120,
    "Revisão elétrica": 250,
    "Troca de fiação": 300,
    "Manutenção predial": 400
}

# ======================
# HTML (INLINE)
# ======================
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Orçamento Elétrico</title>
<style>
body{font-family:Arial;background:#f4f4f4;padding:20px}
form{background:#fff;padding:20px;border-radius:6px}
label{display:block;margin-top:10px}
input,select,button{width:100%;padding:8px;margin-top:5px}
table{width:100%;border-collapse:collapse;margin-top:10px}
th,td{border:1px solid #ccc;padding:6px;text-align:center}
button{background:#ff9800;color:#fff;font-weight:bold;border:none;margin-top:15px}
</style>
</head>
<body>

<h2>⚡ Orçamento Manutenção Elétrica</h2>

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

<button type="button" onclick="add()">Adicionar</button>

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
<select name="pagamento">
<option>Pix</option>
<option>Cartão de Crédito</option>
<option>Cartão de Débito</option>
<option>Dinheiro</option>
</select>

<button type="submit">Gerar PDF</button>

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
 total.value=(subtotal - Number(desconto.value)).toFixed(2);
}

function itensField(){
 document.getElementById("itens").value=JSON.stringify(itens);
}
</script>

</body>
</html>
"""

# ======================
# PDF
# ======================
def gerar_pdf(dados, itens):
    nome = f"orcamento_{uuid.uuid4().hex}.pdf"
    c = canvas.Canvas(nome, pagesize=A4)

    AZUL = HexColor("#0D47A1")
    LARANJA = HexColor("#FF9800")
    CINZA = HexColor("#555555")

    if os.path.exists("static/logo.png"):
        c.drawImage("static/logo.png", 40, 770, 100, 50, mask='auto')

    c.setFont("Helvetica-Bold",18)
    c.setFillColor(AZUL)
    c.drawString(160,800,"ORÇAMENTO ELÉTRICO")

    c.setStrokeColor(LARANJA)
    c.setLineWidth(3)
    c.line(40,760,550,760)

    c.setFont("Helvetica",11)
    c.setFillColor(CINZA)
    c.drawString(40,730,f"Cliente: {dados['cliente']}")
    c.drawString(40,710,f"Telefone: {dados['telefone']}")
    c.drawString(40,690,f"Tipo: {dados['tipo']}")
    c.drawString(400,730,f"Data: {dados['data']}")

    y=650
    c.setFont("Helvetica-Bold",11)
    c.drawString(40,y,"Serviço")
    c.drawString(300,y,"Qtd")
    c.drawString(360,y,"Valor")
    c.drawString(450,y,"Total")
    c.line(40,y-5,550,y-5)

    y-=20
    c.setFont("Helvetica",11)
    for i in itens:
        c.drawString(40,y,i["descricao"])
        c.drawString(310,y,str(i["qtd"]))
        c.drawString(360,y,f"R$ {i['valor']:.2f}")
        c.drawString(450,y,f"R$ {i['total']:.2f}")
        y-=18

    y-=20
    c.setFont("Helvetica-Bold",12)
    c.setFillColor(AZUL)
    c.drawString(360,y,"Subtotal:")
    c.drawString(450,y,f"R$ {dados['subtotal']:.2f}")

    y-=20
    c.drawString(360,y,"Desconto:")
    c.drawString(450,y,f"R$ {dados['desconto']:.2f}")

    y-=25
    c.setFont("Helvetica-Bold",14)
    c.setFillColor(LARANJA)
    c.drawString(360,y,"TOTAL:")
    c.drawString(450,y,f"R$ {dados['total']:.2f}")

    y-=40
    c.setFont("Helvetica",11)
    c.setFillColor(CINZA)
    c.drawString(40,y,f"Pagamento: {dados['pagamento']}")

    c.setStrokeColor(LARANJA)
    c.line(40,80,550,80)
    c.setFont("Helvetica-Oblique",9)
    c.drawString(40,60,"Validade do orçamento: 7 dias")

    c.save()
    return nome

# ======================
# ROTAS
# ======================
def to_float(valor):
    try:
        return float(valor)
    except:
        return 0.0


@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        import json

        itens_json = request.form.get("itens", "[]")
        itens = json.loads(itens_json)

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

    return render_template_string(HTML, servicos=SERVICOS_PADRAO)

if __name__=="__main__":
    app.run(debug=True)
