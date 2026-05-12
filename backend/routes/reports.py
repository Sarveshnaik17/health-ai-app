"""
MediVision AI - Report Routes
GET /api/reports/csv - Download prediction history as CSV
GET /api/reports/pdf - Download prediction report as PDF
"""
import io, csv
from flask import Blueprint, send_file, make_response
from datetime import datetime, timezone
from utils.db import get_predictions_collection
from utils.helpers import token_required, error_response

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@reports_bp.route("/csv", methods=["GET"])
@token_required
def download_csv(current_user):
    preds = get_predictions_collection()
    records = list(preds.find({"user": current_user}).sort("timestamp", -1))
    if not records:
        return error_response("No records to export", 404)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date","Risk","Probability","Confidence","Category",
        "Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin","BMI","DPF","Age"])
    for r in records:
        ts = r.get("timestamp","")
        if hasattr(ts, "strftime"): ts = ts.strftime("%Y-%m-%d %H:%M:%S")
        inp = r.get("input_data", {})
        writer.writerow([ts, r.get("risk",""), r.get("probability",""), r.get("confidence",""),
            r.get("risk_category",""), inp.get("Pregnancies",""), inp.get("Glucose",""),
            inp.get("BloodPressure",""), inp.get("SkinThickness",""), inp.get("Insulin",""),
            inp.get("BMI",""), inp.get("DiabetesPedigreeFunction",""), inp.get("Age","")])
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers["Content-Type"] = "text/csv"
    resp.headers["Content-Disposition"] = f"attachment; filename=medivision_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
    return resp

@reports_bp.route("/pdf", methods=["GET"])
@token_required
def download_pdf(current_user):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch, cm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        return error_response("reportlab not installed", 503)
    preds = get_predictions_collection()
    records = list(preds.find({"user": current_user}).sort("timestamp", -1).limit(50))
    if not records:
        return error_response("No records for PDF", 404)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle("T", parent=styles["Title"], fontSize=22, textColor=HexColor("#1d4ed8"), spaceAfter=10)
    sub_s = ParagraphStyle("S", parent=styles["Normal"], fontSize=12, textColor=HexColor("#64748b"), spaceAfter=20)
    elems = []
    elems.append(Paragraph("MediVision AI - Health Report", title_s))
    elems.append(Paragraph(f"Patient: {current_user} | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", sub_s))
    elems.append(Spacer(1, 0.3*inch))
    total = len(records)
    high = sum(1 for r in records if r.get("risk")=="High Risk")
    avg_p = round(sum(r.get("probability",0) for r in records)/total, 2)
    sd = [["Total",str(total)],["High Risk",str(high)],["Low Risk",str(total-high)],["Avg Score",f"{avg_p}%"]]
    st = Table(sd, colWidths=[3*inch, 2*inch])
    st.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor("#f1f5f9")),("PADDING",(0,0),(-1,-1),10),("GRID",(0,0),(-1,-1),0.5,HexColor("#cbd5e1"))]))
    elems.append(st)
    elems.append(Spacer(1, 0.4*inch))
    elems.append(Paragraph("Prediction History", styles["Heading2"]))
    elems.append(Spacer(1, 0.2*inch))
    td = [["Date","Risk","Score (%)","Category"]]
    for r in records:
        ts = r.get("timestamp","")
        if hasattr(ts, "strftime"): ts = ts.strftime("%Y-%m-%d %H:%M")
        td.append([str(ts), r.get("risk",""), str(r.get("probability","")), r.get("risk_category","")])
    ht = Table(td, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1.4*inch])
    ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),HexColor("#1d4ed8")),("TEXTCOLOR",(0,0),(-1,0),HexColor("#fff")),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("PADDING",(0,0),(-1,-1),6),
        ("GRID",(0,0),(-1,-1),0.5,HexColor("#e2e8f0")),("ROWBACKGROUNDS",(0,1),(-1,-1),[HexColor("#fff"),HexColor("#f8fafc")])]))
    elems.append(ht)
    doc.build(elems)
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True,
        download_name=f"medivision_report_{current_user}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf")
