import os
import sys
import importlib.util
import ast
import platform
import pkg_resources

def get_module_version(module_name):
    """
    Retrieve the version of a module.
    
    Args:
        module_name (str): Name of the module
    
    Returns:
        str: Module version or 'Unknown'
    """
    try:
        return pkg_resources.get_distribution(module_name).version
    except (pkg_resources.DistributionNotFound, pkg_resources.RequirementParseError):
        try:
            # Fallback for some modules that might not be in pkg_resources
            module = importlib.import_module(module_name)
            return getattr(module, '__version__', 'Unknown')
        except (ImportError, AttributeError):
            return 'Unknown'

def detect_modules(script_path, visited_scripts=None):
    """
    Recursively detect and categorize Python modules used in a script and its local imports.
    
    Args:
        script_path (str): Path to the Python script to analyze
        visited_scripts (set, optional): Set of already processed script paths to prevent circular imports
    
    Returns:
        dict: Categorized modules with versions
    """
    # Initialize visited scripts set to track processed files
    if visited_scripts is None:
        visited_scripts = set()
    
    # Prevent processing the same script multiple times
    script_path = os.path.abspath(script_path)
    if script_path in visited_scripts:
        return {'built_in': [], 'third_party': [], 'local': []}
    visited_scripts.add(script_path)
    
    # Categorized modules dictionary
    categorized_modules = {
        'built_in': set(),
        'third_party': {},  # Changed to dict to store versions
        'local': set(),
        'problematic': set(),
    }
    
    # Get the directory of the script
    script_dir = os.path.dirname(script_path)
    
    # Read the script
    try:
        with open(script_path, 'r') as file:
            script_content = file.read()
    except Exception as e:
        print(f"Error reading script {script_path}: {e}")
        return categorized_modules
    
    # Parse the script's AST to find imports
    module_names = set()
    try:
        tree = ast.parse(script_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                module_names.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_names.add(node.module.split('.')[0])
    except SyntaxError:
        print(f"Syntax error parsing script: {script_path}")
        return categorized_modules
    
    # Categorize modules
    for module in module_names:
        # Check built-in modules
        try:
            spec = importlib.util.find_spec(module)
            if spec is None:
                raise Exception(f"Local module {module} not found in {script_dir}")
            
            # Determine module origin
            if spec.origin and 'site-packages' in spec.origin:
                # Third-party module
                version = get_module_version(module)
                categorized_modules['third_party'][module] = version
            elif spec.origin and (
                spec.origin.startswith(sys.prefix) or 
                spec.origin.startswith(sys.base_prefix)
            ):
                # Built-in module
                categorized_modules['built_in'].add(module)
            elif spec.origin == "built-in":
                # Built-in module
                categorized_modules['built_in'].add(module)
            else:
                # Check for local module
                local_module_path = os.path.join(script_dir, module + '.py')
                if os.path.exists(local_module_path):
                    # Local module found
                    categorized_modules['local'].add(module)
                    
                    # Recursively detect modules in the local module
                    local_module_modules = detect_modules(
                        local_module_path, 
                        visited_scripts
                    )
                    
                    # Merge detected modules
                    for category, mods in local_module_modules.items():
                        if category == 'third_party':
                            categorized_modules[category].update(mods)
                        elif category == 'local':
                            categorized_modules[category].update(mods)
                        elif category == 'built_in':
                            categorized_modules[category].update(mods)
                else:
                    # Local module not found
                    raise Exception(f"Local module {module} not found in {script_dir}")
        except Exception as e:
            # If we can't determine the module, skip it
            categorized_modules['problematic'].add(module)
            # print(f"Error processing module {module}: {e}")
    
    return categorized_modules

def print_module_report(modules):
    """
    Print a formatted report of detected modules.
    
    Args:
        modules (dict): Categorized modules
    """
    # Print Python version
    print("Python Version Report:")
    print("-" * 30)
    print(f"Python Implementation: {platform.python_implementation()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Build: {platform.python_build()[0]}")
    print(f"Python Compiler: {platform.python_compiler()}")
    print("\n")
    
    # Print Module Report
    print("Module Usage Report:")
    print("-" * 30)
    
    # Built-in Modules
    print("\nBuilt-in Modules:")
    if modules['built_in']:
        for module in sorted(set(modules['built_in'])):
            print(f"  - {module}")
    else:
        print("  No built-in modules found")
    
    # Third-party Modules with Versions
    print("\nThird-party Modules:")
    if modules['third_party']:
        for module, version in sorted(modules['third_party'].items()):
            print(f"  - {module} (Version: {version})")
    else:
        print("  No third-party modules found")
    
    # Local Modules
    print("\nLocal Modules:")
    if modules['local']:
        for module in sorted(set(modules['local'])):
            print(f"  - {module}")
    else:
        print("  No local modules found")

    # Problematic Modules
    print("\nProblematic Modules:")
    if modules['problematic']:
        for module in sorted(set(modules['problematic'])):
            print(f"  - {module}")
    else:
        print("  No problematic modules found")

def main():
    # Check if script path is provided
    if len(sys.argv) < 2:
        print("Usage: python module_detector.py <path_to_script>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    
    # Detect modules
    detected_modules = detect_modules(script_path)
    
    # Print report
    print_module_report(detected_modules)

if __name__ == "__main__":
    main()