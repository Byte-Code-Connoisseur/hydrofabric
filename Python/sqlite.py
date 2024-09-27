import sqlite3
import pandas as pd
import geopandas as gpd

# Function to connect to GeoPackage as SQLite and list layers or retrieve a specific layer
def as_sqlite(gpkg, lyr=None, ignore="gpkg_|rtree_|sqlite_"):
    """
    Connects to a GeoPackage (GPKG) as an SQLite database and optionally retrieves a layer.

    Parameters:
    gpkg (str): Path to the GeoPackage
    lyr (str, optional): Specific layer to retrieve, defaults to None
    ignore (str, optional): Pattern for layers to be ignored, defaults to "gpkg_|rtree_|sqlite_"
    
    Returns:
    sqlite3.Connection: SQLite connection to the GeoPackage
    """
    conn = sqlite3.connect(gpkg)
    cursor = conn.cursor()
    
    # If no specific layer is provided, list all the tables except those matching the ignore pattern
    if lyr is None:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        tables = [table for table in tables if not pd.Series(table).str.contains(ignore).any()]
        print(tables)
        conn.close()
        return None
    else:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        if lyr in tables:
            return conn
        else:
            conn.close()
            raise ValueError(f"{lyr} not in gpkg.")
    
    return conn

# Function to extract spatial data from an SQLite connection
def read_sf_dataset_sqlite(conn, lyr):
    """
    Extracts spatial data from an SQLite connection.

    Parameters:
    conn (sqlite3.Connection): SQLite connection to the GeoPackage
    lyr (str): Layer name to extract
    
    Returns:
    gpd.GeoDataFrame or pd.DataFrame: GeoDataFrame if spatial, DataFrame if non-spatial
    """
    # Get the spatial reference system information
    query = "SELECT * FROM gpkg_spatial_ref_sys"
    srs = pd.read_sql(query, conn).iloc[-1]  # Get the last row (slicing as in R)

    # Read the layer data
    query = f"SELECT * FROM {lyr}"
    data = pd.read_sql(query, conn)
    
    # Check if there is a geometry column
    if 'geom' in data.columns or 'geometry' in data.columns:
        # Convert to GeoDataFrame using the spatial reference system
        crs = srs['definition']
        gdf = gpd.GeoDataFrame(data, geometry='geom' if 'geom' in data.columns else 'geometry', crs=crs)
        return gdf
    else:
        print("Warning: no simple features geometry column present")
        return data