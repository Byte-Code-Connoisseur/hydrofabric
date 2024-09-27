import geopandas as gpd
import os
from shapely.geometry import Polygon
import pandas as pd

def mask_hydrofabric(gpkg: str, mask: gpd.GeoDataFrame, outfile: str = None) -> dict:
    # Load GeoPackage layers
    gdf = gpd.read_file(gpkg, layer=None)
    layers = gdf.keys()

    s_lyrs = [layer for layer in layers if gdf[layer].geometry is not None]
    as_lyrs = [layer for layer in layers if gdf[layer].geometry is None]
    
    hydrofabric = {}
    ids = []

    # Process spatial layers
    for s_lyr in s_lyrs:
        layer_gdf = gpd.read_file(gpkg, layer=s_lyr)
        
        # Transform mask CRS if needed
        if not mask.crs.equals(layer_gdf.crs):
            mask = mask.to_crs(layer_gdf.crs)
        
        # Filter spatial data by mask
        tmp = gpd.sjoin(layer_gdf, mask, how='inner', op='intersects')
        
        # Collect unique IDs
        id_cols = ['COMID', 'FEATUREID', 'divide_id', 'id', 'ds_id', "ID"]
        id_values = tmp[id_cols].apply(pd.Series.dropna, axis=1).unstack().unique()
        ids.append(set(id_values))

        # Write or store results
        if outfile:
            tmp.to_file(outfile, layer=s_lyr, driver='GPKG')
        else:
            hydrofabric[s_lyr] = tmp

    # Process aspatial layers
    all_ids = set.union(*ids)  # Collect all unique IDs
    all_ids = {id_ for id_ in all_ids if pd.notna(id_)}  # Remove NaN values

    for as_lyr in as_lyrs:
        layer_df = gpd.read_file(gpkg, layer=as_lyr)
        
        # Filter by IDs
        filtered_df = layer_df[layer_df['COMID'].isin(all_ids) |
                               layer_df['FEATUREID'].isin(all_ids) |
                               layer_df['divide_id'].isin(all_ids) |
                               layer_df['id'].isin(all_ids) |
                               layer_df['ds_id'].isin(all_ids) |
                               layer_df['ID'].isin(all_ids)]
        
        if outfile:
            filtered_df.to_file(outfile, layer=as_lyr, driver='GPKG')
        else:
            hydrofabric[as_lyr] = filtered_df

    if outfile:
        return outfile
    else:
        return hydrofabric