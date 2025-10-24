import tkinter as tk
from tkinter import ttk, messagebox
from models import Cliente

class ClientesView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # Campo de busca
        frame_top = ttk.Frame(self)
        frame_top.pack(fill="x", pady=5)
        ttk.Label(frame_top, text="Buscar:").pack(side="left", padx=5)
        self.entry_busca = ttk.Entry(frame_top)
        self.entry_busca.pack(side="left", fill="x", expand=True)
        ttk.Button(frame_top, text="Buscar", command=self.refresh).pack(side="left", padx=5)

        # Treeview
        self.tree = ttk.Treeview(self, columns=("nome", "email", "telefone"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Botões
        frame_bottom = ttk.Frame(self)
        frame_bottom.pack(fill="x", pady=5)
        ttk.Button(frame_bottom, text="Novo", command=self.novo_cliente).pack(side="left", padx=5)
        ttk.Button(frame_bottom, text="Editar", command=self.editar_cliente).pack(side="left", padx=5)
        ttk.Button(frame_bottom, text="Excluir", command=self.excluir_cliente).pack(side="left", padx=5)

    def refresh(self):
        """Recarrega a lista de clientes com base na busca."""
        termo = self.entry_busca.get().lower().strip()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for c in Cliente.all():
            if not termo or termo in c.nome.lower() or termo in (c.email or "").lower():
                self.tree.insert("", "end", iid=c.id, values=(c.nome, c.email, c.telefone))

    # --------------------------------------------------------
    # Ações
    # --------------------------------------------------------
    def novo_cliente(self):
        ClienteForm(self, callback=self.refresh)

    def editar_cliente(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um cliente para editar.")
            return
        cid = int(sel[0])
        ClienteForm(self, cliente=Cliente.get(cid), callback=self.refresh)

    def excluir_cliente(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um cliente para excluir.")
            return
        cid = int(sel[0])
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este cliente?"):
            c = Cliente.get(cid)
            if c:
                c.delete()
            self.refresh()


class ClienteForm(tk.Toplevel):
    def __init__(self, master, cliente=None, callback=None):
        super().__init__(master)
        self.title("Cliente")
        self.cliente = cliente
        self.callback = callback
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_cancelar)

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10)

        self.vars = {f: tk.StringVar() for f in ["nome", "email", "telefone"]}
        if self.cliente:
            for f in self.vars:
                self.vars[f].set(getattr(self.cliente, f))

        for i, (label, var) in enumerate(self.vars.items()):
            ttk.Label(frm, text=label.capitalize()+":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            ttk.Entry(frm, textvariable=var, width=30).grid(row=i, column=1, padx=5, pady=5)

        ttk.Button(frm, text="Salvar", command=self.on_salvar).grid(row=3, column=0, pady=10)
        ttk.Button(frm, text="Cancelar", command=self.on_cancelar).grid(row=3, column=1, pady=10)

    def validar(self):
        nome = self.vars["nome"].get().strip()
        email = self.vars["email"].get().strip()
        telefone = self.vars["telefone"].get().strip()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório.")
            return False
        if email and "@" not in email:
            messagebox.showerror("Erro", "E-mail inválido.")
            return False
        if telefone and not telefone.isdigit():
            messagebox.showerror("Erro", "Telefone deve conter apenas dígitos.")
            return False
        return True

    def on_salvar(self):
        if not self.validar():
            return
        dados = {f: self.vars[f].get().strip() for f in self.vars}
        if self.cliente:
            for k, v in dados.items():
                setattr(self.cliente, k, v)
        else:
            self.cliente = Cliente(**dados)
        self.cliente.save()
        if self.callback:
            self.callback()
        self.destroy()

    def on_cancelar(self):
        if messagebox.askyesno("Cancelar", "Deseja cancelar sem salvar?"):
            self.destroy()
