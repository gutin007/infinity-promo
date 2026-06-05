from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from database import (
    buscar_todas_promocoes, buscar_por_categoria,
    contar_por_categoria, obter_estatisticas
)

console = Console()


def formatar_preco(valor):
    if valor is None:
        return "N/A"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_vendidos(valor):
    if valor is None:
        return ""
    if valor >= 1000:
        return f"{valor/1000:.1f}k vendidos"
    return f"{valor} vendidos"


def exibir_cabecalho():
    console.print()
    console.print(Panel(
        Text("PROMOCOES DA SHOPEE", style="bold white", justify="center"),
        subtitle=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        style="orange1",
        box=box.DOUBLE
    ))
    console.print()


def exibir_estatisticas():
    stats = obter_estatisticas()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan")
    table.add_column(style="white")

    table.add_row("Total de Produtos:", str(stats["total_produtos"]))
    table.add_row("Categorias:", str(stats["total_categorias"]))
    table.add_row("Media de Desconto:", f"{stats['media_desconto']}%")
    table.add_row("Maior Desconto:", f"{stats['maior_desconto']}%")
    table.add_row("Media de Vendas:", formatar_vendidos(stats["media_vendas"]))
    table.add_row("Ultima Atualizacao:", stats["ultima_atualizacao"])

    console.print(Panel(table, title="[bold orange1]ESTATISTICAS[/]", border_style="orange1"))
    console.print()


def exibir_produto(produto, index=None):
    titulo = produto.get("titulo", "Sem titulo")
    preco_original = formatar_preco(produto.get("preco_original"))
    preco_desconto = formatar_preco(produto.get("preco_desconto"))
    desconto = produto.get("porcentagem_desconto")
    url = produto.get("url_afiliado") or produto.get("url_original", "")
    specs = produto.get("especificacoes", "")
    categoria = produto.get("categoria", "geral")
    vendidos = produto.get("vendidos")
    avaliacoes = produto.get("avaliacoes")

    header = f"#{index} " if index else ""
    header += titulo[:55] + ("..." if len(titulo) > 55 else "")

    lines = []
    lines.append(f"[bold red]De:[/] {preco_original}")
    lines.append(f"[bold green]Por:[/] {preco_desconto}")
    if desconto:
        lines.append(f"[bold yellow]Desconto:[/] {desconto}% OFF")
    if vendidos:
        lines.append(f"[bold magenta]Vendidos:[/] {formatar_vendidos(vendidos)}")
    if avaliacoes:
        lines.append(f"[bold cyan]Avaliacoes:[/] {avaliacoes} estrelas")
    if specs:
        lines.append(f"[bold blue]Info:[/] {specs}")
    lines.append(f"[dim]Categoria:[/] {categoria}")
    lines.append(f"[link={url}]Ver produto[/]")

    content = "\n".join(lines)

    console.print(Panel(
        content,
        title=f"[bold white]{header}[/]",
        border_style="orange1",
        width=80
    ))


def exibir_lista_produtos(produtos, titulo="PRODUTOS ENCONTRADOS"):
    console.print()
    console.print(f"[bold]{titulo}[/]", style="bold orange1")
    console.print("-" * 80)

    if not produtos:
        console.print("[yellow]Nenhum produto encontrado.[/]")
        return

    for i, produto in enumerate(produtos[:20], 1):
        exibir_produto(produto, i)

    console.print()
    console.print(f"[dim]Mostrando {min(20, len(produtos))} de {len(produtos)} produtos[/]")
    console.print()


def exibir_por_categoria():
    categorias = contar_por_categoria()

    if not categorias:
        console.print("[yellow]Nenhuma categoria encontrada.[/]")
        return

    table = Table(title="PRODUTOS POR CATEGORIA", box=box.ROUNDED)
    table.add_column("Categoria", style="cyan")
    table.add_column("Total", justify="right", style="green")

    for cat in categorias:
        table.add_row(cat["categoria"], str(cat["total"]))

    console.print(table)
    console.print()


def exibir_melhores_ofertas(produtos):
    console.print()
    console.print("[bold]MELHORES OFERTAS (maior desconto)[/]", style="bold orange1")
    console.print("-" * 80)

    produtos_ordenados = sorted(
        [p for p in produtos if p.get("porcentagem_desconto")],
        key=lambda x: x["porcentagem_desconto"],
        reverse=True
    )

    for i, produto in enumerate(produtos_ordenados[:10], 1):
        exibir_produto(produto, i)

    console.print()


def exibir_resumo_atualizacao(produtos_novos, produtos_total):
    console.print()
    console.print(Panel(
        f"[bold green]Scraping concluido![/]\n\n"
        f"Produtos coletados nesta execucao: [bold]{produtos_novos}[/]\n"
        f"Total no banco de dados: [bold]{produtos_total}[/]\n\n"
        f"[dim]Proxima atualizacao em 45 minutos...[/]",
        title="[bold yellow]STATUS[/]",
        border_style="yellow"
    ))
    console.print()


def exibir_mensagem_agendamento(proxima_execucao):
    console.print()
    console.print(Panel(
        f"[bold]Bot em execucao continua[/]\n\n"
        f"Proxima atualizacao: [bold cyan]{proxima_execucao}[/]\n"
        f"[dim]Pressione Ctrl+C para parar[/]",
        title="[bold green]AGENDAMENTO[/]",
        border_style="green"
    ))
    console.print()


def exibir_erro(mensagem):
    console.print()
    console.print(Panel(
        f"[bold red]{mensagem}[/]",
        title="[bold red]ERRO[/]",
        border_style="red"
    ))
    console.print()


def exibir_titulo_secao(titulo):
    console.print()
    console.rule(f"[bold white]{titulo}[/]", style="orange1")
    console.print()
