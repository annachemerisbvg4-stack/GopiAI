import os
import re


def find_all_imports(root_dir="gopiai"):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if re.match(r"\s*(import |from )", line):
                                print(f"{filepath}:{i}: {line.strip()}")
                except Exception as e:
                    print(f"Ошибка при чтении {filepath}: {e}")


if __name__ == "__main__":
    find_all_imports("gopiai")
