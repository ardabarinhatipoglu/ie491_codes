import os
import pandas as pd
from dataretrieval import waterdata

site_no = "USGS-01646500"  # Potomac River near Wash, DC

df, metadata = waterdata.get_continuous(
    monitoring_location_id=site_no,
    parameter_code="00060",        # discharge, cfs
    time="2025-01-01/2026-01-01",  # ISO 8601 interval
    properties=["time", "value", "unit_of_measure", "approval_status"],
    skip_geometry=True,
)

df["value"] = df["value"]*0.02831685
df["unit"] = "m^3/s"
df.drop(columns=["unit_of_measure"], inplace=True)

df["time"] = pd.to_datetime(df["time"])
df = df.set_index("time")
df_hourly = df.value.resample('h').mean()

# Build path to a folder on the Desktop
output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "usgs_data")
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "usgs_data_potomac.csv")
df_hourly = df_hourly.reset_index()
df_hourly.to_csv(output_path, index=False)

print(f"Saved {len(df_hourly)} rows to {output_path}")

