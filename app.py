from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from typing import Any, List

app = Flask(__name__)
app.json.sort_keys = False

def get_matching_mask(df: pd.DataFrame, search_text: str, case: bool = False) -> pd.DataFrame:
    return df.astype(str).apply(
        lambda col: col.str.contains(search_text, na=False, case=case)
    )

def find_matches(df: pd.DataFrame, mask: pd.DataFrame, search_text: str, case_sensitive: bool = False) -> tuple[list, int]:
    match_count = 0
    matches = []
    
    # Search headers
    for col_index, col_header in enumerate(df.columns):
        if case_sensitive:
            found = search_text in col_header
        else:
            found = search_text.lower() in col_header.lower()

        if found:
            matches.append({
                "match_type": "column_header",
                "row": None,
                "col": int(col_index),
                "col_header": col_header,
                "value": col_header
            })
            match_count += 1
    
    # Search individual cells
    rows, cols = np.where(mask)
    
    for row, col in zip(rows, cols):
        matches.append({
            "match_type": "cell",
            "row": int(row), 
            "col": int(col), 
            "col_header": df.columns[col], 
            "value": df.iat[row, col]})
        match_count += 1
        
    return matches, match_count

def validate_data(req_data):
    if not req_data:
        return None, jsonify({"error": "Invalid JSON"}), 400
    
    data = req_data.get("data", [])
    search_text = req_data.get("search_text", "")
    case_sensitive = req_data.get("case_sensitive", False)

    if not data:
        return None, jsonify({"error": "No data provided"}), 400

    if not search_text:
        return None, jsonify({"error": "No search text provided"}), 400

    try:
        df = pd.DataFrame(data)
    except Exception:
        return None, jsonify({"error": "Could not convert data into DataFrame"}), 400
    
    validated_data = {
        "df": df,
        "search_text": search_text,
        "case_sensitive": case_sensitive
    }
    
    return validated_data, None
    
@app.route('/api/search', methods=['POST'])
def search():
    """Searches through tabular data to find any matches.

    Returns:
        Response: A Flask JSON response returning any cell locations matching the search_text.
    """
    req_data = request.get_json()
    
    data, error = validate_data(req_data)
    
    if error:
        return error
    
    df = data["df"] 
    search_text = data["search_text"]
    case_sensitive = data["case_sensitive"]
    
    mask = get_matching_mask(df, search_text, case_sensitive)
    matches, match_count = find_matches(df, mask, search_text, case_sensitive)
    
    response = {
        "matches": matches,
        "match_count": match_count
    }
    
    return jsonify(response)

@app.route('/api/filter', methods=['POST'])
def filter_data():
    """Filters tabular data and returns the filtered DataFrame.

    Returns:
        Response: A Flask JSON response containing the filtered, jsonified DataFrame.
    """
    req_data = request.get_json()
    
    data, error = validate_data(req_data)
    
    if error:
        return error
    
    df = data["df"]
    search_text = data["search_text"]
    case_sensitive = data["case_sensitive"]

    mask = get_matching_mask(df, search_text, case_sensitive)
    filtered_dataframe = df[mask.any(axis=1)]
    
    response = {
        "filtered_data": filtered_dataframe.to_dict(orient="records")
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000)