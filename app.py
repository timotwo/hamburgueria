from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

from flask import Flask, render_template, request, redirect, session, jsonify, flash
from supabase import create_client
from functools import wraps
from datetime import datetime, date

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = "hamburgueria_rf7_vendas_burger_2026"
app.config["UPLOAD_FOLDER"] = "uploads"

 
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated
 
def nivel_required(*niveis):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("nivel_acesso") not in niveis:
                flash("Acesso negado.", "danger")
                return redirect("/")
            return f(*args, **kwargs)
        return decorated
    return decorator



 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        res = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("senha", senha).eq("ativo", True).execute()
        if res.data:
            u = res.data[0]
            session["usuario_id"] = u["id"]
            session["usuario_nome"] = u["nome"]
            session["nivel_acesso"] = u["nivel_acesso"]
            return redirect("/")
        flash("Usuário ou senha inválidos.", "danger")
    return render_template("login.html")
 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
 
@app.route("/")
@login_required
def home():
    return redirect("/pedidos")
 



@app.route("/usuarios")
@login_required
@nivel_required("ADMINISTRADOR")
def usuarios():
    users = supabase.table("usuarios").select("*").order("nome").execute().data
    return render_template("usuarios.html", usuarios=users)
 
@app.route("/usuarios/adicionar", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR")
def adicionar_usuario():
    supabase.table("usuarios").insert({
        "nome": request.form["nome"],
        "cpf": request.form["cpf"],
        "data_nascimento": request.form["data_nascimento"],
        "usuario": request.form["usuario"],
        "senha": "H@mburger123",
        "nivel_acesso": request.form["nivel_acesso"],
        "ativo": True
    }).execute()
    flash("Usuário cadastrado com sucesso!", "success")
    return redirect("/usuarios")
 
@app.route("/usuarios/editar/<int:id>")
@login_required
@nivel_required("ADMINISTRADOR")
def editar_usuario(id):
    u = supabase.table("usuarios").select("*").eq("id", id).execute().data[0]
    users = supabase.table("usuarios").select("*").order("nome").execute().data
    return render_template("usuarios.html", usuario=u, usuarios=users)
 
@app.route("/usuarios/atualizar/<int:id>", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR")
def atualizar_usuario(id):
    supabase.table("usuarios").update({
        "nome": request.form["nome"],
        "cpf": request.form["cpf"],
        "data_nascimento": request.form["data_nascimento"],
        "usuario": request.form["usuario"],
        "nivel_acesso": request.form["nivel_acesso"]
    }).eq("id", id).execute()
    flash("Usuário atualizado!", "success")
    return redirect("/usuarios")
 
@app.route("/usuarios/excluir/<int:id>")
@login_required
@nivel_required("ADMINISTRADOR")
def excluir_usuario(id):
    supabase.table("usuarios").update({"ativo": False}).eq("id", id).execute()
    flash("Usuário removido.", "success")
    return redirect("/usuarios")
 


@app.route("/categorias")
@login_required
@nivel_required("ADMINISTRADOR")
def categorias():
    cats = supabase.table("categorias").select("*").execute().data
    return render_template("categorias.html", categorias=cats)
 
@app.route("/categorias/adicionar", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR")
def adicionar_categoria():
    supabase.table("categorias").insert({
        "nome": request.form["nome"],
        "descricao": request.form["descricao"]
    }).execute()
    flash("Categoria adicionada!", "success")
    return redirect("/categorias")
 
@app.route("/categorias/editar/<int:id>")
@login_required
@nivel_required("ADMINISTRADOR")
def editar_categoria(id):
    cat = supabase.table("categorias").select("*").eq("id_categoria", id).execute().data[0]
    cats = supabase.table("categorias").select("*").execute().data
    return render_template("categorias.html", categoria=cat, categorias=cats)
 
@app.route("/categorias/atualizar/<int:id>", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR")
def atualizar_categoria(id):
    supabase.table("categorias").update({
        "nome": request.form["nome"],
        "descricao": request.form["descricao"]
    }).eq("id_categoria", id).execute()
    flash("Categoria atualizada!", "success")
    return redirect("/categorias")
 
@app.route("/categorias/excluir/<int:id>")
@login_required
@nivel_required("ADMINISTRADOR")
def excluir_categoria(id):
    supabase.table("categorias").delete().eq("id_categoria", id).execute()
    flash("Categoria removida.", "success")
    return redirect("/categorias")
 


@app.route("/produtos")
@login_required
@nivel_required("ADMINISTRADOR")
def produtos():
    prods = supabase.table("produtos").select("*, categorias(nome)").execute().data
    cats = supabase.table("categorias").select("*").execute().data
    return render_template("produtos.html", produtos=prods, categorias=cats)
 
@app.route("/produtos/adicionar", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR")
def adicionar_produto():
    foto = request.files.get("foto")
    nome_foto = ""
    if foto and foto.filename:
        nome_foto = foto.filename
        foto.save(os.path.join(app.config["UPLOAD_FOLDER"], nome_foto))
 
    supabase.table("produtos").insert({
        "nome": request.form["nome"],
        "descricao": request.form["descricao"],
        "preco": request.form["preco"],
        "id_categoria": request.form["id_categoria"],
        "foto": nome_foto,
        "data_cadastro": datetime.now().isoformat()
    }).execute()
    flash("Produto adicionado!", "success")
    return redirect("/produtos")
 
@app.route("/produtos/editar/<int:id>")
@login_required
@nivel_required("ADMINISTRADOR")
def editar_produto(id):
    produto = supabase.table("produtos").select("*").eq("id_produto", id).execute().data[0]
    prods = supabase.table("produtos").select("*, categorias(nome)").execute().data
    cats = supabase.table("categorias").select("*").execute().data
    return render_template("produtos.html", produto=produto, produtos=prods, categorias=cats)
 
@app.route("/produtos/atualizar/<int:id>", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR")
def atualizar_produto(id):
    supabase.table("produtos").update({
        "nome": request.form["nome"],
        "descricao": request.form["descricao"],
        "preco": request.form["preco"],
        "id_categoria": request.form["id_categoria"]
    }).eq("id_produto", id).execute()
    flash("Produto atualizado!", "success")
    return redirect("/produtos")
 
@app.route("/produtos/excluir/<int:id>")
@login_required
@nivel_required("ADMINISTRADOR")
def excluir_produto(id):
    supabase.table("produtos").delete().eq("id_produto", id).execute()
    flash("Produto removido.", "success")
    return redirect("/produtos")

 
@app.route("/clientes")
@login_required
@nivel_required("ADMINISTRADOR")
def clientes():
    cls = supabase.table("clientes").select("*").execute().data
    return render_template("clientes.html", clientes=cls)
 
@app.route("/clientes/adicionar", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR")
def adicionar_cliente():
    supabase.table("clientes").insert({
        "nome": request.form["nome"],
        "telefone": request.form["telefone"],
        "endereco": request.form["endereco"]
    }).execute()
    flash("Cliente adicionado!", "success")
    return redirect("/clientes")
 
@app.route("/clientes/editar/<int:id>")
@login_required
@nivel_required("ADMINISTRADOR")
def editar_cliente(id):
    cliente = supabase.table("clientes").select("*").eq("id", id).execute().data[0]
    cls = supabase.table("clientes").select("*").execute().data
    return render_template("clientes.html", cliente=cliente, clientes=cls)
 
@app.route("/clientes/atualizar/<int:id>", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR")
def atualizar_cliente(id):
    supabase.table("clientes").update({
        "nome": request.form["nome"],
        "telefone": request.form["telefone"],
        "endereco": request.form["endereco"]
    }).eq("id", id).execute()
    flash("Cliente atualizado!", "success")
    return redirect("/clientes")
 
@app.route("/clientes/excluir/<int:id>")
@login_required
@nivel_required("ADMINISTRADOR")
def excluir_cliente(id):
    supabase.table("clientes").delete().eq("id", id).execute()
    flash("Cliente removido.", "success")
    return redirect("/clientes")

 
@app.route("/pedidos")
@login_required
def pedidos():
    nivel = session.get("nivel_acesso")
    todos = supabase.table("pedidos").select("*, clientes(nome)").order("data_pedido", desc=True).execute().data
 
    if nivel == "CHAPISTA":
        todos = [p for p in todos if p["status_pedido"] in ("CADASTRADO", "EM_PRODUCAO")]
    elif nivel == "ENTREGADOR":
        todos = [p for p in todos if p["status_pedido"] in ("PRONTO", "SAIU_ENTREGA", "ENTREGUE") and p["tipo_pedido"] == "DELIVERY"]
 
    
    filtro_num = request.args.get("numero")
    filtro_tipo = request.args.get("tipo")
    filtro_status = request.args.get("status")
    filtro_mesa = request.args.get("mesa")
    filtro_cliente = request.args.get("cliente")
    filtro_data = request.args.get("data")
 
    if filtro_num:
        todos = [p for p in todos if str(p["id"]) == filtro_num]
    if filtro_tipo:
        todos = [p for p in todos if p["tipo_pedido"] == filtro_tipo]
    if filtro_status:
        todos = [p for p in todos if p["status_pedido"] == filtro_status]
    if filtro_mesa:
        todos = [p for p in todos if str(p.get("numero_mesa", "")) == filtro_mesa]
    if filtro_cliente:
        todos = [p for p in todos if filtro_cliente.lower() in (p.get("clientes") or {}).get("nome", "").lower()]
    if filtro_data:
        todos = [p for p in todos if p["data_pedido"] and p["data_pedido"][:10] == filtro_data]
 
    return render_template("pedidos_lista.html", pedidos=todos)
 
@app.route("/pedidos/novo")
@login_required
@nivel_required("ADMINISTRADOR", "GARCON")
def novo_pedido():
    produtos = supabase.table("produtos").select("*, categorias(nome)").execute().data
    clientes = supabase.table("clientes").select("*").execute().data
    itens = session.get("itens_pedido", [])
    return render_template("pedidos_novo.html", produtos=produtos, clientes=clientes, itens=itens)
 
@app.route("/pedidos/adicionar-item", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR", "GARCON")
def adicionar_item():
    itens = session.get("itens_pedido", [])
    produto_id = int(request.form["produto_id"])
    produto = supabase.table("produtos").select("*").eq("id_produto", produto_id).execute().data[0]
    itens.append({
        "produto_id": produto_id,
        "produto_nome": produto["nome"],
        "preco": float(produto["preco"]),
        "quantidade": int(request.form["quantidade"]),
        "observacoes": request.form.get("observacoes", "")
    })
    session["itens_pedido"] = itens
    return redirect("/pedidos/novo")
 
@app.route("/pedidos/remover-item/<int:indice>")
@login_required
def remover_item(indice):
    itens = session.get("itens_pedido", [])
    if indice < len(itens):
        itens.pop(indice)
    session["itens_pedido"] = itens
    return redirect("/pedidos/novo")
 
@app.route("/pedidos/editar-item/<int:indice>", methods=["POST"])
@login_required
def editar_item(indice):
    itens = session.get("itens_pedido", [])
    if indice < len(itens):
        itens[indice]["quantidade"] = int(request.form["quantidade"])
        itens[indice]["observacoes"] = request.form.get("observacoes", "")
    session["itens_pedido"] = itens
    return redirect("/pedidos/novo")
 
@app.route("/pedidos/concluir", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR", "GARCON")
def concluir_pedido():
    tipo = request.form["tipo_pedido"]
    cliente_id = request.form.get("cliente_id") or None
    mesa = request.form.get("numero_mesa") or None
    taxa = request.form.get("taxa_entrega", "0") or "0"
    taxa = float(taxa.replace(",", "."))
 
    if tipo == "DELIVERY" and not cliente_id:
        flash("Cliente obrigatório para Delivery.", "danger")
        return redirect("/pedidos/novo")
    if tipo == "CONSUMO_LOCAL" and not mesa:
        flash("Mesa obrigatória para consumo local.", "danger")
        return redirect("/pedidos/novo")
 
    pedido = supabase.table("pedidos").insert({
        "tipo_pedido": tipo,
        "cliente_id": int(cliente_id) if cliente_id else None,
        "numero_mesa": int(mesa) if mesa else None,
        "taxa_entrega": taxa,
        "status_pedido": "CADASTRADO",
        "data_pedido": datetime.now().isoformat()
    }).execute()
 
    pedido_id = pedido.data[0]["id"]
    for item in session.get("itens_pedido", []):
        supabase.table("itens_pedido").insert({
            "pedido_id": pedido_id,
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "observacoes": item["observacoes"]
        }).execute()
 
    session["itens_pedido"] = []
    flash(f"Pedido #{pedido_id} cadastrado com sucesso!", "success")
    return redirect("/pedidos")
 
@app.route("/pedidos/detalhe/<int:id>")
@login_required
def detalhe_pedido(id):
    pedido = supabase.table("pedidos").select("*, clientes(nome, telefone, endereco)").eq("id", id).execute().data[0]
    itens = supabase.table("itens_pedido").select("*, produtos(nome, preco)").eq("pedido_id", id).execute().data
   
    subtotal = sum(float(i["produtos"]["preco"]) * i["quantidade"] for i in itens)
    nivel = session.get("nivel_acesso")
    return render_template("pedido_detalhe.html", pedido=pedido, itens=itens, subtotal=subtotal, nivel=nivel)
 
 
STATUS_PERMITIDOS = {
    "CHAPISTA": ["EM_PRODUCAO", "PRONTO"],
    "ENTREGADOR": ["SAIU_ENTREGA", "ENTREGUE", "RETORNADO"],
    "ADMINISTRADOR": ["CADASTRADO", "EM_PRODUCAO", "PRONTO", "SAIU_ENTREGA", "ENTREGUE", "RETORNADO"],
    "GARCON": ["CADASTRADO", "EM_PRODUCAO", "PRONTO", "SAIU_ENTREGA", "ENTREGUE", "RETORNADO"]
}
 
@app.route("/pedidos/mudar-status/<int:id>", methods=["POST"])
@login_required
def mudar_status(id):
    novo_status = request.form["status"]
    nivel = session.get("nivel_acesso")
    permitidos = STATUS_PERMITIDOS.get(nivel, [])
    if novo_status not in permitidos:
        flash("Você não pode definir esse status.", "danger")
        return redirect(f"/pedidos/detalhe/{id}")
    supabase.table("pedidos").update({"status_pedido": novo_status}).eq("id", id).execute()
    flash("Status atualizado!", "success")
    return redirect(f"/pedidos/detalhe/{id}")
 

@app.route("/pagamentos")
@login_required
@nivel_required("ADMINISTRADOR", "GARCON", "ENTREGADOR")
def pagamentos():
    nivel = session.get("nivel_acesso")
 
    pedidos = supabase.table("pedidos").select("*, clientes(nome)").execute().data
    
    pagos_ids = {p["pedido_id"] for p in supabase.table("pagamentos").select("pedido_id").execute().data}
    pendentes = [p for p in pedidos if p["id"] not in pagos_ids and p["status_pedido"] not in ("CADASTRADO", "EM_PRODUCAO", "RETORNADO")]
 
    if nivel == "GARCON":
        pendentes = [p for p in pendentes if p["tipo_pedido"] == "CONSUMO_LOCAL"]
    elif nivel == "ENTREGADOR":
        pendentes = [p for p in pendentes if p["tipo_pedido"] == "DELIVERY"]
 
    return render_template("pagamentos.html", pedidos=pendentes)
 
@app.route("/pagamentos/registrar/<int:pedido_id>")
@login_required
@nivel_required("ADMINISTRADOR", "GARCON", "ENTREGADOR")
def form_pagamento(pedido_id):
    pedido = supabase.table("pedidos").select("*, clientes(nome)").eq("id", pedido_id).execute().data[0]
    itens = supabase.table("itens_pedido").select("*, produtos(nome, preco)").eq("pedido_id", pedido_id).execute().data
    subtotal = sum(float(i["produtos"]["preco"]) * i["quantidade"] for i in itens)
    total = subtotal + float(pedido.get("taxa_entrega") or 0)
    return render_template("pagamento_form.html", pedido=pedido, itens=itens, subtotal=subtotal, total=total)
 
@app.route("/pagamentos/confirmar/<int:pedido_id>", methods=["POST"])
@login_required
@nivel_required("ADMINISTRADOR", "GARCON", "ENTREGADOR")
def confirmar_pagamento(pedido_id):
    forma = request.form["forma_pagamento"]
    pedido = supabase.table("pedidos").select("*").eq("id", pedido_id).execute().data[0]
    itens = supabase.table("itens_pedido").select("*, produtos(preco)").eq("pedido_id", pedido_id).execute().data
    subtotal = sum(float(i["produtos"]["preco"]) * i["quantidade"] for i in itens)
    taxa_entrega = float(pedido.get("taxa_entrega") or 0)
    taxa_servico = 0.0
    if pedido["tipo_pedido"] == "CONSUMO_LOCAL" and request.form.get("taxa_servico") == "on":
        taxa_servico = round(subtotal * 0.10, 2)
    valor_total = subtotal + taxa_entrega + taxa_servico
 
    supabase.table("pagamentos").insert({
        "pedido_id": pedido_id,
        "valor_total": valor_total,
        "valor_taxa_servico": taxa_servico,
        "forma_pagamento": forma,
        "data_pagamento": datetime.now().isoformat()
    }).execute()
    supabase.table("pedidos").update({"status_pedido": "ENTREGUE"}).eq("id", pedido_id).execute()
    flash(f"Pagamento do pedido #{pedido_id} registrado!", "success")
    return redirect("/pagamentos")
 

@app.route("/pagamentos/historico")
@login_required
@nivel_required("ADMINISTRADOR", "GARCON", "ENTREGADOR")
def historico_pagamentos():
    nivel = session.get("nivel_acesso")
    pags = supabase.table("pagamentos").select("*, pedidos(id, tipo_pedido, numero_mesa, cliente_id, data_pedido, clientes(nome))").order("data_pagamento", desc=True).execute().data
 
    if nivel == "GARCON":
        pags = [p for p in pags if p["pedidos"]["tipo_pedido"] == "CONSUMO_LOCAL"]
    elif nivel == "ENTREGADOR":
        pags = [p for p in pags if p["pedidos"]["tipo_pedido"] == "DELIVERY"]
 
    return render_template("pagamentos_historico.html", pagamentos=pags)
 

 
@app.route("/relatorio")
@login_required
@nivel_required("ADMINISTRADOR")
def relatorio():
    data_str = request.args.get("data", date.today().isoformat())
    pags = supabase.table("pagamentos").select("*, pedidos(id, tipo_pedido, numero_mesa, taxa_entrega, clientes(nome))").execute().data
    pags_dia = [p for p in pags if p["data_pagamento"] and p["data_pagamento"][:10] == data_str]
 
    total_geral = sum(float(p["valor_total"] or 0) - float(p["pedidos"].get("taxa_entrega") or 0) - float(p["valor_taxa_servico"] or 0) for p in pags_dia)
    entrega_lista = [p for p in pags_dia if float(p["pedidos"].get("taxa_entrega") or 0) > 0]
    total_entrega = sum(float(p["pedidos"].get("taxa_entrega") or 0) for p in entrega_lista)
    servico_lista = [p for p in pags_dia if float(p["valor_taxa_servico"] or 0) > 0]
    total_servico = sum(float(p["valor_taxa_servico"] or 0) for p in servico_lista)
 
    
    todos_pedidos = supabase.table("pedidos").select("*, clientes(nome)").execute().data
    pags_ids = {p["pedido_id"] for p in pags}
    pedidos_dia = [p for p in todos_pedidos if p.get("data_pedido", "")[:10] == data_str]
    pendentes = [p for p in pedidos_dia if p["id"] not in pags_ids]
 
    return render_template("relatorio.html",
        data=data_str,
        pagamentos=pags_dia,
        total_geral=total_geral,
        entrega_lista=entrega_lista,
        total_entrega=total_entrega,
        servico_lista=servico_lista,
        total_servico=total_servico,
        pendentes=pendentes
    )
 

@app.route("/cardapio")
def cardapio():
    cats = supabase.table("categorias").select("*").execute().data
    prods = supabase.table("produtos").select("*, categorias(nome)").execute().data
    por_categoria = {}
    for cat in cats:
        por_categoria[cat["id_categoria"]] = {"nome": cat["nome"], "produtos": []}
    for p in prods:
        cid = p["id_categoria"]
        if cid in por_categoria:
            por_categoria[cid]["produtos"].append(p)
    return render_template("cardapio.html", categorias=por_categoria)
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)