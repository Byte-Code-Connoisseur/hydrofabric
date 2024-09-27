import geopandas as gpd
import pandas as pd
import os
from datetime import datetime

# Function to read a QML file
def read_qml(qml_file):
    """
    Reads in a QML file.
    
    Parameters:
    qml_file (str): Path to the QML file
    
    Returns:
    str: Contents of the QML file as a string
    """
    with open(qml_file, 'r') as file:
        return file.read()

# Function to create a style row (as a pandas DataFrame row)
def create_style_row(gpkg_path, layer_name, style_name, style_qml):
    """
    Creates a style row for the layer.
    
    Parameters:
    gpkg_path (str): Path to the GeoPackage
    layer_name (str): Name of the layer
    style_name (str): Name of the style
    style_qml (str): QML style content
    
    Returns:
    pd.DataFrame: DataFrame representing the style row
    """
    query = f"SELECT column_name FROM gpkg_geometry_columns WHERE table_name = '{layer_name}'"
    geom_col = gpd.read_postgis(query, con=gpkg_path).iloc[0, 0]
    
    return pd.DataFrame({
        'f_table_catalog': [""],
        'f_table_schema': [""],
        'f_table_name': [layer_name],
        'f_geometry_column': [geom_col],
        'styleName': [style_name],
        'styleQML': [style_qml],
        'styleSLD': [""],
        'useAsDefault': [True],
        'description': ["Generated for hydrofabric"],
        'owner': [""],
        'ui': [None],
        'update_time': [datetime.now()]
    })

# Function to append style to GPKG
def append_style(gpkg_path, qml_dir=None, layer_names=None):
    """
    Appends styles to a GeoPackage.
    
    Parameters:
    gpkg_path (str): Path to the GeoPackage
    qml_dir (str): Directory path to the QML files
    layer_names (list): List of layer names to populate
    
    Returns:
    str: Path to the GeoPackage with the appended styles
    """
    # Default qml_dir if not provided
    if qml_dir is None:
        qml_dir = os.path.join(os.path.dirname(__file__), 'qml')
    
    # Find QML files and corresponding layers
    qml_files = [f for f in os.listdir(qml_dir) if f.endswith('.qml')]
    good_layers = [os.path.splitext(os.path.basename(f))[0] for f in qml_files]
    
    # Filter layer names to only those with matching QML files
    layer_names = [layer for layer in layer_names if layer in good_layers]
    files = [os.path.join(qml_dir, f"{layer}.qml") for layer in layer_names]
    
    # Read QML files and create style names
    styles = [read_qml(file) for file in files]
    style_names = [f"{layer}__hydrofabric_style" for layer in layer_names]
    
    # Create style rows
    style_rows = pd.concat(
        [create_style_row(gpkg_path, layer, style_name, style) 
         for layer, style_name, style in zip(layer_names, style_names, styles)]
    )
    
    # Check if "layer_styles" exists, and delete if necessary
    layers = gpd.read_file(gpkg_path, layer=None)
    if "layer_styles" in layers:
        gpd.io.file.fiona.drvsupport.supported_drivers['GPKG'] = 'rw'
        with fiona.open(gpkg_path, 'r+') as src:
            src.remove('layer_styles')

    # Write the new styles to the GPKG
    if not style_rows.empty:
        style_rows.to_file(gpkg_path, layer='layer_styles', driver='GPKG')

    return gpkg_path
