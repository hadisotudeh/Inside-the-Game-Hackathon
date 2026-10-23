"""Create a secret-free App Service ZIP from runtime files and Pipenv's lock."""

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[1]
    lock = json.loads((root / "Pipfile.lock").read_text())
    requirements = []
    for name, package in sorted(lock["default"].items()):
        requirement = name + package["version"]
        if package.get("markers"):
            requirement += "; " + package["markers"]
        requirements.append(requirement)
    output = root / ".demo-production" / "azure" / "touchline.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted((root / "app").rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                if path.suffix in {
                    ".py",
                    ".html",
                    ".css",
                    ".js",
                    ".json",
                    ".svg",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                    ".ico",
                }:
                    archive.write(path, path.relative_to(root))
        archive.writestr("requirements.txt", "\n".join(requirements) + "\n")
    print(output)


if __name__ == "__main__":
    main()
