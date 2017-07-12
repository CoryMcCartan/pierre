import click as cl

@cl.group()
def main():
    cl.secho("Hello.", fg="red", bold=True)
    cl.echo(c.get_app_dir("pierre"))
