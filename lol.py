import os
import re
import pkg_resources

def get_imports_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    imports = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
    # Extract top-level packages to reduce duplicates and irrelevant submodules
    return set(import_.split('.')[0] for import_ in imports if import_)

def get_imports_from_directory(directory, script_name):
    imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != script_name:
                file_path = os.path.join(root, file)
                file_imports = get_imports_from_file(file_path)
                if file_imports:
                    print(f"Found imports in {file_path}: {file_imports}")
                imports.update(file_imports)
    return imports

def get_module_versions(modules):
    module_versions = {}
    for module in modules:
        if module:  # Ensure module is not an empty string
            try:
                version = pkg_resources.get_distribution(module).version
                module_versions[module] = version
            except pkg_resources.DistributionNotFound:
                print(f"Module {module} not found")
    return module_versions

def write_requirements_txt(module_versions, output_file='requirements.txt'):
    with open(output_file, 'w', encoding='utf-8') as file:
        for module, version in module_versions.items():
            if module:  # Again, check to ensure module is not empty
                file.write(f"{module}=={version}\n")

if __name__ == "__main__":
    directories = ['finsage', 'proj']  # List all directories to scan
    script_name = 'lol.py'  # Name of this script to exclude from analysis
    all_imports = set()

    for directory in directories:
        imports = get_imports_from_directory(directory, script_name)
        all_imports.update(imports)

    print(f"Total unique imports found: {len(all_imports)}")
    module_versions = get_module_versions(all_imports)
    write_requirements_txt(module_versions)
    print(f"requirements.txt generated with {len(module_versions)} modules.")
