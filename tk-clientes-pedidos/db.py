import sqlite3
from sqlite3 import Error

DB_NAME = "clientes_pedidos.db"

def conectar():
    """Abre conexão com o banco SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except Error as e:
        print("Erro ao conectar ao banco:", e)
        return None

def inicializar_db():
    """Cria as tabelas necessárias, se não existirem."""
    conn = conectar()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT,
                telefone TEXT
            );

            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                data TEXT,
                total REAL,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            );

            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                produto TEXT,
                quantidade INTEGER,
                preco_unit REAL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
            );
        """)
        conn.commit()
    except Error as e:
        print("Erro ao criar tabelas:", e)
    finally:
        conn.close()

def executar(sql, params=(), fetch=False):
    """
    Executa comandos SQL parametrizados.
    Retorna:
      - resultado (fetch=True)
      - id do último registro inserido (fetch=False)
    """
    conn = conectar()
    if not conn:
        return None

    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        if fetch:
            result = cur.fetchall()
        else:
            result = cur.lastrowid
        return result
    except Error as e:
        print("Erro SQL:", e)
        return None
    finally:
        conn.close()