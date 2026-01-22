PROJECT_INFO = {
    "name": "MetaTrace Desktop",
    "version": "1.0",
    "description": "Digital Evidence Metadata Extraction & Correlation Analysis Tool",
    
    "purpose": """
MetaTrace Desktop is a cybersecurity tool designed for digital forensics and metadata analysis.

It extracts comprehensive metadata from multiple file types and automatically finds connections
between files by analyzing:
- Author information (documents)
- Camera/Device data (images)
- Creation software
- Timestamps and suspicious patterns
- File signature validation

Perfect for investigations, digital forensics, and evidence correlation.
    """,
    
    "how_to_use": """
1. SELECT FILES
   - Click "Select Files" to choose individual files
   - Click "Scan Folder" to analyze entire folders (with recursive option)
   - Click "Remove Selected" to remove files from analysis

2. ANALYZE
   - Click "Analyze" to extract metadata and find correlations
   - View results in the tree display
   - Anomalies and correlations appear automatically

3. EXPORT REPORTS
   - JSON: Structured data for further processing
   - CSV: Tabular format for spreadsheets
   - PDF: Professional styled report
   - HTML: Interactive report with collapsible sections

4. VIEW LOGS
   - Click "Project Info" → "View Logs" to see all activities
   - Export logs for integrity verification
    """,
    
    "privacy_and_security": """
PRIVACY POLICY:
- No files are uploaded to external servers (fully local processing)
- Metadata is extracted locally on your machine
- Reports are generated and stored only where you save them
- Email functionality uses your own Gmail credentials
- Logs are stored locally in the /logs folder

DATA HANDLING:
- Files are analyzed but not modified
- Hashes are calculated for integrity verification
- File signatures are validated against known formats
- No metadata is sent anywhere without explicit user action

GMAIL APP PASSWORD:
- Uses Google's 2FA App Passwords (secure method)
- Your actual Gmail password is NEVER used
- Each app password can be revoked independently
- Learn more: https://support.google.com/accounts/answer/185833
    """,
    
    "features": """
✓ Metadata Extraction
  - Images (EXIF data, camera info)
  - Documents (PDF, Word, Excel, PowerPoint)
  - Media files (audio, video metadata)
  - Archives and documents

✓ File Signature Validation
  - Detect fake file extensions
  - Real file type verification
  - Signature mismatch warnings

✓ Anomaly Detection
  - Temporal anomalies (created after modified)
  - Empty files
  - Signature mismatches

✓ Correlation Analysis
  - Same author across files
  - Same device/camera used
  - Same creation software
  - Confidence scoring

✓ Report Generation
  - JSON (structured data)
  - CSV (spreadsheet format)
  - PDF (professional styling)
  - HTML (interactive, collapsible)

✓ Hash Calculation
  - MD5, SHA1, SHA256, SHA512
  - Integrity verification
  - Duplicate detection

✓ Logging System
  - Append-only logs
  - Timestamp tracking
  - Action history
  - Integrity hashing
    """,
    
    "developers": {
        "team": "Cybersecurity Student Project Team",
        "version_info": "v1.0 - Initial Release",
        "built_with": [
            "Python 3.13",
            "Tkinter (GUI)",
            "PyPDF2 (PDF processing)",
            "python-docx (Word documents)",
            "Pillow (Image processing)",
            "ReportLab (PDF generation)",
            "Jinja2 (Report templating)"
        ],
        "contact": "For issues and feedback, refer to project documentation"
    },
    
    "license": "Educational Project - Cybersecurity Assignment",
    
    "keyboard_shortcuts": """
No custom shortcuts currently implemented.
Use mouse to interact with the GUI.
    """
}


def get_info_text(section="full"):
    if section == "full":
        return f"""
{'='*70}
{PROJECT_INFO['name']} v{PROJECT_INFO['version']}
{'='*70}

{PROJECT_INFO['purpose']}

{'='*70}
HOW TO USE
{'='*70}
{PROJECT_INFO['how_to_use']}

{'='*70}
PRIVACY & SECURITY
{'='*70}
{PROJECT_INFO['privacy_and_security']}

{'='*70}
FEATURES
{'='*70}
{PROJECT_INFO['features']}

{'='*70}
DEVELOPERS
{'='*70}
Team: {PROJECT_INFO['developers']['team']}
Version: {PROJECT_INFO['developers']['version_info']}

Built with:
{chr(10).join('  - ' + lib for lib in PROJECT_INFO['developers']['built_with'])}

{'='*70}
        """
    elif section == "purpose":
        return PROJECT_INFO['purpose']
    elif section == "how_to_use":
        return PROJECT_INFO['how_to_use']
    elif section == "privacy":
        return PROJECT_INFO['privacy_and_security']
    elif section == "features":
        return PROJECT_INFO['features']
