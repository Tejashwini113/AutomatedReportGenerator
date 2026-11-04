
from flask import Flask, send_file
import subprocess
import os
import platform
import getpass
import uuid
import socket
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")

NAVY = colors.HexColor("#18344F")
BLUE = colors.HexColor("#315B7D")
LIGHT = colors.HexColor("#EDF2F6")
GREY = colors.HexColor("#64748B")


def get_command_output(command):
    try:
        return subprocess.check_output(
            command,
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "Not available"


def create_table(data):
    table = Table(data, colWidths=[175, 315], repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CFD8E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, LIGHT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    return table


def add_footer(canvas, doc):
    canvas.saveState()

    width, height = A4

    canvas.setStrokeColor(colors.HexColor("#B8C5D1"))
    canvas.line(40, 40, width - 40, 40)

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)

    canvas.drawString(
        40, 26,
        "SYSTEM INFORMATION REPORT | CONFIDENTIAL"
    )

    canvas.drawRightString(
        width - 40, 26,
        f"Page {doc.page}"
    )

    canvas.restoreState()


@app.route("/")
def home():
    return send_file(os.path.join(BASE_DIR, "index.html"))


@app.route("/style.css")
def css():
    return send_file(os.path.join(BASE_DIR, "style.css"))


@app.route("/generate", methods=["POST"])
def generate():

    os.makedirs(REPORT_DIR, exist_ok=True)

    report_id = "SAR-" + uuid.uuid4().hex[:10].upper()
    now = datetime.now()

    pdf_path = os.path.join(REPORT_DIR, "System_Report.pdf")

    hostname = platform.node()
    username = getpass.getuser()
    operating_system = platform.platform()
    architecture = platform.machine()
    processor = get_command_output([
        "bash", "-c",
        "lscpu | grep 'Model name' | head -1 | cut -d: -f2"
    ])

    memory = get_command_output(["free", "-h"]).splitlines()
    memory_values = memory[1].split() if len(memory) > 1 else []

    disk = get_command_output(["df", "-h", "/"]).splitlines()
    disk_values = disk[1].split() if len(disk) > 1 else []

    uptime = get_command_output(["uptime", "-p"])
    kernel = platform.release()

    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip_address = "Not available"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=42,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "OfficialTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=22,
        alignment=TA_CENTER,
        textColor=NAVY,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "OfficialSubtitle",
        parent=styles["Normal"],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=GREY,
        spaceAfter=17
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=7
    )

    note_style = ParagraphStyle(
        "Note",
        parent=styles["Normal"],
        fontSize=8,
        leading=12,
        textColor=GREY
    )

    elements = []

    elements.append(Paragraph(
        "SYSTEM AUDIT & INFORMATION REPORT",
        title_style
    ))

    elements.append(Paragraph(
        "TECHNICAL RECORD | SYSTEM CONFIGURATION AND RESOURCE UTILIZATION",
        subtitle_style
    ))

    elements.append(Paragraph(
        "DOCUMENT CONTROL",
        section_style
    ))

    control_data = [
        ["Document Reference", report_id],
        ["Document Type", "System Configuration Report"],
        ["Date of Generation", now.strftime("%d-%m-%Y")],
        ["Time of Generation", now.strftime("%H:%M:%S")],
        ["Collection Environment", "Linux / WSL"]
    ]

    elements.append(create_table([
        ["CONTROL FIELD", "RECORDED VALUE"]
    ] + control_data))

    elements.append(Paragraph(
        "1. SYSTEM IDENTIFICATION",
        section_style
    ))

    system_data = [
        ["System Property", "Recorded Information"],
        ["Device / Host Name", hostname],
        ["System User", username],
        ["Operating System", operating_system],
        ["Kernel Version", kernel],
        ["Processor Model", processor],
        ["System Architecture", architecture],
        ["System Uptime", uptime]
    ]

    elements.append(create_table(system_data))

    elements.append(Paragraph(
        "2. MEMORY RESOURCE UTILIZATION",
        section_style
    ))

    memory_data = [
        ["Memory Parameter", "Recorded Value"],
        ["Total Memory", memory_values[1] if len(memory_values) > 1 else "N/A"],
        ["Used Memory", memory_values[2] if len(memory_values) > 2 else "N/A"],
        ["Free Memory", memory_values[3] if len(memory_values) > 3 else "N/A"],
        ["Available Memory", memory_values[6] if len(memory_values) > 6 else "N/A"]
    ]

    elements.append(create_table(memory_data))

    elements.append(Paragraph(
        "3. STORAGE RESOURCE UTILIZATION",
        section_style
    ))

    disk_data = [
        ["Storage Parameter", "Recorded Value"],
        ["Total Capacity", disk_values[1] if len(disk_values) > 1 else "N/A"],
        ["Used Capacity", disk_values[2] if len(disk_values) > 2 else "N/A"],
        ["Available Capacity", disk_values[3] if len(disk_values) > 3 else "N/A"],
        ["Utilization", disk_values[4] if len(disk_values) > 4 else "N/A"]
    ]

    elements.append(create_table(disk_data))

    elements.append(Paragraph(
        "4. NETWORK CONFIGURATION",
        section_style
    ))

    network_data = [
        ["Network Parameter", "Recorded Value"],
        ["Host Name", hostname],
        ["Resolved IP Address", ip_address]
    ]

    elements.append(create_table(network_data))

    elements.append(Paragraph(
        "5. TECHNICAL OBSERVATIONS",
        section_style
    ))

    elements.append(Paragraph(
        "This report records the system configuration and resource "
        "utilization values accessible to the reporting application "
        "at the time of collection. Values may vary with system activity. "
        "The collection environment is Linux/WSL; therefore, the recorded "
        "values should not be interpreted as a complete inventory of "
        "the Windows host device.",
        note_style
    ))

    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        "<b>END OF REPORT</b>",
        ParagraphStyle(
            "End",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=9,
            textColor=NAVY,
            spaceBefore=8
        )
    ))

    doc.build(
        elements,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="System_Audit_Report.pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)
