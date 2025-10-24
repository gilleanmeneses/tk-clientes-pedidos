import tkinter as tk
from tkinter import ttk, messagebox
from models import Pedido, Cliente, ItemPedido

class PedidosListView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # Barra de busca
        frame_top = ttk.Frame(self)
        frame_top.pack(fill="x", pady=5)
        ttk.Label(frame_top, text="Buscar por cliente/data:").pack(side="left", padx=5)
        self.entry_busca = ttk.Entry(frame_top)
        self.entry_busca.pack(side="left", fill="x", expand=True)
        ttk.Button(frame_top, text="Buscar", command=self.refresh).pack(side="left", padx=5)

        # Treeview principal
        cols = ("id", "cliente", "data", "total")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, w in zip(cols, [50, 200, 120, 100]):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Botões
        frame_bottom = ttk.Frame(self)
        frame_bottom.pack(fill="x", pady=5)
        ttk.Button(frame_bottom, text="Detalhes", command=self.ver_detalhes).pack(side="left", padx=5)
        ttk.Button(frame_bottom, text="Excluir", command=self.excluir_pedido).pack(side="left", padx=5)

    def refresh(self):
        """Atualiza a lista de pedidos."""
        termo = self.entry_busca.get().lower().strip()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in Pedido.all():
            cliente = Cliente.get(p.cliente_id)
            cliente_nome = cliente.nome if cliente else "Desconhecido"
            if not termo or termo in cliente_nome.lower() or termo in p.data.lower():
                self.tree.insert("", "end", iid=p.id, values=(p.id, cliente_nome, p.data, f"R$ {p.total:.2f}"))

    def ver_detalhes(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um pedido.")
            return
        pid = int(sel[0])
        p = Pedido.get(pid)
        if not p:
            messagebox.showerror("Erro", "Pedido não encontrado.")
            return
        PedidoDetalhes(self, pedido=p)

    def excluir_pedido(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um pedido.")
            return
        pid = int(sel[0])
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este pedido?"):
            # Excluir itens antes do pedido (para integridade)
            for item in ItemPedido.by_pedido(pid):
                item.delete()
            Pedido.get(pid).delete()
            self.refresh()
            messagebox.showinfo("Sucesso", "Pedido excluído.")


class PedidoDetalhes(tk.Toplevel):
    def __init__(self, master, pedido):
        super().__init__(master)
        self.title(f"Pedido #{pedido.id}")
        self.pedido = pedido
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10, fill="both", expand=True)

        cliente = Cliente.get(self.pedido.cliente_id)
        ttk.Label(frm, text=f"Cliente: {cliente.nome if cliente else 'Desconhecido'}").pack(anchor="w")
        ttk.Label(frm, text=f"Data: {self.pedido.data}").pack(anchor="w")
        ttk.Label(frm, text=f"Total: R$ {self.pedido.total:.2f}", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)

        ttk.Separator(frm, orient="horizontal").pack(fill="x", pady=5)

        # Itens do pedido
        tree = ttk.Treeview(frm, columns=("produto", "quantidade", "preco_unit", "subtotal"), show="headings")
        for c, w in zip(tree["columns"], [150, 80, 80, 100]):
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=w, anchor="center")
        tree.pack(fill="both", expand=True, pady=5)

        for item in self.pedido.get_itens():
            tree.insert("", "end", values=(item.produto, item.quantidade, item.preco_unit, item.subtotal()))

        ttk.Button(frm, text="Fechar", command=self.destroy).pack(pady=10)