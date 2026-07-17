# fetch_india.py
# pulls all the data i needed for the india article
# sources: FRED (free, no api key needed), World Bank API, some manual stuff

import json
import subprocess
import os
import pandas as pd
from io import StringIO

OUT = "data/processed"
os.makedirs(OUT, exist_ok=True)

FRED_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
WB_BASE = "https://api.worldbank.org/v2/country/IN/indicator/"


# curl bc requests kept giving me weird ssl errors
def curl(url, timeout=90):
    result = subprocess.run(
        ["curl", "-s", "--max-time", "60", url],
        capture_output=True, text=True, timeout=timeout
    )
    if not result.stdout.strip():
        raise RuntimeError(f"got empty response from: {url}")
    return result.stdout


def get_fred(series_id, date_col, val_col, start="2015-01-01"):
    raw = curl(FRED_BASE + series_id)
    df = pd.read_csv(StringIO(raw), na_values=[".", ""])
    df.columns = [date_col, val_col]
    df[date_col] = pd.to_datetime(df[date_col])
    df = df[df[date_col] >= start].dropna().reset_index(drop=True)
    return df


# world bank returns json with a weird nested structure, data[1] is the actual records
def get_wb(indicator, val_col, start=2015, end=2024):
    url = f"{WB_BASE}{indicator}?format=json&date={start}:{end}&per_page=100"

    for attempt in range(3):
        try:
            raw = curl(url)
            break
        except RuntimeError:
            if attempt == 2:
                print("  skipping " + indicator + ", no data after 3 tries")
                return pd.DataFrame(columns=["year", val_col])

    data = json.loads(raw.encode().decode("utf-8-sig"))
    rows = data[1] if len(data) > 1 and data[1] else []

    records = []
    for r in rows:
        if r.get("value") is not None:
            records.append({"year": int(r["date"]), val_col: float(r["value"])})

    return pd.DataFrame(records).sort_values("year").reset_index(drop=True)


## 1. INR/USD daily exchange rate
# DEXINUS = Indian Rupees per 1 USD on FRED
# higher value = rupee is weaker
print("fetching INR/USD...")
df_inr = get_fred("DEXINUS", "date", "inr_per_usd", start="2015-01-01")
print(f"  range: {df_inr.date.min().date()} to {df_inr.date.max().date()}")
print(f"  first value: {df_inr.iloc[0].inr_per_usd:.2f}, latest: {df_inr.iloc[-1].inr_per_usd:.2f}")
df_inr.to_csv(f"{OUT}/inr_usd.csv", index=False)
print(f"  saved ({len(df_inr)} rows)")


## 2. Brent crude daily price
print("\nfetching brent crude...")
df_brent = get_fred("DCOILBRENTEU", "date", "brent_usd", start="2015-01-01")
print(f"  {df_brent.date.min().date()} to {df_brent.date.max().date()}")
df_brent.to_csv(f"{OUT}/brent.csv", index=False)
print(f"  saved ({len(df_brent)} rows)")


## 3. Oil cost in INR = the double hit chart
# resample both to monthly then merge so dates line up
print("\ncalculating oil in INR...")
inr_monthly = df_inr.set_index("date").resample("ME").last().reset_index()
brent_monthly = df_brent.set_index("date").resample("ME").last().reset_index()

df_oil = pd.merge(inr_monthly, brent_monthly, on="date", how="inner")
df_oil["brent_inr"] = df_oil["inr_per_usd"] * df_oil["brent_usd"]
df_oil[["date", "inr_per_usd", "brent_usd", "brent_inr"]].to_csv(f"{OUT}/oil_inr.csv", index=False)
print(f"  saved oil_inr.csv ({len(df_oil)} rows)")


## 4. India CPI monthly
print("\nfetching india CPI...")
cpi_df = get_fred("INDCPIALLMINMEI", "date", "cpi_index", start="2015-01-01")
cpi_df["cpi_yoy_pct"] = cpi_df["cpi_index"].pct_change(12) * 100
cpi_df = cpi_df.dropna().reset_index(drop=True)
print(f"  peak YoY inflation: {cpi_df.cpi_yoy_pct.max():.1f}%")
cpi_df.to_csv(f"{OUT}/india_cpi.csv", index=False)
print(f"  saved ({len(cpi_df)} rows)")


## 5. current account balance % GDP
print("\nfetching current account...")
df_ca = get_wb("BN.CAB.XOKA.GD.ZS", "current_account_pct_gdp")
df_ca.to_csv(f"{OUT}/current_account.csv", index=False)
print(f"  saved ({len(df_ca)} rows)")


