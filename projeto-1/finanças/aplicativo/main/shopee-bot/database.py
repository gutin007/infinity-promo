import sqlite3
from datetime import datetime
from config import DB_NAME


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id TEXT,
            titulo TEXT NOT NULL,
            url_original TEXT NOT NULL,
            url_afiliado TEXT,
            preco_original REAL,
            preco_desconto REAL,
            porcentagem_desconto REAL,
            imagem_url TEXT,
            especificacoes TEXT,
            categoria TEXT,
            vendedor TEXT,
            avaliacoes REAL,
            vendidos INTEGER,
            localizacao TEXT,
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            preco REAL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_produtos_categoria 
        ON produtos(categoria)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_produtos_data 
        ON produtos(data_coleta)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_produtos_produto_id 
        ON produtos(produto_id)
    """)

    conn.commit()
    conn.close()


def inserir_produto(produto):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO produtos (
                produto_id, titulo, url_original, url_afiliado, preco_original,
                preco_desconto, porcentagem_desconto, imagem_url, especificacoes,
                categoria, vendedor, avaliacoes, vendidos, localizacao, data_coleta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            produto.get("produto_id", ""),
            produto["titulo"],
            produto["url_original"],
            produto.get("url_afiliado", ""),
            produto.get("preco_original"),
            produto.get("preco_desconto"),
            produto.get("porcentagem_desconto"),
            produto.get("imagem_url", ""),
            produto.get("especificacoes", ""),
            produto.get("categoria", "geral"),
            produto.get("vendedor", ""),
            produto.get("avaliacoes"),
            produto.get("vendidos"),
            produto.get("localizacao", ""),
            produto.get("data_coleta", datetime.now().isoformat())
        ))

        produto_db_id = cursor.lastrowid

        if produto.get("preco_desconto"):
            cursor.execute("""
                INSERT INTO historico_precos (produto_id, preco)
                VALUES (?, ?)
            """, (produto_db_id, produto["preco_desconto"]))

        conn.commit()
        return produto_db_id

    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def inserir_produtos_em_lote(produtos):
    conn = get_connection()
    cursor = conn.cursor()
    inseridos = 0

    try:
        for produto in produtos:
            try:
                cursor.execute("""
                    INSERT INTO produtos (
                        produto_id, titulo, url_original, url_afiliado, preco_original,
                        preco_desconto, porcentagem_desconto, imagem_url, especificacoes,
                        categoria, vendedor, avaliacoes, vendidos, localizacao, data_coleta
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    produto.get("produto_id", ""),
                    produto["titulo"],
                    produto["url_original"],
                    produto.get("url_afiliado", ""),
                    produto.get("preco_original"),
                    produto.get("preco_desconto"),
                    produto.get("porcentagem_desconto"),
                    produto.get("imagem_url", ""),
                    produto.get("especificacoes", ""),
                    produto.get("categoria", "geral"),
                    produto.get("vendedor", ""),
                    produto.get("avaliacoes"),
                    produto.get("vendidos"),
                    produto.get("localizacao", ""),
                    produto.get("data_coleta", datetime.now().isoformat())
                ))

                produto_db_id = cursor.lastrowid

                if produto.get("preco_desconto"):
                    cursor.execute("""
                        INSERT INTO historico_precos (produto_id, preco)
                        VALUES (?, ?)
                    """, (produto_db_id, produto["preco_desconto"]))

                inseridos += 1
            except sqlite3.Error:
                continue

        conn.commit()
        return inseridos

    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def buscar_todas_promocoes(limite=100):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM produtos 
        ORDER BY data_coleta DESC 
        LIMIT ?
    """, (limite,))

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultados


def buscar_por_categoria(categoria, limite=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM produtos 
        WHERE categoria = ?
        ORDER BY data_coleta DESC 
        LIMIT ?
    """, (categoria, limite))

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultados


def buscar_maior_desconto(limite=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM produtos 
        WHERE porcentagem_desconto IS NOT NULL
        ORDER BY porcentagem_desconto DESC 
        LIMIT ?
    """, (limite,))

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultados


def contar_por_categoria():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT categoria, COUNT(*) as total 
        FROM produtos 
        GROUP BY categoria 
        ORDER BY total DESC
    """)

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultados


def limpar_produtos_antigos(dias=7):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM produtos 
        WHERE data_coleta < datetime('now', ? || ' days')
    """, (-dias,))

    deletados = cursor.rowcount
    conn.commit()
    conn.close()
    return deletados


def obter_estatisticas():
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    cursor.execute("SELECT COUNT(*) FROM produtos")
    stats["total_produtos"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT categoria) FROM produtos")
    stats["total_categorias"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(porcentagem_desconto) 
        FROM produtos 
        WHERE porcentagem_desconto IS NOT NULL
    """)
    resultado = cursor.fetchone()[0]
    stats["media_desconto"] = round(resultado, 1) if resultado else 0

    cursor.execute("""
        SELECT MAX(porcentagem_desconto) 
        FROM produtos 
        WHERE porcentagem_desconto IS NOT NULL
    """)
    resultado = cursor.fetchone()[0]
    stats["maior_desconto"] = round(resultado, 1) if resultado else 0

    cursor.execute("""
        SELECT data_coleta FROM produtos 
        ORDER BY data_coleta DESC LIMIT 1
    """)
    resultado = cursor.fetchone()
    stats["ultima_atualizacao"] = resultado[0] if resultado else "Nunca"

    cursor.execute("""
        SELECT AVG(vendidos) FROM produtos 
        WHERE vendidos IS NOT NULL
    """)
    resultado = cursor.fetchone()[0]
    stats["media_vendas"] = int(resultado) if resultado else 0

    conn.close()
    return stats
