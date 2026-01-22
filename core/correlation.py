def get_all_metadata_fields(metadata):
    fields = {}
    
    for key, value in metadata.items():
        if key not in ["file_name", "file_path", "file_size", "created_time", "modified_time", "file_extension", "signature_valid", "signature_warning", "image_error", "pdf_error", "office_error", "word_paragraphs", "excel_sheets", "pptx_slides"]:
            fields[key] = value if value else ""
    
    return fields


def find_matching_metadata(files_data):
    correlations = []
    
    if len(files_data) < 2:
        return correlations
    
    all_metadata = {}
    for idx, file_entry in enumerate(files_data):
        metadata = file_entry.get("metadata", {})
        fields = get_all_metadata_fields(metadata)
        
        for field_name, field_value in fields.items():
            if field_value and field_value not in ["N/A", ""]:
                field_key = f"{field_name}:{field_value}"
                
                if field_key not in all_metadata:
                    all_metadata[field_key] = []
                all_metadata[field_key].append({
                    "file_idx": idx,
                    "file_name": metadata.get("file_name", "Unknown"),
                    "field_name": field_name,
                    "field_value": field_value
                })
    
    for field_key, matches in all_metadata.items():
        if len(matches) > 1:
            field_name = matches[0]["field_name"]
            field_value = matches[0]["field_value"]
            file_indices = [m["file_idx"] for m in matches]
            file_names = [m["file_name"] for m in matches]
            
            confidence = min(95, 50 + (len(matches) * 15))
            
            correlation = {
                "type": "metadata_match",
                "matched_field": field_name,
                "matched_value": str(field_value)[:80],
                "file_count": len(matches),
                "file_indices": file_indices,
                "files": file_names,
                "confidence": confidence,
                "explanation": f"{len(matches)} files share {field_name}: '{field_value}'. These files are likely related."
            }
            correlations.append(correlation)
    
    return correlations


def find_device_correlation(files_data):
    correlations = []
    devices = {}
    
    for idx, file_entry in enumerate(files_data):
        metadata = file_entry.get("metadata", {})
        device_key = None
        device_info = None
        
        if "exif_Make" in metadata and "exif_Model" in metadata:
            device_key = f"{metadata['exif_Make']}_{metadata['exif_Model']}"
            device_info = f"{metadata['exif_Make']} {metadata['exif_Model']}"
        
        if device_key:
            if device_key not in devices:
                devices[device_key] = {"info": device_info, "indices": []}
            devices[device_key]["indices"].append(idx)
    
    for device_key, device_data in devices.items():
        file_indices = device_data["indices"]
        if len(file_indices) > 1:
            confidence = min(98, 60 + (len(file_indices) * 12))
            
            correlation = {
                "type": "device_match",
                "matched_value": device_data["info"],
                "file_count": len(file_indices),
                "file_indices": file_indices,
                "confidence": confidence,
                "explanation": f"{len(file_indices)} photos taken with {device_data['info']}. Same camera/device used."
            }
            correlations.append(correlation)
    
    return correlations


def find_software_correlation(files_data):
    correlations = []
    software = {}
    
    for idx, file_entry in enumerate(files_data):
        metadata = file_entry.get("metadata", {})
        
        creator_software = None
        
        if "pdf_producer" in metadata:
            creator_software = metadata.get("pdf_producer")
        elif "pdf_creator" in metadata:
            creator_software = metadata.get("pdf_creator")
        
        if creator_software and creator_software != "N/A":
            if creator_software not in software:
                software[creator_software] = []
            software[creator_software].append(idx)
    
    for soft, file_indices in software.items():
        if len(file_indices) > 1:
            confidence = min(85, 45 + (len(file_indices) * 10))
            
            correlation = {
                "type": "software_match",
                "matched_value": soft,
                "file_count": len(file_indices),
                "file_indices": file_indices,
                "confidence": confidence,
                "explanation": f"{len(file_indices)} files created with {soft}. Same software used to create files."
            }
            correlations.append(correlation)
    
    return correlations


def find_timestamp_patterns(files_data):
    correlations = []
    timestamps = {}
    
    for idx, file_entry in enumerate(files_data):
        metadata = file_entry.get("metadata", {})
        created_time = metadata.get("created_time")
        
        if created_time:
            if created_time not in timestamps:
                timestamps[created_time] = []
            timestamps[created_time].append(idx)
    
    for timestamp, file_indices in timestamps.items():
        if len(file_indices) > 1:
            correlation = {
                "type": "timestamp_pattern",
                "matched_value": timestamp,
                "file_count": len(file_indices),
                "file_indices": file_indices,
                "confidence": 75,
                "explanation": f"{len(file_indices)} files created at exact same time ({timestamp}). Suspicious timestamp pattern detected."
            }
            correlations.append(correlation)
    
    return correlations


def analyze_correlations(case_data):
    files_data = case_data.get("files", [])
    
    all_correlations = find_matching_metadata(files_data)
    all_correlations.sort(key=lambda x: x["confidence"], reverse=True)
    
    return all_correlations


def add_correlations_to_case(case_data):
    correlations = analyze_correlations(case_data)
    case_data["correlations"] = correlations
    case_data["correlation_count"] = len(correlations)
    
    return case_data
