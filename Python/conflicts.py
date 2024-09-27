import importlib
import inspect
from collections import defaultdict
from typing import List, Dict, Optional

core = ["dplyr", "climateR", "nhdplusTools", "hydrofab", "zonal", 
        "hfsubsetR", "ngen.hydrofab", "sf", "terra"]

def ls_env(module_name: str) -> List[str]:
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return []
    
    x = dir(module)

    # Simulate removing specific functions based on environment
    if module_name in ["dplyr", "lubridate"]:
        x = [item for item in x if item not in ["intersect", "setdiff", "setequal", "union"]]
    
    if module_name == "lubridate":
        x = [item for item in x if item not in ["as_difftime", "date"]]
    
    return x

def hydrofabric_conflicts(only: Optional[List[str]] = None) -> Dict[str, List[str]]:
    # Get list of loaded modules (simulating environments)
    loaded_modules = list(sys.modules.keys())
    
    if only:
        only = set(only).union(core)
        loaded_modules = [mod for mod in loaded_modules if mod in only]

    # Check objects across environments and find conflicts
    objs = defaultdict(list)
    
    for module_name in loaded_modules:
        module_objects = ls_env(module_name)
        for obj in module_objects:
            objs[obj].append(module_name)
    
    # Find conflicts (objects that exist in more than one module)
    conflicts = {k: v for k, v in objs.items() if len(v) > 1}

    # Filter conflicts involving core hydrofabric packages
    hydrofabric_pkgs = [pkg for pkg in loaded_modules if pkg in core]
    conflicts = {k: v for k, v in conflicts.items() if any(pkg in hydrofabric_pkgs for pkg in v)}

    # Filter out common base libraries and return conflicts
    excluded_pkgs = {'hydrofabric', 'base', 'stats', 'graphics', 'utils', 'grDevices', 'testthat'}
    filtered_conflicts = {k: [pkg for pkg in v if pkg not in excluded_pkgs] for k, v in conflicts.items()}
    
    return {k: v for k, v in filtered_conflicts.items() if len(v) > 1}

def hydrofabric_conflict_message(conflicts: Dict[str, List[str]]) -> str:
    if not conflicts:
        return ""
    
    header = "Conflicts:\n"
    bullets = []
    
    for func, pkgs in conflicts.items():
        winner = pkgs[0]
        others = pkgs[1:]
        bullet = f"{winner}::{func}() masks {', '.join(f'{pkg}::{func}()' for pkg in others)}"
        bullets.append(bullet)
    
    return header + "\n".join(bullets)

def print_hydrofabric_conflicts(conflicts: Dict[str, List[str]], startup: bool = False) -> None:
    message = hydrofabric_conflict_message(conflicts)
    print(message)

def confirm_conflict(packages: List[str], name: str) -> Optional[List[str]]:
    objs = []
    
    # Retrieve functions dynamically from the loaded packages
    for pkg in packages:
        try:
            module = importlib.import_module(pkg)
            obj = getattr(module, name, None)
            if callable(obj):
                objs.append(obj)
        except ImportError:
            continue

    # Filter out identical functions (based on memory address comparison)
    if len(objs) > 1:
        unique_objs = list({id(obj): obj for obj in objs}.values())
        if len(unique_objs) > 1:
            return packages
    
    return None

"""Example usage
conflicts = hydrofabric_conflicts()
print_hydrofabric_conflicts(conflicts)"""
