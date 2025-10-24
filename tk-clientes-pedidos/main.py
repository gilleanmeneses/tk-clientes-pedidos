import tkinter as tk
from tkinter import ttk
from db import inicializar_db
from views.clientes_view import ClientesView
from views.pedidos_view import PedidoForm
from views.pedidos_list_view import PedidosListView

def main():
    inicializar_db()

    root = tk.Tk()
    root.title("Gestão de Clientes e Pedidos")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)

    tab_clientes = ClientesView(notebook)
    tab_pedidos = PedidosListView(notebook)

    notebook.add(tab_clientes, text="Clientes")
    notebook.add(tab_pedidos, text="Pedidos")
    notebook.pack(fill="both", expand=True)

    ttk.Button(root, text="Novo Pedido", command=lambda: PedidoForm(root, callback=tab_pedidos.refresh)).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()