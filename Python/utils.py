import sys
import pkg_resources
import importlib

# Helper function to print messages in different contexts
def msg(*args, startup=False):
    """
    Prints messages with different behavior depending on startup context.

    Parameters:
    args (str): Message to be printed.
    startup (bool): If True, prints message only if the quiet mode is not enabled.
    """
    if startup:
        if not is_hydrofabric_quiet():
            print(text_col(*args), file=sys.stderr)
    else:
        print(text_col(*args))

# Helper function to check if hydrofabric quiet mode is enabled (dummy implementation)
def is_hydrofabric_quiet():
    # For Python, we assume this checks an environmental variable or configuration option
    return False  # Replace with actual logic if needed

# Helper function to color messages
def text_col(*args):
    """
    Colors text based on the terminal's theme (simulating the behavior of RStudio in Python).
    """
    theme = get_theme_info()
    text = ' '.join(map(str, args))
    if theme.get('dark', False):
        return colored(text, 'white')
    else:
        return colored(text, 'black')

# Simulate a function to get theme info (for Python terminal)
def get_theme_info():
    # Placeholder: implement logic to check terminal theme if necessary
    # For now, assume a light theme.
    return {'dark': False}

# Dummy color function (crayon::white/black equivalent in Python)
def colored(text, color):
    """
    Colors text in the terminal based on color. You can use libraries like termcolor or colorama.
    """
    from termcolor import colored as term_colored
    return term_colored(text, color)

# Function to list all packages imported by a specific module (equivalent to hydrofabric_packages)
def hydrofabric_packages(include_self=True):
    """
    Lists all packages imported by hydrofabric or another package.

    Parameters:
    include_self (bool): If True, includes the package itself in the list.
    
    Returns:
    list: Names of the packages.
    """
    # Get the list of imported packages
    package_name = 'hydrofabric'  # Replace with the actual package name if different
    try:
        package = importlib.import_module(package_name)
        distribution = pkg_resources.get_distribution(package_name)
        imports = distribution.requires()
        
        # Filter out specific packages
        names = [str(req).split()[0] for req in imports if str(req).split()[0] not in ['purrr', 'cli', 'crayon', 'rstudioapi']]
        
        if include_self:
            names.append(package_name)
        
        return names
    except pkg_resources.DistributionNotFound:
        print(f"Package '{package_name}' not found.")
        return []

# Invert function to invert a dictionary (similar to R's invert function)
def invert(d):
    """
    Inverts a dictionary of lists, mapping values back to keys.

    Parameters:
    d (dict): Dictionary to invert.
    
    Returns:
    dict: Inverted dictionary.
    """
    if not d:
        return {}
    
    inverted = {}
    for key, values in d.items():
        for value in values:
            inverted.setdefault(value, []).append(key)
    
    return inverted

# Function to create grey-styled text (equivalent to style_grey)
def style_grey(level, *args):
    """
    Styles text with a grey color depending on the level.

    Parameters:
    level (float): Grey intensity level.
    args (str): Text to style.
    
    Returns:
    str: Styled text.
    """
    from termcolor import colored
    text = ' '.join(map(str, args))
    grey_color = f"grey{int(level * 100)}"  # Approximation for grey level
    return colored(text, grey_color)