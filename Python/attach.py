import importlib
import pkg_resources
from typing import List, Optional

core = [
    "dplyr", "climateR", "nhdplusTools", "hydrofab", "zonal", 
    "hfsubsetR", "ngen.hydrofab", "sf", "terra"
]

def core_unloaded() -> List[str]:
    loaded_packages = {pkg.key for pkg in pkg_resources.working_set}
    return [pkg for pkg in core if pkg not in loaded_packages]

def same_library(pkg: str) -> Optional[str]:
    try:
        return importlib.import_module(pkg)
    except ImportError:
        print(f"Package '{pkg}' could not be found.")
        return None

def hydrofabric_attach():
    to_load = core_unloaded()
    
    if not to_load:
        return

    print("Attaching packages:")
    
    versions = {pkg: pkg_resources.get_distribution(pkg).version for pkg in to_load}
    for pkg in to_load:
        version = versions[pkg]
        print(f"{pkg}: {version}")

    for pkg in to_load:
        same_library(pkg)

def package_version(pkg_name: str) -> str:
    version = pkg_resources.get_distribution(pkg_name).version
    version_parts = version.split('.')
    
    # Format version with colors in console (using ANSI escape codes)
    if len(version_parts) > 3:
        version_parts[3:] = [f"\033[91m{part}\033[0m" for part in version_parts[3:]]  # red color
    return ".".join(version_parts)