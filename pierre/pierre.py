import os

import click as cl

file_arg = cl.argument("file", type=cl.File("r+"))
desc_arg = cl.option("-d", "--description", prompt=True, default="")

divider_small = "-" * 30
divider = "#" * 78

@cl.group()
@cl.version_option(message="""%(prog)s version %(version)s

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.""")
@cl.pass_context
def main(ctx):
    """A tool for managing and evaluating hypotheses using Bayes' rule."""
    pass


@main.command()
@cl.argument("filename", type=cl.Path())
@cl.option("-t", "--title", prompt=True)
@desc_arg
def create(filename, title, description):
    """Create a hypothesis file."""
    if os.path.isfile(filename):
        cl.confirm(f"This will overwrite {filename}. Continue?", abort=True)
    
    with open(filename, "w+") as f:
        writeln(title, f)
        writeln(divider_small, f)
        writeln(description, f)
        writeln(divider, f)

@main.command()
@file_arg
@cl.option("-i", "--id", prompt=True, help="A short identifier for the hypothesis.")
@cl.option("-n", "--name", prompt=True, help="A human-readable name for the hypothesis.")
@desc_arg
@cl.option("-p", "--prob", type=cl.FLOAT, prompt=True, 
        help="The prior probability of the hypothesis.")
def add(file, id, name, description, prob):
    """Add a hypothesis."""
    


@main.command()
@cl.argument("topic", default=None, required=False, nargs=1)
@cl.pass_context
def help(ctx, topic):
    """Get help on a particular command."""
    if topic is None:
        cl.echo(ctx.parent.get_help())
    else:
        cl.echo(main.commands[topic].get_help(ctx))


######################################
# HELPER FUNCTIONS                   #
######################################

def writeln(text, f):
    print(cl.wrap_text(text), file=f)
