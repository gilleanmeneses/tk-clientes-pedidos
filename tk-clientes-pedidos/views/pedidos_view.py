import tkinter as tk
from tkinter import ttk, messagebox
from models import Cliente, Pedido, ItemPedido
from datetime import date

class PedidoForm(tk.Toplevel):
    def __init__(self, master, callback=None):
        super().__init__(master)
        self.title("Novo Pedido")
        self.callback = callback
        self.pedido = None
        self.itens = []
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_cancelar)

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10, fill="both", expand=True)

        ttk.Label(frm, text="Cliente:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.combo_cliente = ttk.Combobox(frm, state="readonly",
            values=[f"{c.id} - {c.nome}" for c in Cliente.all()])
        self.combo_cliente.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frm, text="Data:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_data = ttk.Entry(frm)
        self.entry_data.insert(0, date.today().isoformat())
        self.entry_data.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Tabela de itens
        self.tree = ttk.Treeview(frm, columns=("produto", "quantidade", "preco", "subtotal"), show="headings")
        for col, w in zip(self.tree["columns"], [150, 80, 80, 100]):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=w, anchor="center")
        self.tree.grid(row=2, column=0, columnspan=3, pady=5)

        # Campos para adicionar item
        ttk.Label(frm, text="Produto:").grid(row=3, column=0)
        self.entry_produto = ttk.Entry(frm)
        self.entry_produto.grid(row=3, column=1)

        ttk.Label(frm, text="Qtd:").grid(row=4, column=0)
        self.entry_qtd = ttk.Entry(frm, width=5)
        self.entry_qtd.grid(row=4, column=1, sticky="w")

        ttk.Label(frm, text="Preço:").grid(row=5, column=0)
        self.entry_preco = ttk.Entry(frm, width=10)
        self.entry_preco.grid(row=5, column=1, sticky="w")

        ttk.Button(frm, text="Adicionar Item", command=self.adicionar_item).grid(row=6, column=1, sticky="w", pady=5)
        ttk.Button(frm, text="Remover Selecionado", command=self.remover_item).grid(row=6, column=2, padx=5)

        # Total
        self.lbl_total = ttk.Label(frm, text="Total: R$ 0,00", font=("Arial", 11, "bold"))
        self.lbl_total.grid(row=7, column=0, columnspan=3, pady=10)

        # Botões finais
        ttk.Button(frm, text="Salvar Pedido", command=self.on_salvar).grid(row=8, column=0, pady=10)
        ttk.Button(frm, text="Cancelar", command=self.on_cancelar).grid(row=8, column=1, pady=10)

    def adicionar_item(self):
        try:
            prod = self.entry_produto.get().strip()
            qtd = int(self.entry_qtd.get())
            preco = float(self.entry_preco.get())
        except ValueError:
            messagebox.showerror("Erro", "Preencha os campos corretamente.")
            return
        if not prod:
            messagebox.showerror("Erro", "Produto obrigatório.")
            return
        subtotal = qtd * preco
        self.itens.append((prod, qtd, preco))
        self.tree.insert("", "end", values=(prod, qtd, preco, subtotal))
        self.atualizar_total()
        self.entry_produto.delete(0, "end")
        self.entry_qtd.delete(0, "end")
        self.entry_preco.delete(0, "end")

    def remover_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        self.tree.delete(sel[0])
        del self.itens[idx]
        self.atualizar_total()

    def atualizar_total(self):
        total = sum(q * p for _, q, p in self.itens)
        self.lbl_total["text"] = f"Total: R$ {total:.2f}"

    def on_salvar(self):
        if not self.combo_cliente.get():
            messagebox.showerror("Erro", "Selecione um cliente.")
            return
        cliente_id = int(self.combo_cliente.get().split(" - ")[0])
        data = self.entry_data.get().strip()

        self.pedido = Pedido(cliente_id=cliente_id, data=data, total=0)
        self.pedido.save()

        for prod, qtd, preco in self.itens:
            ItemPedido(pedido_id=self.pedido.id, produto=prod, quantidade=qtd, preco_unit=preco).save()

        self.pedido.calcular_total()
        messagebox.showinfo("Sucesso", "Pedido salvo com sucesso!")
        if self.callback:
            self.callback()
        self.destroy()

    def on_cancelar(self):
        if messagebox.askyesno("Cancelar", "Deseja sair sem salvar o pedido?"):
            self.destroy()