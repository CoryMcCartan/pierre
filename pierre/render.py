import os
import os.path as path
import subprocess
import shutil
import tempfile
import re
import contextlib
from textwrap import dedent, indent
from math import floor

import mistune
from latex import LatexRenderer

def html_render(text, title, style):
    renderer = HTML_Renderer() # allow raw HTML in markdown
    markdown = mistune.Markdown(renderer)
    html = indent(markdown(text), " "*8)

    if style is not None:
        css = style.read()
    else:
        css = ""

    return dedent(f"""\
        <html>
        <head>
            <title>{title}</title>
            <style>{css}</style>
            <script type="text/x-mathjax-config">
                MathJax.Hub.Config({{
                    messageStyle: "none",
                    CommonHTML: {{ linebreaks: {{ automatic: true }} }},
                    tex2jax: {{inlineMath: [['$','$']]}}
                }});
            </script>
            <script async 
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
        </head>
        <body>
            <h1 style="font-size: 2.5em" class="title">{title}</h1>
            <main>
            {html}
            </main>
        </body>
        """)

def tex_render(text, title, style):
    renderer = TeX_Renderer()
    markdown = mistune.Markdown(renderer)
    latex = indent(markdown(text), " "*8)
    # fixing latex output
    latex = latex.replace(r"\hrulefill", "\n\hrulefill\\\\\n")
    latex = latex.replace("%", r"\%")

    if style is not None:
        styling = style.read()
    else:
        styling = ""

    return dedent(f"""\
        \\documentclass{{article}}

        \\setcounter{{secnumdepth}}{{0}}
        \\usepackage[margin=1.0in]{{geometry}}
        {styling}

        \\title{{{title}}}

        \\begin{{document}}
            \maketitle

            {latex}
        \\end{{document}}
        """)

# Render a PDF from LaTeX source
def make_pdf(latex, outname):
    tex_file = tempfile.NamedTemporaryFile(delete=False).name
    filename = path.basename(tex_file) 

    with cwd(path.dirname(tex_file)):
        with open(filename, "w+") as f:
            f.write(latex)
            f.close()

        with open(os.devnull, 'w') as FNULL:
            proc = subprocess.Popen(["pdflatex", filename], stdout=FNULL)
            proc.communicate()

        os.unlink(filename)
        os.unlink(filename + ".log")

    shutil.move(tex_file + ".pdf", outname)


class BayesMixin(object):
    def __init__(self, lang):
        self.lang = lang

    def get_eval(self, text):
        match = re.search(r"\[([-+]?\d+\.?\d*)\]", text)

        if not match:
            num =  float(re.split(r"[ =]", text.strip())[-1])
        else:
            num = float(match.group(1))

        if num == floor(num):
            num = int(num)

        return num

    def get_evidence_eval(self, text):
        match = re.search("\[([+-]?\d+.?\d*) ==([+-]?\d+.?\d*)==> ([+-]?\d+.?\d*)\]", text)
        if not match:
            raise cl.UsageError(f"Properly formatted evaluation not found: {text}")
        else:
            return [float(match.group(1)), float(match.group(2)), 
                    float(match.group(3))]

    def codespan(self, text):
        value = self.get_eval(text)
        return str(round(value, 2))

    def block_code(self, text, lang):
        first, *lines = text.split("\n")
        kind = first.split(":", 1)[0]

        if kind == "@priors":
            return self.format_prior(lines)
        elif kind == "@evidence":
            return self.format_evidence(lines, first)
        else:
            raise cl.UsageError(f"Unknown block type '{kind[1:]}.'")

    def format_prior(self, lines):
        output = []
        for l in lines:
            try: label, value = l.split(":")
            except: continue
            label = label.strip()
            value = self.get_eval(value) # parse number
            output.append([label, f"{value:.1%}"])

        if self.lang == "html":
            rows = map(lambda r: f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>", output)
            rows = " ".join(rows)
            return dedent(f"""\
                <table>
                    <tr><th>Hypothesis</th><th>Prior</th></tr>
                    {rows}
                </table>""")
        elif self.lang == "tex":
            rows = map(lambda r: f"{r[0]} & {r[1]}", output)
            rows = " \\\\ ".join(rows)
            return dedent(f"""\
                \\begin{{center}}
                \\begin{{tabular}}{{ l|r }}
                    \\hline
                    Hypothesis & Prior \\\\ \\hline 
                    {rows}
                \\end{{tabular}}
                \\end{{center}}""")

    def format_evidence(self, lines, first):
        # handle labels for evidence
        first = first.split(":")
        label = None
        if len(first) > 1:
            label = first[1].strip()
        evt_str = f"Evidence: {label}" if label is not None else ""
        if label is not None:
            if label.startswith("not "):
                table_str = f" of not being {label[4:]}"
            else:
                table_str = f" of being {label}"
        else:
            table_str = ""

        output = []
        for l in lines:
            try: label, value = l.split(":")
            except: continue
            label = label.strip()
            # parse evaluation
            prior, likelihood, posterior = self.get_evidence_eval(value)
            output.append([label, f"{prior:.1%}", f"{likelihood:.1%}", 
                            f"{posterior:.1%}"])

        if self.lang == "html":
            rows = map(lambda r: (f"<tr><td>{r[0]}</td><td>{r[1]}</td>"
                                 f"<td>{r[2]}</td><td>{r[3]}</td></tr>"), 
                       output)
            rows = " ".join(rows)
            return dedent(f"""\
                <strong>{evt_str}</strong>
                <table>
                    <tr><th>Hypothesis</th><th>Prior</th>
                    <th>Likelihood{table_str}</th><th>Posterior</th></tr>
                    {rows}
                </table>""")
        elif self.lang == "tex":
            rows = map(lambda r: f"{r[0]} & {r[1]} & {r[2]} & {r[3]}", output)
            rows = r" \\ ".join(rows)
            return dedent(f"""\
                \\begin{{center}}
                \\textbf{{{evt_str}}}

                \\begin{{tabular}}{{ l|r r|r }}
                    \\hline
                    Hypothesis & Prior & Likelihood{table_str} & Posterior \\\\ 
                    \\hline 
                    {rows}
                \\end{{tabular}}
                \\end{{center}}""")

# Dummy classes to insert Bayes mixin and hold defaults
class HTML_Renderer(BayesMixin, mistune.Renderer):
    def __init__(self):
        BayesMixin.__init__(self, lang="html")
        mistune.Renderer.__init__(self, escape=False)
        

class TeX_Renderer(BayesMixin, LatexRenderer):
    def __init__(self):
        BayesMixin.__init__(self, lang="tex")
        LatexRenderer.__init__(self)


def extract_title(markdown):
    """Take the first header from the markdown and use it as the title."""
    result = re.split(r"^\s*# *(.+)", markdown, maxsplit=0)
    title = result[1]
    markdown = result[2].strip()
    return title, markdown


@contextlib.contextmanager
def cwd(dirname):
    curdir = os.getcwd()
    try: 
        os.chdir(dirname)
        yield
    finally: 
        os.chdir(curdir)
