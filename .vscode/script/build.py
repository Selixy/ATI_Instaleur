# .vscode/script/build.py
import shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "ATI_Instaleur.spec"
OUT = ROOT / "build"

def run(cmd):
    print("+", " ".join(map(str, cmd)))
    subprocess.check_call(cmd)

def main():
    if OUT.exists():
        shutil.rmtree(OUT)

    distpath = OUT / "dist"
    workpath = OUT / "work"

    run([
        sys.executable, "-m", "PyInstaller",
        str(SPEC),
        "--distpath", str(distpath),
        "--workpath", str(workpath),
        "--clean",
        "--noconfirm"
    ])

    root_exe = distpath / "ATI_Instaleur.exe"
    if root_exe.exists():
        root_exe.unlink()

    print(f"\n Build terminé -> {distpath/'ATI_Instaleur'}")
    

if __name__ == "__main__":
    main()
