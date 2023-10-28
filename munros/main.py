import click
from munros.gateway import MunrosCSVGateway
from munros.presenter import MapPresenter
from munros.usecase import FastestRouteSolver


@click.command()
@click.option('--fast', default=True, help='Use first solution strategy')
def main(fast):
    presenter = MapPresenter()
    FastestRouteSolver(MunrosCSVGateway('munros.csv'), presenter)(fast)
    presenter.present()
    
    
