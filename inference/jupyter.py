proof_css = """
<style>
table.inference_proof {
  border: none;
  border-collapse: collapse;
}

table.inference_proof table {
  border: none;
  border-collapse: collapse;
  margin: 0 auto !important;
}


table.inference_proof td {
  border-width: 0 20px 0 0;
  padding: 2px 0;
  border-style: solid;
  border-color: black rgba(0,0,0,0);
  vertical-align: bottom;
  text-align: center;
  white-space: nowrap
}

table.inference_proof td:last-child {
  border-width: 0 !important;

}

table.inference_proof tr {
  border-width: 0;
}


table.inference_proof tr:last-child td {
  border-width: 1px 0 0 0 !important;
}
</style>
"""


def proof_to_html(proof, nested=False):
    rule = proof.rule
    relation_str = f'<span title="{rule.name}">{proof.conclusion!r}</span>'

    pre_htmls = [proof_to_html(p, nested=True) for p in proof.premises]
    result = []
    if nested:
        result = ['<table>']
    else:
        result = [proof_css, '<table class="inference_proof">']

    if pre_htmls:
        result.append('<tr>')
        for pre_html in pre_htmls:
            result.append('<td>')
            result.append(pre_html)
            result.append('</td>')
        result.append('</tr>')
    colspan = len(pre_htmls) or 1
    result.append(f'<tr><td colspan={colspan}>{relation_str}</td></tr></table>')
    return ''.join(result)
