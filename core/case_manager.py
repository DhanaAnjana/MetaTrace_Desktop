import json
from datetime import datetime
from pathlib import Path
from core.correlation import add_correlations_to_case


def create_case(case_name, files_data):
    case = {
        "case_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "case_name": case_name,
        "created_at": datetime.now().isoformat(),
        "total_files": len(files_data),
        "files": files_data
    }
    
    case = add_correlations_to_case(case)
    return case


def export_case_json(case_data, output_path):
    clean_case = {
        "case_id": case_data["case_id"],
        "case_name": case_data["case_name"],
        "created_at": case_data["created_at"],
        "total_files": case_data["total_files"],
        "files": [],
        "correlations": case_data.get("correlations", []),
        "correlation_count": case_data.get("correlation_count", 0)
    }
    
    for file_entry in case_data["files"]:
        clean_metadata = {}
        for key, value in file_entry["metadata"].items():
            if "error" not in key:
                clean_metadata[key] = value
        
        clean_file = {
            "file_path": file_entry["file_path"],
            "metadata": clean_metadata,
            "hashes": file_entry["hashes"],
            "anomalies": file_entry["anomalies"]
        }
        clean_case["files"].append(clean_file)
    
    try:
        with open(output_path, 'w') as f:
            json.dump(clean_case, f, indent=2)
        return {"success": True, "message": f"Case exported to {output_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_summary(case_data):
    summary = {
        "case_id": case_data["case_id"],
        "case_name": case_data["case_name"],
        "created_at": case_data["created_at"],
        "total_files": case_data["total_files"],
        "total_anomalies": 0,
        "critical_anomalies": 0,
        "files_with_signature_issues": 0
    }
    
    for file_entry in case_data["files"]:
        summary["total_anomalies"] += len(file_entry.get("anomalies", []))
        
        for anomaly in file_entry.get("anomalies", []):
            if anomaly.get("severity") == "high":
                summary["critical_anomalies"] += 1
        
        if not file_entry.get("metadata", {}).get("signature_valid", True):
            summary["files_with_signature_issues"] += 1
    
    return summary
