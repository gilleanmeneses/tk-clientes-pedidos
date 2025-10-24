from db import executar
from datetime import date

class BaseModel:
    """Classe base com operações CRUD genéricas."""
    table_name = ""
    fields = []

    def __init__(self, **kwargs):
        for f in self.fields + ["id"]:
            setattr(self, f, kwargs.get(f))

    # ---------- CRUD genéricos ----------
    @classmethod
    def all(cls):
        """Retorna todos os registros."""
        rows = executar(f"SELECT id, {', '.join(cls.fields)} FROM {cls.table_name}", fetch=True)
        return [cls(id=r[0], **dict(zip(cls.fields, r[1:]))) for r in rows] if rows else []

    @classmethod
    def get(cls, _id):
        """Busca um registro pelo ID."""
        row = executar(f"SELECT id, {', '.join(cls.fields)} FROM {cls.table_name} WHERE id = ?", (_id,), fetch=True)
        if row:
            r = row[0]
            return cls(id=r[0], **dict(zip(cls.fields, r[1:])))
        return None

    def save(self):
        """Insere ou atualiza conforme o caso."""
        if getattr(self, "id", None):  # UPDATE
            sets = ", ".join([f"{f}=?" for f in self.fields])
            values = [getattr(self, f) for f in self.fields] + [self.id]
            executar(f"UPDATE {self.table_name} SET {sets} WHERE id=?", values)
        else:  # INSERT
            cols = ", ".join(self.fields)
            qmarks = ", ".join(["?"] * len(self.fields))
            values = [getattr(self, f) for f in self.fields]
            self.id = executar(f"INSERT INTO {self.table_name} ({cols}) VALUES ({qmarks})", values)

    def delete(self):
        """Exclui o registro atual."""
        if getattr(self, "id", None):
            executar(f"DELETE FROM {self.table_name} WHERE id=?", (self.id,))

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"

# -------------------------------------------------------------------
# 👥 Modelo de Cliente
# -------------------------------------------------------------------
class Cliente(BaseModel):
    table_name = "clientes"
    fields = ["nome", "email", "telefone"]

    def __str__(self):
        return f"{self.nome} ({self.email or 'sem email'})"

# -------------------------------------------------------------------
# 📦 Modelo de Pedido
# -------------------------------------------------------------------
class Pedido(BaseModel):
    table_name = "pedidos"
    fields = ["cliente_id", "data", "total"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.data:
            self.data = date.today().isoformat()

    def get_cliente(self):
        """Retorna o cliente associado a este pedido."""
        from models import Cliente  # import local para evitar referência circular
        return Cliente.get(self.cliente_id)

    def get_itens(self):
        """Retorna lista de itens vinculados a este pedido."""
        return ItemPedido.by_pedido(self.id)

    def calcular_total(self):
        """Recalcula o total com base nos itens."""
        itens = self.get_itens()
        total = sum(i.quantidade * i.preco_unit for i in itens)
        self.total = round(total, 2)
        self.save()
        return total

# -------------------------------------------------------------------
# 🧾 Modelo de Item de Pedido
# -------------------------------------------------------------------
class ItemPedido(BaseModel):
    table_name = "itens_pedido"
    fields = ["pedido_id", "produto", "quantidade", "preco_unit"]

    @classmethod
    def by_pedido(cls, pedido_id):
        """Lista todos os itens de um pedido específico."""
        rows = executar(
            f"SELECT id, {', '.join(cls.fields)} FROM {cls.table_name} WHERE pedido_id = ?",
            (pedido_id,), fetch=True
        )
        return [cls(id=r[0], **dict(zip(cls.fields, r[1:]))) for r in rows] if rows else []

    def subtotal(self):
        """Retorna o subtotal deste item (quantidade * preço_unit)."""
        return round(self.quantidade * self.preco_unit, 2)