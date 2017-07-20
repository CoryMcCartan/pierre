#!/usr/bin/env python3

import json

import click as cl

import evaluate
import render


version_message = """
%(prog)s version %(version)s

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.
"""
STDIN = cl.get_text_stream("stdin")
STDOUT = cl.get_text_stream("stdout")


###################################
# ENTRY POINT                     #
###################################

@cl.group("pierre")
@cl.version_option(message=version_message.strip())
@cl.pass_context
def main(ctx):
    """A tool for evaluating and documenting hypotheses and evidence using Bayes' rule."""
    pass


@main.command("eval")
@cl.argument("file", type=cl.File("r+"), default=STDIN)
def eval_file(file):
    """Evaluate a Bayes document."""
    text = file.read()
    text = evaluate.clean_text(text)

    result, _ = evaluate.run_file(text)
    file.seek(0)
    file.truncate()
    file.write(result)


@main.command()
@cl.argument("file", type=cl.File("r+"), default=STDIN)
@cl.option("-o", "--output", type=cl.Path(), default="-",
        help="Output file. Defaults to STDOUT.")
def data(file, output):
    """Export Bayes document data."""
    text = file.read()
    text = evaluate.clean_text(text)

    _, hypotheses = evaluate.run_file(text)

    with cl.open_file(output, "w+") as f:
        json.dump(hypotheses, f)
        f.write("\n")


@main.command("render")
@cl.argument("file", type=cl.File("r"), default=STDIN)
@cl.option("-o", "--output", type=cl.Path(), default="-",
        help="Output file. Defaults to STDOUT.")
@cl.option("-f", "--format", type=cl.Choice(["html", "tex", "pdf"]),
        help="Output format. Defaults to HTML, but will be inffered from suffix of output file.")
@cl.option("-s", "--style", type=cl.File("r"),
        help="Render stylesheet, CSS or TeX, that will be added to the output file.")
def render_file(file, output, format, style):
    """Evaluate and render a Bayes document."""
    text = file.read()
    text = evaluate.clean_text(text)
    text, _ = evaluate.run_file(text)

    title, markdown = render.extract_title(text)

    # infer type by output file name
    if format is None:
        format = infer_type(output, "html")

    if format == "html":
        rendered = render.html_render(markdown, title, style)
    elif format == "tex":
        rendered = render.tex_render(markdown, title, style)
    elif format == "pdf":
        rendered = render.tex_render(markdown, title, style)
        if output == "-":
            raise cl.UsageError("Cannot write PDF to STDOUT. Please specify a file to write to.")
        render.make_pdf(rendered, output)
        return

    with cl.open_file(output, "w+") as f:
        f.write(rendered)


@main.command()
@cl.argument("topic", default=None, required=False, nargs=1)
@cl.pass_context
def help(ctx, topic):
    """Get help on a particular command."""
    if topic is None:
        cl.echo(ctx.parent.get_help())
    else:
        cl.echo(main.commands[topic].get_help(ctx))


###################################
# HELPER FUNCTIONS                #
###################################

def infer_type(filename, default):
    split = filename.rsplit(".", 1)
    if len(split) > 1:
        return split[-1]
    else:
        return default

if __name__ == "__main__":
    main()