## 6. forex reserves
print("\nfetching forex reserves...")
df_fx = get_wb("FI.RES.TOTL.CD", "forex_reserves_usd")
df_fx["forex_reserves_bn"] = df_fx["forex_reserves_usd"] / 1e9
df_fx[["year","forex_reserves_usd","forex_reserves_bn"]].to_csv(f"{OUT}/forex_reserves.csv", index=False)
print("  saved forex_reserves.csv")


# trade data - need to pull exports and imports separately then combine
print("\nfetching trade data...")
exports = get_wb("BX.GSR.GNFS.CD", "exports_usd")
imports = get_wb("BM.GSR.GNFS.CD", "imports_usd")
df_trade = pd.merge(exports, imports, on="year", how="inner")
df_trade["trade_balance_usd"] = df_trade["exports_usd"] - df_trade["imports_usd"]
df_trade["exports_bn"] = df_trade["exports_usd"] / 1e9
df_trade["imports_bn"] = df_trade["imports_usd"] / 1e9
df_trade["balance_bn"] = df_trade["trade_balance_usd"] / 1e9
df_trade.to_csv(f"{OUT}/trade.csv", index=False)
print("  saved trade.csv, balance each year:")
for _, row in df_trade.iterrows():
    print("    " + str(int(row.year)) + ": $" + f"{row.balance_bn:.0f}B")


## fuel import share
print("\nfetching fuel imports share...")
df_fuel = get_wb("TM.VAL.FUEL.ZS.UN", "fuel_imports_pct")
df_fuel.to_csv(f"{OUT}/fuel_imports.csv", index=False)
print(f"  saved ({len(df_fuel)} rows)")


## FDI net inflows
print("\nfetching FDI...")
df_fdi = get_wb("BX.KLT.DINV.CD.WD", "fdi_usd")
df_fdi["fdi_bn"] = df_fdi["fdi_usd"] / 1e9
df_fdi[["year","fdi_usd","fdi_bn"]].to_csv(f"{OUT}/fdi.csv", index=False)
print(f"  saved ({len(df_fdi)} rows)")


# LPG cylinder prices - had to collect these manually from PPAC website
# PPAC = Petroleum Planning and Analysis Cell, Ministry of Petroleum
# 14.2kg cylinder in Delhi, non-subsidised market price
print("\nsaving LPG prices (manual)...")
lgp_data = [
    # year, month, price_inr, notes
    (2015, 1,  419,  ""),
    (2016, 1,  495,  ""),
    (2017, 1,  591,  ""),
    (2018, 1,  715,  ""),
    (2018, 9,  858,  "peak 2018"),
    (2019, 1,  694,  "eased a bit"),
    (2020, 1,  714,  ""),
    (2020, 5,  581,  "covid - global oil demand crashed"),
    (2021, 2,  769,  ""),
    (2021, 7,  834,  ""),
    (2022, 3,  899,  "russia ukraine"),
    (2022, 7, 1053,  "all time high"),
    (2023, 8,  903,  "govt cut Rs200, pre-election"),
    (2024, 3,  803,  ""),
    (2024, 8,  829,  ""),
    (2025, 4,  853,  "latest i could find"),
]
df_lgp = pd.DataFrame(lgp_data, columns=["year","month","lgp_price_inr","note"])
df_lgp["date"] = pd.to_datetime(df_lgp[["year","month"]].assign(day=1))
df_lgp.to_csv(f"{OUT}/lgp_prices.csv", index=False)
print(f"  saved ({len(df_lgp)} rows)")


# gold import duty - pulled from ministry of finance budget docs
print("saving gold duty (manual)...")
gold_raw = [
    (2015, 1,  10.0,   "held at 10% since 2013 CAD crisis"),
    (2019, 7,  12.5,   "budget 2019 hike"),
    (2021, 2,  10.75,  "slight rollback + agri cess"),
    (2022, 7,  15.0,   "raised to 15% + cess = ~18.45% effective"),
    (2024, 7,   6.0,   "budget 2024 surprise cut"),
    (2025, 2,   6.0,   "maintained"),
]
df_gold = pd.DataFrame(gold_raw, columns=["year","month","duty_pct","note"])
df_gold["date"] = pd.to_datetime(df_gold[["year","month"]].assign(day=1))
df_gold.to_csv(f"{OUT}/gold_duty.csv", index=False)
print(f"  saved ({len(df_gold)} rows)")

print("\ndone, everything in data/processed/")
