import os
from pathlib import Path
import geopandas as gpd
import pandas as pd
import zipfile
import tempfile

def _zip_uri(zip_path: Path) -> str:
    # Normalize to forward slashes for GDAL
    return f"zip:///{zip_path.as_posix()}"

def read_zipped_shapefile(zip_path: Path) -> gpd.GeoDataFrame:
    """
    Read a zipped shapefile using the 'zip:///<zip>!<inner>.shp' syntax.
    Auto-detects the inner .shp name. Falls back to unzip-to-temp if needed.
    """
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP not found: {zip_path}")

    with zipfile.ZipFile(zip_path) as zf:
        # Find the first .shp inside (handles nested folders)
        shp_members = [m for m in zf.namelist() if m.lower().endswith(".shp")]
        if not shp_members:
            raise ValueError(f"No .shp found in {zip_path.name}. Contents: {zf.namelist()[:10]}...")
        inner_shp = shp_members[0]

    # Try reading via GDAL VFS (fast, no tempfiles)
    zip_vsi = _zip_uri(zip_path) + "!" + inner_shp.replace("\\", "/")
    try:
        return gpd.read_file(zip_vsi)
    except Exception as e:
        print(f"VFS read failed ({e}). Falling back to unzip-to-temp...")

    # Fallback: unzip to a temp dir and read from there (very robust)
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(td)
        shp_path = Path(td) / inner_shp
        return gpd.read_file(shp_path)
    
def make_pa_subset(input_zip: Path, output_dir: Path) -> Path:
    """
    Reads a zipped shapefile, filters Pennsylvania features,
    and writes a GeoParquet subset to the output directory.
    """
    input_path = Path(input_zip)
    output_path = Path(output_dir)
    if not os.path.exists(input_zip):
        raise FileNotFoundError(f"Input file not found: {input_zip}")
    #input_zip = input_zip.replace('\\', '/')
    output_path.mkdir(parents=True, exist_ok=True)
    print(input_zip)
    # Read directly from zip
    gdf = read_zipped_shapefile(input_zip)
    print(f"Loaded {len(gdf)} records from {input_zip}")
    print("Columns:", list(gdf.columns))

    # Try state-first, then ZCTA fallback
    state_cols = ["STATE", "ST", "STUSPS", "STATE_ABBR", "STATEFP", "STATE2", "STATE_NAME"]
    col_hit = next((c for c in state_cols if c in gdf.columns), None)

    if col_hit:
        want_value = "42" if col_hit.upper().endswith("FP") else "PA"
        pa_gdf = gdf[gdf[col_hit].astype(str).str.upper() == want_value]
        suffix = "pa"
        print(f"Filtered by {col_hit}={want_value}: {len(pa_gdf)} records")
    else:
        # ZCTA numeric range (15000–19699) for PA
        code_col = next((c for c in gdf.columns if "ZCTA" in c.upper()), None)
        if not code_col:
            raise ValueError("No state/ZCTA column found; tell me the right column name.")
        zcta_num = pd.to_numeric(gdf[code_col], errors="coerce")
        pa_gdf = gdf[(zcta_num >= 15000) & (zcta_num <= 19699)]
        suffix = "pa_zcta"
        print(f"Filtered ZCTAs 15000–19699 using {code_col}: {len(pa_gdf)} records")

    input_path = Path(input_zip)
    out = os.path.join(output_dir, f"{suffix}_{input_path.stem}.parquet")
    pa_gdf.to_parquet(out)
    print(f"✅ Wrote {len(pa_gdf)} → {out}")
    return out


def main():
    # Base paths
    project_root = os.path.dirname(os.path.dirname(__file__))
    print(project_root)
    print(os.path.dirname(__file__))
    print("*"*88)
    print(project_root)
    data_dir = os.path.join(project_root, "data")
    output_dir =  os.path.join(data_dir, "pa_subsets")

    # Input files
    weather_zip = os.path.join(data_dir, "z_18mr25.zip")
    zcta_zip = os.path.join(data_dir, "tl_2020_us_zcta520.zip")

    # Run subsets
    make_pa_subset(weather_zip, output_dir)
    make_pa_subset(zcta_zip, output_dir)


if __name__ == "__main__":
    main()
