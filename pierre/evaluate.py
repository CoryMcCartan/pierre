import re
from textwrap import dedent, indent

import click as cl

PREC = 6

def run_file(text):
    """Evaluate a Bayes file."""
    global file_vars, env
    file_vars = {}
    env = {"__builtins__": {}}

    # extract code chunks from text, combine, and sort by position
    chunks = extract_chunks(text)

    hypotheses = {}
    # as we insert values, the string will get longer, so we must keep track
    # of how much we've shifted it
    offset = 0 
    # Evaluate each chunk
    for match in chunks:
        chunk = dedent(match.group(1))

        if chunk.startswith("@"): # block
            new = run_block(chunk, hypotheses)
            new = indent(new, " "*4)
        else: # inline
            new = run_inline(chunk)

        # insert evaluated chunk back into text
        start, end = match.span(1)
        text = text[:start+offset] + new + text[end+offset:]
        offset += len(dedent(new)) - len(chunk)

    return text, hypotheses


def run_inline(chunk):
    """Evaluate a chunk of inline code."""
    sides = chunk.split("=")
    if len(sides) > 1:
        expr = sides[1]
    else:
        expr = sides[0]

    value = eval(expr, env, file_vars)

    # save value
    if len(sides) > 1:
        varname = sides[0].strip()
        file_vars[varname] = value

    if is_num(expr):
        return chunk
    else:
        return f"{chunk} [{value}]"


def run_block(chunk, hypotheses):
    """Evaluate a Bayes block."""
    first, *lines, last = chunk.split("\n")
    kind = first.split(" ", 1)[0]

    if kind == "@priors":
        new_lines = run_priors(lines, hypotheses)
    elif kind == "@evidence":
        new_lines = run_evidence(first, lines, hypotheses)
    else:
        raise cl.UsageError(f"Unknown block type '{kind[1:]}.'")

    new_lines = "\n".join(new_lines)
    return f"{first}\n{new_lines}\n{last}"


def run_priors(lines, hypotheses):
    """Evaluate a priors block."""
    data = {}

    for line in lines:
        name, expr = line.split(":")

        prior = eval(expr, env, file_vars)
        prior = round(prior, PREC)
        data[line] = prior
        hypotheses[name] = [prior]


    normalize(hypotheses)

    for i, line in enumerate(lines):
        if is_num(expr): continue
        lines[i] = f"{line} [{data[line]}]" 

    return lines

def run_evidence(first, lines, hypotheses):
    """Evaluate an evidence block."""
    data = {}

    for line in lines:
        name, expr = line.split(":")
        if not name in hypotheses:
            raise cl.UsageError(f"Unknown hypothesis: '{name}.'")

        likelihood = eval(expr, env, file_vars)
        likelihood = round(likelihood, PREC)
        # apply Bayes' rule
        prior = hypotheses[name][-1]
        posterior = prior * likelihood
        data[line] = [prior, likelihood, posterior]

        hypotheses[name].append(posterior)

    norm = normalize(hypotheses)

    for i, line in enumerate(lines):
        lines[i] = (f"{line} [{data[line][0]} =={data[line][1]}==> "
                f"{round(data[line][2] / norm, PREC)}]")

    return lines


def normalize(hypotheses, index=-1):
    """Normalize probabilities."""
    total = 0
    for probs in hypotheses.values():
        total += probs[index]
    for probs in hypotheses.values():
        probs[index] /= total

    return total


def clean_text(text):
    """Clear out old evaluations and results from file."""
    text = re.sub(r" ?\[[-+]?\d*\.?\d*\]", "", text)
    text = re.sub("\[([+-]?\d+.?\d*) ==([+-]?\d+.?\d*)==> ([+-]?\d+.?\d*)\]", "", text)
    return text


def extract_chunks(text):
    """Extract chunks of code from Bayes file."""
    inline = re.finditer(r"`([^`]+)`", text)
    blocks = re.finditer(r"\n((?:^(?:    | *\t)+.*\n)+)", text, re.M)
    chunks = [*inline] + [*blocks] 
    chunks.sort(key=lambda m: m.start())
    return chunks

def is_num(text):
    """Check if text can be parsed as a number."""
    try:
        float(text)
    except:
        return False
    else:
        return True

