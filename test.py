def _quick_format_html(html: str) -> str:
    if not html:
        return html
    
    html = html.replace("<", "\n<")
    html = html.replace(">", ">\n")
    
    html_clean = ""
    in_tag = False
    for line in html.splitlines():
        if line.startswith("<"):
            in_tag = True
        if line.endswith(">"):
            in_tag = False
        html_clean += line
        if not in_tag:
            html_clean += "\n"

    return html


html = """<a pa nesto?>
<div pdksldjlas?>
jao
pao
dao
<div ovo 
je  u vise
linija div >
opet
<br>
"""

print (_quick_format_html(html))