import pandas as pd
import os
import config
from modules.geocoder import convert_address
from modules.geo_checker import GeoValidator
from modules.address_parser import extract_ward, extract_address_parts


def split_addresses():
    """Tách địa chỉ từ input.xlsx và lưu vào split_addresses.xlsx."""
    print("Splitting addresses...")
    df = pd.read_excel(config.INPUT_PATH)
    split_results = []
    
    for idx, row in df.iterrows():
        addr = row['Address']
        addr_parts = extract_address_parts(addr)
        
        split_results.append({
            'Original_Address': addr,
            'Street_Address': addr_parts['street'],
            'Ward_District': addr_parts['ward'],
            'District': addr_parts['district'],
            'City': addr_parts['city']
        })
        
        if (idx + 1) % 50 == 0:
            print(f"  Split {idx + 1}/{len(df)} addresses")
    
    pd.DataFrame(split_results).to_excel(config.SPLIT_PATH, index=False)
    print(f"✓ Split completed! Saved to: {config.SPLIT_PATH}\n")
    return split_results


def load_existing_results():
    if os.path.exists(config.OUTPUT_PATH):
        try:
            existing_df = pd.read_excel(config.OUTPUT_PATH)
            results = existing_df.to_dict('records')
            start_index = len(existing_df)
            print(f"Resuming from row {start_index + 1}...")
            return results, start_index
        except Exception as e:
            print(f"Warning: Could not read existing output file: {e}")
            return [], 0
    return [], 0


def process_address(row, validator):
    addr = row['Address']
    old_ward = extract_ward(addr)
    addr_parts = extract_address_parts(addr)
    
    data = convert_address(addr, retries=5)
    
    if data and data.get('address_latitude'):
        api_ward = data.get('address_ward', 'N/A')
        lat, lon = data['address_latitude'], data['address_longitude']
        response_time = data.get('response_time', 'N/A')
        
        geo_ward = validator.find_ward_geo(lat, lon)
        note = validator.get_merging_note(api_ward)
        
        status = "MISMATCH"
        if api_ward.lower() == geo_ward.lower():
            status = "MATCH"
            if old_ward.lower() in note.lower():
                status = "MATCH (Confirmed Merger)"
        
        return {
            'Original_Address': addr,
            'Street_Address': addr_parts['street'],
            'Ward_District': addr_parts['ward'],
            'District': addr_parts['district'],
            'City': addr_parts['city'],
            'Old_Ward_Split': old_ward,
            'New_Ward_API': api_ward,
            'Geo_Ward_Verify': geo_ward,
            'Status': status,
            'Merging_Note': note,
            'Response_Time_Sec': response_time,
            'Lat': lat, 'Lon': lon
        }
    else:
        return {
            'Original_Address': addr,
            'Street_Address': addr_parts['street'],
            'Ward_District': addr_parts['ward'],
            'District': addr_parts['district'],
            'City': addr_parts['city'],
            'Status': "API_FAIL",
            'Response_Time_Sec': 'N/A',
            'Error_Note': 'API failed after 5 retries'
        }


def save_results(results, current_count, total_count):
    pd.DataFrame(results).to_excel(config.OUTPUT_PATH, index=False)
    print(f"✓ Saved {current_count}/{total_count} rows")


def run_tool(batch_size=10):
    print("Starting Professional Address Verification Tool...")
    
    # Step 1: Split addresses
    split_addresses()
    
    # Step 2: Load input
    df = pd.read_excel(config.INPUT_PATH)
    validator = GeoValidator()
    
    results, start_index = load_existing_results()
    
    for idx, (_, row) in enumerate(df.iloc[start_index:].iterrows(), start=start_index):
        print(f"[{idx + 1}/{len(df)}] Processing: {row['Address'][:50]}...")
        result = process_address(row, validator)
        results.append(result)
        
        if (idx + 1) % batch_size == 0:
            save_results(results, idx + 1, len(df))

    save_results(results, len(df), len(df))
    print(f"Total processed: {len(results)}")
