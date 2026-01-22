import csv
import json
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors


def export_csv(case_data, output_path):
    try:
        files_data = case_data.get("files", [])
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if not files_data:
                return {"success": False, "error": "No files in case"}
            
            fieldnames = ["file_name", "file_path", "file_size", "created_time", "modified_time", "file_extension", "signature_valid", "md5", "sha256"]
            
            for file_data in files_data:
                metadata = file_data.get("metadata", {})
                for key in metadata.keys():
                    if key not in fieldnames and "error" not in key:
                        fieldnames.append(key)
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for file_data in files_data:
                metadata = file_data.get("metadata", {})
                hashes = file_data.get("hashes", {})
                
                row = {}
                for field in fieldnames:
                    if field in metadata:
                        row[field] = metadata[field]
                    elif field == "md5":
                        row[field] = hashes.get("md5", "")
                    elif field == "sha256":
                        row[field] = hashes.get("sha256", "")
                    else:
                        row[field] = ""
                
                writer.writerow(row)
        
        return {"success": True, "message": f"CSV report exported to {output_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_pdf(case_data, output_path):
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        story.append(Paragraph("MetaTrace Digital Evidence Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        case_info = [
            ["Case ID:", case_data.get("case_id", "")],
            ["Case Name:", case_data.get("case_name", "")],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Total Files:", str(case_data.get("total_files", 0))],
            ["Correlations Found:", str(case_data.get("correlation_count", 0))]
        ]
        
        case_table = Table(case_info, colWidths=[2*inch, 4.5*inch])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f2ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(case_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("File Summary", heading_style))
        
        files_data = case_data.get("files", [])
        for idx, file_data in enumerate(files_data, 1):
            metadata = file_data.get("metadata", {})
            hashes = file_data.get("hashes", {})
            anomalies = file_data.get("anomalies", [])
            
            file_info = [
                ["File Name:", metadata.get("file_name", "")],
                ["File Size:", str(metadata.get("file_size", "")) + " bytes"],
                ["MD5:", hashes.get("md5", "")[:32] + "..."],
                ["SHA256:", hashes.get("sha256", "")[:32] + "..."],
            ]
            
            file_table = Table(file_info, colWidths=[2*inch, 4.5*inch])
            file_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
            ]))
            
            story.append(Paragraph(f"File {idx}: {metadata.get('file_name', '')}", styles['Heading3']))
            story.append(file_table)
            
            if anomalies:
                story.append(Paragraph(f"⚠️ Anomalies Detected ({len(anomalies)})", styles['Normal']))
                for anomaly in anomalies:
                    story.append(Paragraph(f"• {anomaly['message']}", styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        correlations = case_data.get("correlations", [])
        if correlations:
            story.append(PageBreak())
            story.append(Paragraph("Correlation Analysis", heading_style))
            
            for corr in correlations:
                corr_text = f"<b>{corr['matched_field']}</b>: {corr['matched_value'][:60]}<br/>Confidence: {corr['confidence']}%<br/>{corr['explanation']}"
                story.append(Paragraph(corr_text, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return {"success": True, "message": f"PDF report exported to {output_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_html(case_data, output_path):
    try:
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MetaTrace Report - {case_data.get('case_id', '')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px; }}
        
        h1 {{ color: #1f77b4; margin-bottom: 20px; border-bottom: 3px solid #1f77b4; padding-bottom: 10px; }}
        h2 {{ color: #2ca02c; margin-top: 30px; margin-bottom: 15px; }}
        h3 {{ color: #ff7f0e; margin-top: 20px; margin-bottom: 10px; }}
        
        .case-info {{ background: #e6f2ff; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .case-info p {{ margin: 8px 0; }}
        .case-info strong {{ color: #1f77b4; }}
        
        .file-section {{ background: #f9f9f9; padding: 15px; margin-bottom: 20px; border-left: 4px solid #ff7f0e; border-radius: 3px; }}
        .file-header {{ cursor: pointer; display: flex; justify-content: space-between; align-items: center; user-select: none; }}
        .file-header:hover {{ color: #1f77b4; }}
        .toggle-icon {{ display: inline-block; transition: transform 0.3s; }}
        .toggle-icon.collapsed {{ transform: rotate(-90deg); }}
        .file-content {{ margin-top: 15px; padding: 15px; background: white; border-radius: 3px; }}
        
        .metadata-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 10px 0; }}
        .metadata-item {{ background: #f0f0f0; padding: 10px; border-radius: 3px; }}
        .metadata-item strong {{ color: #333; }}
        .metadata-item p {{ color: #666; font-size: 0.9em; word-break: break-all; }}
        
        .anomaly {{ background: #ffe6e6; padding: 12px; margin: 10px 0; border-left: 3px solid #d9534f; border-radius: 3px; }}
        .anomaly-severity-high {{ border-left-color: #d9534f; }}
        .anomaly-severity-medium {{ border-left-color: #f0ad4e; }}
        
        .correlation {{ background: #e8f5e9; padding: 15px; margin: 15px 0; border-radius: 3px; border-left: 4px solid #2ca02c; }}
        .correlation-confidence {{ display: inline-block; background: #2ca02c; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }}
        
        .hash-display {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; font-size: 0.85em; word-break: break-all; }}
        
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-card.correlations {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.anomalies {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .stat-card.files {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        .stat-number {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
        
        footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; text-align: center; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 MetaTrace Digital Evidence Report</h1>
        
        <div class="case-info">
            <p><strong>Case ID:</strong> {case_data.get('case_id', '')}</p>
            <p><strong>Case Name:</strong> {case_data.get('case_name', '')}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>System:</strong> Windows</p>
        </div>
        
        <div class="stats">
            <div class="stat-card files">
                <div class="stat-number">{case_data.get('total_files', 0)}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card correlations">
                <div class="stat-number">{case_data.get('correlation_count', 0)}</div>
                <div class="stat-label">Correlations</div>
            </div>
            <div class="stat-card anomalies">
                <div class="stat-number">{sum(len(f.get('anomalies', [])) for f in case_data.get('files', []))}</div>
                <div class="stat-label">Anomalies</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([c for c in case_data.get('correlations', []) if c.get('confidence', 0) >= 80])}</div>
                <div class="stat-label">High Confidence</div>
            </div>
        </div>
"""
        
        files_data = case_data.get("files", [])
        for idx, file_data in enumerate(files_data, 1):
            metadata = file_data.get("metadata", {})
            hashes = file_data.get("hashes", {})
            anomalies = file_data.get("anomalies", [])
            
            html_content += f"""
        <h2>Files ({idx}/{len(files_data)})</h2>
        <div class="file-section">
            <div class="file-header" onclick="toggleContent(this)">
                <span><span class="toggle-icon">▶</span> {metadata.get('file_name', 'Unknown')}</span>
                <span style="color: #666; font-size: 0.9em;">{metadata.get('file_size', 0)} bytes</span>
            </div>
            <div class="file-content" style="display: none;">
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <strong>File Path:</strong>
                        <p>{metadata.get('file_path', '')}</p>
                    </div>
                    <div class="metadata-item">
                        <strong>Extension:</strong>
                        <p>{metadata.get('file_extension', '')}</p>
                    </div>
                    <div class="metadata-item">
                        <strong>Created:</strong>
                        <p>{metadata.get('created_time', '')}</p>
                    </div>
                    <div class="metadata-item">
                        <strong>Modified:</strong>
                        <p>{metadata.get('modified_time', '')}</p>
                    </div>
"""
            
            if "pdf_author" in metadata:
                html_content += f"""
                    <div class="metadata-item">
                        <strong>PDF Author:</strong>
                        <p>{metadata.get('pdf_author', '')}</p>
                    </div>
                    <div class="metadata-item">
                        <strong>PDF Producer:</strong>
                        <p>{metadata.get('pdf_producer', '')}</p>
                    </div>
"""
            
            if "word_author" in metadata:
                html_content += f"""
                    <div class="metadata-item">
                        <strong>Word Author:</strong>
                        <p>{metadata.get('word_author', '')}</p>
                    </div>
                    <div class="metadata-item">
                        <strong>Last Modified By:</strong>
                        <p>{metadata.get('word_last_modified_by', '')}</p>
                    </div>
"""
            
            html_content += f"""
                </div>
                
                <h3>Hash Values</h3>
                <div class="hash-display"><strong>MD5:</strong> {hashes.get('md5', '')}</div>
                <div class="hash-display"><strong>SHA256:</strong> {hashes.get('sha256', '')}</div>
"""
            
            if anomalies:
                html_content += f"<h3>⚠️ Anomalies ({len(anomalies)})</h3>"
                for anomaly in anomalies:
                    severity = anomaly.get('severity', 'medium').lower()
                    html_content += f"""<div class="anomaly anomaly-severity-{severity}">
                        <strong>[{severity.upper()}]</strong> {anomaly.get('message', '')}
                    </div>"""
            
            html_content += """
            </div>
        </div>
"""
        
        correlations = case_data.get("correlations", [])
        if correlations:
            html_content += f"""
        <h2>Correlation Analysis ({len(correlations)} found)</h2>
"""
            for corr in correlations:
                html_content += f"""
        <div class="correlation">
            <strong>{corr.get('matched_field', '')}</strong>
            <p>{corr.get('matched_value', '')}</p>
            <p>{corr.get('explanation', '')}</p>
            <span class="correlation-confidence">Confidence: {corr.get('confidence', 0)}%</span>
        </div>
"""
        
        html_content += """
        <footer>
            <p>Generated by MetaTrace Desktop v1.0 | Digital Evidence Analysis Tool</p>
            <p>This report contains sensitive information. Handle with care.</p>
        </footer>
    </div>
    
    <script>
        function toggleContent(header) {
            const content = header.nextElementSibling;
            const icon = header.querySelector('.toggle-icon');
            content.style.display = content.style.display === 'none' ? 'block' : 'none';
            icon.classList.toggle('collapsed');
        }
    </script>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return {"success": True, "message": f"HTML report exported to {output_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
