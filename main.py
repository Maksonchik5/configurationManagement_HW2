#!/bin/python3

import subprocess
import yaml
import re
from pathlib import Path

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_dependencies(package, max_depth, current_depth=0, dependencies=None):
    if dependencies is None:
        dependencies = {}

    if current_depth >= max_depth:
        return dependencies
    
    result = subprocess.run(
        ["apt-cache", "depends", package],
        capture_output=True,
        text=True
    )
    
    dependencies[package] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("Depends:"):
            dep = line.split(" ")[1]
            dependencies[package].append(dep)
            if dep not in dependencies:
                get_dependencies(dep, max_depth, current_depth + 1, dependencies)

    return dependencies

def generate_mermaid_graph(dependencies):
    lines = ["graph TD"]
    for package, deps in dependencies.items():
        for dep in deps:
            dep = re.sub(r'[<>]', '', dep)
            lines.append(f"{package} --> {dep}")
    return "\n".join(lines)

def save_mermaid_to_png(mermaid_text, output_path, visualizer_path):
    with open("temp.mmd", "w") as file:
        file.write(mermaid_text)
    
    subprocess.run([visualizer_path, "-i", "temp.mmd", "-o", output_path])
    Path("temp.mmd").unlink()  # Удаляем временный файл после использования

def main():
    config_path = "config.yaml"
    config = load_config(config_path)
    
    dependencies = get_dependencies(
        config['package'],
        config['max_depth']
    )
    
    mermaid_text = generate_mermaid_graph(dependencies)
    print(f'Mermaid_Dependencies for {config["package"]}, depth = {config["max_depth"]}\n{mermaid_text}')
    save_mermaid_to_png(
        mermaid_text,
        config['output_path'],
        config['visualizer_path']
    )
    
    print("Граф зависимостей успешно сохранён в", config['output_path'])

if __name__ == "__main__":
    main()

