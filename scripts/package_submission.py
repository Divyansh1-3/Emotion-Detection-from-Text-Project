"""Build a verified source archive without secrets or machine-specific state."""
import argparse
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package(output: Path):
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    files = []
    for name in filter(None, tracked):
        path = Path(name)
        if (any(part in {'.git', '.venv', 'venv', '__pycache__', 'logs', '.tools'} for part in path.parts)
            or (path.name.startswith('.env') and path.name != '.env.example')
            or path.suffix.lower() in {'.db', '.sqlite3', '.zip', '.pyc', '.bin', '.safetensors'}):
            raise ValueError(f'Unsafe tracked file: {name}')
        data = (ROOT / path).read_bytes()
        if path.suffix in {'.py', '.md', '.txt', '.js', '.json', '.yaml', '.yml'} or path.name == '.env.example':
            if re.search(rb'AIza[\w-]{30,}|sk-[A-Za-z0-9_-]{30,}', data):
                raise ValueError(f'Possible credential in {name}')
        files.append((name, data))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files:
            archive.writestr(ROOT.name + '/' + name, data)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Archive integrity check failed')
    print(f'Verified archive: {len(files)} files, {output.stat().st_size:,} bytes: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    package(parser.parse_args().output.resolve())
