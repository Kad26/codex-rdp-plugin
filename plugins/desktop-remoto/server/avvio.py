import os
from pathlib import Path
import site
import sys


STATE_DIR = Path(os.environ.get("CODEX_DESKTOP_RDP_STATE") or (
    Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "CodexDesktopRemoto"
))


def main():
    runtime = STATE_DIR / "runtime-v1"
    if not runtime.is_dir():
        sys.exit("Esegui Installa.ps1 per preparare il runtime di Desktop remoto RDP.")

    site.addsitedir(str(runtime))
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    if sys.argv[1:]:
        from profilo import configure_cli

        configure_cli(STATE_DIR)
    else:
        from mcp_rdp import run

        run(STATE_DIR)


if __name__ == "__main__":
    main()
