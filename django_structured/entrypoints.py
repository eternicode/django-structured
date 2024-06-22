import click

from .options import AppOptions, ProjectOptions, click_options


@click.group()
def structured():
    pass


@structured.command()
@click_options(ProjectOptions)
def startproject(**options):
    options = ProjectOptions(**options)
    breakpoint()


@structured.command()
@click_options(AppOptions)
def startapp(**options):
    options = AppOptions(**options)
    breakpoint()
