import pandas as pd

def compare_with_sector(info, sector_data):

    sector = info.get("sector", "")

    if sector not in sector_data["Sector"].values:
        return None

    row = sector_data[sector_data["Sector"] == sector].iloc[0]

    company_pe = info.get("trailingPE", 0)
    company_roe = info.get("returnOnEquity", 0)

    result = {
        "sector": sector,
        "sector_pe": row["Average_PE"],
        "sector_roe": row["Average_ROE"],
        "company_pe": company_pe,
        "company_roe": company_roe
    }

    return result
