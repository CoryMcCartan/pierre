#!/usr/bin/env python3

import os
from datetime import datetime

import yaml
import click as cl

file_arg = cl.argument("file", type=cl.File("r+"))
desc_arg = cl.option("-d", "--description", prompt=True, default="")

yaml_opts = {
        "default_flow_style": False,
        "width": 72,
        "indent": 4,
        }


###################################
# ENTRY POINT                     #
###################################

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


###################################
# COMMANDS                        #
###################################

@main.command()
@cl.argument("filename", type=cl.Path())
@cl.option("-t", "--title", prompt=True)
@cl.option("-f", "--force", is_flag=True, help="Force overwrite any existing file.")
@desc_arg
def create(filename, title, force, description):
    """Create a hypothesis file."""
    if os.path.isfile(filename) and not force:
        cl.confirm(f"This will overwrite {filename}. Continue?", abort=True)

    doc = {
            "title": title,
            "description": description,
            "date": f"{datetime.now():%B %d, %Y}",
            "hypotheses": {},
            "updates": [],
            }
    with open(filename, "w+") as f:
        yaml.dump(doc, f, **yaml_opts)

@main.command()
@file_arg
@cl.option("-i", "--id", prompt=True, help="A short identifier for the hypothesis. "
        "This is how you will refer to this hypothesis in future updates.")
@cl.option("-n", "--name", prompt=True, help="A human-readable name for the hypothesis.")
@desc_arg
@cl.option("-p", "--prob", type=cl.FLOAT, prompt=True, 
        help="The prior probability of the hypothesis.")
def add(file, id, name, description, prob):
    """Add a hypothesis."""
    doc = yaml.load(file)
    doc["hypotheses"][id] = {
        "name": name,
        "description": description,
        "prior": prob,
    }
    save(doc, file)


@main.command()
@file_arg
@cl.option("-n", "--name", prompt=True, help="A name for the event.")
@desc_arg
@cl.option("-p", "--prob", type=cl.FLOAT, prompt=True, 
        help="The probability of the hypothesis.")
@cl.option("-l", "--likelihood", multiple=True, type=cl.Tuple([str, float]),
        help="The likelihood of each hypothesis: P(hypothesis|envent). "
        "Type <id> followed by <prob>.")
def update(file, name, description, prob, likelihood):
    """Update hypotheses based on new information."""
    likelihood = list(likelihood)
    doc = yaml.load(file)
    hyp = doc["hypotheses"]
    # prompt for missing likelihoods
    given_hyp = [l[0] for l in likelihood]
    to_prompt = [h for h in hyp if h not in given_hyp] 
    for h in to_prompt:
        likelihood.append((h, cl.prompt(f"P({name} | {h})", type=cl.FLOAT)))

    # calculate bayes rule
    if len(doc["updates"]) == 0: # first update
        priors = {h: hyp[h]["prior"] for h in hyp}
    else:
        priors = doc["updates"][-1].updated.copy()

    update_obj = {
        "name": name,
        "description": description,
        "date": f"{datetime.now():%B %d, %Y}",
        "priors": priors,
        "updated": priors.copy(),
    }

    for h in hyp:
        lk = [l[1] for l in likelihood if l[0] == h][0]
        update_obj["updated"][h] = update_obj["priors"][h] * lk / prob
    doc["updates"].append(update_obj)

    save(doc, file)
        

    
@main.command()
@file_arg
def rerun(file):
    """Rerun the document and calculations."""
    doc = yaml.load(file)
    save(doc, file)


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

def save(obj, file):
    file.seek(0)
    file.truncate()
    yaml.dump(obj, file, **yaml_opts)


if __name__ == "__main__":
    main()
