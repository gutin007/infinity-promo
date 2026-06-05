import schedule
import time
import signal
import sys
from datetime import datetime, timedelta

from config import UPDATE_INTERVAL, SHOPEE_AFFILIATE_ID
from database import init_db, inserir_produtos_em_lote, obter_estatisticas
from scraper import scraping_completo
from display import (
    console, exibir_cabecalho, exibir_estatisticas,
    exibir_lista_produtos, exibir_resumo_atualizacao,
    exibir_erro, exibir_mensagem_agendamento, exibir_titulo_secao
)


def executar_scraping():
    console.clear()
    exibir_cabecalho()

    if not SHOPEE_AFFILIATE_ID:
        console.print("[yellow]AVISO: ID de afiliado nao configurado. Links serao gerados sem rastreamento.[/]")
        console.print("[dim]Configure a variavel SHOPEE_AFFILIATE_ID no arquivo .env[/]")
        console.print()

    exibir_titulo_secao("INICIANDO SCRAPING DA SHOPEE")

    try:
        produtos = scraping_completo()

        if produtos:
            exibir_titulo_secao("SALVANDO NO BANCO DE DADOS")
            inseridos = inserir_produtos_em_lote(produtos)
            console.print(f"[green]✓[/] {inseridos} produtos salvos com sucesso")

            stats = obter_estatisticas()

            console.clear()
            exibir_cabecalho()
            exibir_estatisticas()
            exibir_lista_produtos(produtos)
            exibir_resumo_atualizacao(inseridos, stats["total_produtos"])
        else:
            exibir_erro("Nenhum produto encontrado nesta execucao")

    except Exception as e:
        exibir_erro(f"Erro durante o scraping: {str(e)}")


def agendar_execucoes():
    schedule.every(UPDATE_INTERVAL).seconds.do(executar_scraping)

    proxima = datetime.now() + timedelta(seconds=UPDATE_INTERVAL)
    exibir_mensagem_agendamento(proxima.strftime("%d/%m/%Y %H:%M:%S"))

    while True:
        schedule.run_pending()
        time.sleep(1)


def signal_handler(sig, frame):
    console.print("\n[yellow]Bot encerrado pelo usuario.[/]")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    console.clear()

    init_db()

    exibir_cabecalho()
    console.print("[bold orange1]Bot de Promocoes da Shopee[/]")
    console.print("[dim]Pressione Ctrl+C a qualquer momento para parar[/]")
    console.print()

    if not SHOPEE_AFFILIATE_ID:
        console.print("[yellow]AVISO: Configure seu ID de afiliado no arquivo .env[/]")
        console.print()

    executar_scraping()

    agendar_execucoes()


if __name__ == "__main__":
    main()
