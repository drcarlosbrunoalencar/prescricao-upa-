from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
import io, os

app = Flask(__name__)
CORS(app)

LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "logo.png")

def gerar_pdf(dados):
    W, H = A4
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    def header(c):
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, 1.5*cm, H-3.0*cm, width=9*cm, height=1.8*cm,
                        preserveAspectRatio=True, mask='auto')
        c.setLineWidth(0.8)
        c.rect(1.5*cm, H-4.8*cm, W-3*cm, 1.6*cm)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(W/2, H-3.8*cm, "UNIDADE DE PRONTO ATENDIMENTO (UPA) 24h")
        c.drawCentredString(W/2, H-4.5*cm, "PRESCRICAO MEDICA - ENFERMARIA")
        y1 = H-5.6*cm
        c.rect(1.5*cm, y1, W-3*cm, 0.72*cm)
        c.line(W-5.2*cm, y1, W-5.2*cm, y1+0.72*cm)
        c.setFont("Helvetica-Bold", 9); c.drawString(1.7*cm, y1+0.2*cm, "NOME:")
        c.setFont("Helvetica", 9); c.drawString(3.1*cm, y1+0.2*cm, dados['nome'].upper()[:48])
        c.setFont("Helvetica-Bold", 9); c.drawString(W-5.0*cm, y1+0.2*cm, "DN:")
        c.setFont("Helvetica", 9); c.drawString(W-4.2*cm, y1+0.2*cm, dados['dn'])
        y2 = y1-0.72*cm
        c.rect(1.5*cm, y2, W-3*cm, 0.72*cm)
        c.line(W-5.2*cm, y2, W-5.2*cm, y2+0.72*cm)
        c.setFont("Helvetica-Bold", 9); c.drawString(1.7*cm, y2+0.2*cm, "HD:")
        c.setFont("Helvetica", 9); c.drawString(2.8*cm, y2+0.2*cm, dados['hd'][:52])
        c.setFont("Helvetica-Bold", 9); c.drawString(W-5.0*cm, y2+0.2*cm, "DATA:")
        c.setFont("Helvetica", 9); c.drawString(W-3.9*cm, y2+0.2*cm, dados['data'])
        return y2 - 0.4*cm

    def draw_table_header(c, y):
        cols_local = [1.1*cm, 8.8*cm, 1.8*cm, 4.2*cm, 3.0*cm]
        th = 0.72*cm
        c.setLineWidth(0.7)
        c.rect(1.5*cm, y-th, sum(cols_local), th)
        hdrs = ["ITEM","MEDICAMENTO","VIA","POSOLOGIA","APRAZAMENTO"]
        xp = 1.5*cm
        c.setFont("Helvetica-Bold", 8)
        for i,(h,w) in enumerate(zip(hdrs, cols_local)):
            if i>0: c.line(xp, y-th, xp, y)
            c.drawCentredString(xp+w/2, y-th+0.18*cm, h)
            xp += w
        return y - th

    cols = [1.1*cm, 8.8*cm, 1.8*cm, 4.2*cm, 3.0*cm]
    tx = 1.5*cm
    rh = 0.62*cm

    def draw_row(c, y, item, med, via, pos, apraz, bold_med=False):
        c.setLineWidth(0.4)
        c.rect(tx, y-rh, sum(cols), rh)
        xp = tx
        vals = [item, med, via, pos, apraz]
        max_chars = [6, 62, 8, 28, 18]
        for i,(val,w,mx) in enumerate(zip(vals, cols, max_chars)):
            if i>0: c.line(xp, y-rh, xp, y)
            c.setFont("Helvetica-Bold" if (bold_med and i==1) else "Helvetica", 7.5)
            c.drawString(xp+0.12*cm, y-rh+0.16*cm, str(val)[:mx])
            xp += w
        return y - rh

    # --- PRESCRIÇÃO ---
    if dados.get('includePresc', True):
        y = header(c)
        y = draw_table_header(c, y)

        if dados.get('dieta'):
            y = draw_row(c, y, '', 'DIETA: '+dados['dieta'].upper(), '', '', '')
        if dados.get('sf','').strip():
            y = draw_row(c, y, '', 'SF 0,9% '+dados['sf'].upper(), 'EV', '', '')

        for m in dados.get('medicamentos', []):
            if m.get('med','').strip():
                if y - rh < 2*cm:
                    c.showPage(); y = header(c); y = draw_table_header(c, y)
                y = draw_row(c, y, m.get('item',''), m['med'].upper(),
                             m.get('via',''), m.get('pos',''), m.get('apraz',''), bold_med=True)

        for f in dados.get('fixos', []):
            if y - rh < 2*cm:
                c.showPage(); y = header(c); y = draw_table_header(c, y)
            y = draw_row(c, y, '', f['med'], f.get('via',''), f.get('pos',''), f.get('apraz',''))

        while y - rh > 1.8*cm:
            c.setLineWidth(0.4)
            c.rect(tx, y-rh, sum(cols), rh)
            xp = tx
            for w in cols: c.line(xp, y-rh, xp, y); xp += w
            y -= rh

    # --- EVOLUÇÃO ---
    if dados.get('includeEv', False):
        c.showPage()
        y = header(c)
        ev = dados.get('evolucao', {})
        bw = W-3*cm

        def ev_box(c, y, label, value, h):
            c.setLineWidth(0.5)
            c.rect(1.5*cm, y-h, bw, h)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(1.7*cm, y-0.42*cm, label)
            if value:
                c.setFont("Helvetica", 8)
                words = value.split(); line = ''; lines = []
                for w in words:
                    test = line+(' ' if line else '')+w
                    if c.stringWidth(test,"Helvetica",8) < bw-0.4*cm: line=test
                    else: lines.append(line); line=w
                if line: lines.append(line)
                off = 0.42*cm
                lbl_w = c.stringWidth(label,"Helvetica-Bold",8)+0.3*cm
                for ln in lines[:max(1,int(h/0.38/cm))]:
                    cx = 1.7*cm+(lbl_w if off==0.42*cm else 0)
                    c.drawString(cx, y-off, ln); off+=0.38*cm
            return y-h

        c.rect(1.5*cm, y-0.72*cm, bw, 0.72*cm)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(W/2, y-0.5*cm, "EVOLUCAO DE ENFERMARIA")
        y -= 0.72*cm

        c.rect(1.5*cm, y-0.65*cm, bw, 0.65*cm)
        c.line(1.5*cm+bw/2, y-0.65*cm, 1.5*cm+bw/2, y)
        c.setFont("Helvetica-Bold",8); c.drawString(1.7*cm, y-0.45*cm, "DIA DE INTERNACAO (DIH):")
        c.setFont("Helvetica",8); c.drawString(1.7*cm+4.8*cm, y-0.45*cm, ev.get('dih',''))
        c.setFont("Helvetica-Bold",8); c.drawString(1.5*cm+bw/2+0.2*cm, y-0.45*cm, "HIPOTESE(S) DIAGNOSTICA(S):")
        c.setFont("Helvetica",8); c.drawString(1.5*cm+bw/2+5.3*cm, y-0.45*cm, ev.get('hipoteses', dados.get('hd',''))[:22])
        y -= 0.65*cm

        fields = [
            ("ADMISSAO:", ev.get('admissao',''), 2.2*cm),
            ("COMORBIDADES:", ev.get('comorbidades',''), 1.5*cm),
            ("ANTECEDENTES:", ev.get('antecedentes',''), 1.3*cm),
            ("ATB PREVIO:", ev.get('atb_previo',''), 1.3*cm),
            ("EVOLUCAO MEDICA:", ev.get('evolucao_medica',''), 3.5*cm),
            ("EXAME FISICO:", ev.get('exame_fisico',''), 3.5*cm),
            ("CONDUTA:", ev.get('conduta',''), 2.8*cm),
        ]
        for lbl, val, h in fields:
            if y-h < 1.5*cm: c.showPage(); y = H-2*cm
            y = ev_box(c, y, lbl, val, h)

    c.save()
    buf.seek(0)
    return buf


@app.route("/")
def index():
    return send_file("static/index.html")

@app.route("/gerar", methods=["POST"])
def gerar():
    dados = request.get_json()
    buf = gerar_pdf(dados)
    nome = dados.get('nome','paciente').replace(' ','_').lower()
    return send_file(buf, mimetype='application/pdf',
                     as_attachment=True,
                     download_name=f'prescricao_{nome}.pdf')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
