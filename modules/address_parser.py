def extract_address_parts(address):
    """Split address into components by comma: street_addr, ward, district, city."""
    try:
        if not address or str(address).strip() == "" or str(address) == "nan":
            return {"street": "N/A", "ward": "N/A", "district": "N/A", "city": "N/A"}
        
        addr_str = str(address).strip()
        parts = [p.strip() for p in addr_str.split(',')]
        
        result = {"street": "N/A", "ward": "N/A", "district": "N/A", "city": "N/A"}
        
        if len(parts) >= 1:
            result["street"] = parts[0]
        if len(parts) >= 2:
            result["ward"] = parts[1]
        if len(parts) >= 3:
            result["district"] = parts[2]
        if len(parts) >= 4:
            result["city"] = parts[3]
        
        return result
        
    except Exception as e:
        print(f"Error parsing address: {e}")
        return {"street": "N/A", "ward": "N/A", "district": "N/A", "city": "N/A"}


def extract_ward(address):
    try:
        if not address or str(address).strip() == "" or str(address) == "nan": 
            return "N/A"
            
        addr_str = str(address).strip()
        parts = [p.strip() for p in addr_str.split(',')]
        
        ward_keywords = ["Phường", "Phuong", "P.", "Xã", "Xa", "X.", "Thị trấn", "Thi tran", "TT."]
        district_keywords = ["Quận", "Quan", "Q.", "Huyện", "Huyen", "H.", "TP."]
        
        for part in reversed(parts):
            part_lower = part.lower()
            if any(keyword.lower() in part_lower for keyword in ward_keywords):
                ward_part = part
                for keyword in ward_keywords:
                    if keyword.lower() in part_lower:
                        idx = part_lower.find(keyword.lower())
                        ward_part = part[idx:]
                        break
                if ward_part.strip():
                    return ward_part.strip()
        
        for part in parts:
            part_lower = part.lower()
            if any(keyword.lower() in part_lower for keyword in district_keywords):
                for keyword in district_keywords:
                    if keyword.lower() in part_lower:
                        idx = part_lower.find(keyword.lower())
                        remainder = part[idx + len(keyword):].strip()
                        if remainder:
                            return remainder.split()[0] if remainder else "N/A"
                        break
                        
    except Exception as e:
        print(f"Error parsing address: {e}")
        
    return "N/A"