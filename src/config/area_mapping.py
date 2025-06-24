"""
Area code to SUUMO slug mapping for Tokyo 23 wards.
"""

# Mapping from standard area codes to SUUMO URL slugs
AREA_CODE_TO_SUUMO_SLUG = {
    "13101": "sc_chiyoda",     # 千代田区
    "13102": "sc_chuo",        # 中央区
    "13103": "sc_minato",      # 港区
    "13104": "sc_shinjuku",    # 新宿区
    "13105": "sc_bunkyo",      # 文京区
    "13106": "sc_taito",       # 台東区
    "13107": "sc_sumida",      # 墨田区
    "13108": "sc_koto",        # 江東区
    "13109": "sc_shinagawa",   # 品川区
    "13110": "sc_meguro",      # 目黒区
    "13111": "sc_ota",         # 大田区
    "13112": "sc_setagaya",    # 世田谷区
    "13113": "sc_shibuya",     # 渋谷区
    "13114": "sc_nakano",      # 中野区
    "13115": "sc_suginami",    # 杉並区
    "13116": "sc_toshima",     # 豊島区
    "13117": "sc_kita",        # 北区
    "13118": "sc_arakawa",     # 荒川区
    "13119": "sc_itabashi",    # 板橋区
    "13120": "sc_nerima",      # 練馬区
    "13121": "sc_adachi",      # 足立区
    "13122": "sc_katsushika",  # 葛飾区
    "13123": "sc_edogawa",     # 江戸川区
}


def get_suumo_slug(area_code: str) -> str:
    """
    Get SUUMO slug for a given area code.
    
    Args:
        area_code: Standard area code (e.g., "13113")
        
    Returns:
        SUUMO slug (e.g., "sc_shibuya")
        
    Raises:
        KeyError: If area code is not found in mapping
    """
    if area_code not in AREA_CODE_TO_SUUMO_SLUG:
        raise KeyError(f"Area code '{area_code}' not found in SUUMO mapping")
    return AREA_CODE_TO_SUUMO_SLUG[area_code]


def is_suumo_slug(value: str) -> bool:
    """
    Check if a value is already a SUUMO slug.
    
    Args:
        value: String to check
        
    Returns:
        True if value is a SUUMO slug, False otherwise
    """
    return value.startswith("sc_") and value in AREA_CODE_TO_SUUMO_SLUG.values()