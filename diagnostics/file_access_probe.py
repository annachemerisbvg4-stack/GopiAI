from pathlib import Path
import json
import os
import sys

def p(*a): 
    print(*a, flush=True)

def main():
    p("=== FILE ACCESS PROBE ===")
    p("CWD:", os.getcwd())
    p("HOME:", os.environ.get("HOME") or os.path.expanduser("~"))
    # UID/GID доступны не на всех платформах (например, отсутствуют в Windows).
    # Используем безопасную проверку наличия атрибутов, чтобы избежать ошибок статического анализа (Pyright)
    # и рантайм-исключений.
    uid = None
    gid = None
    try:
        # Используем getattr с значением по умолчанию, чтобы Pyright понимал,
        # что атрибут может отсутствовать, и не ругался на обращение к нему.
        getuid = getattr(os, "getuid", None)
        getgid = getattr(os, "getgid", None)
        if callable(getuid):
            uid = getuid()
        if callable(getgid):
            gid = getgid()
        if uid is not None or gid is not None:
            p("UID/GID:", uid, gid)
        else:
            p("UID/GID: not available on this platform")
    except Exception:
        p("UID/GID: not available on this platform")

    # Probe: writing log file in CWD or logs dir
    try:
        target = Path("crewai_api_server_debug.log")
        target.touch(exist_ok=True)
        p("touch log in CWD: OK ->", str(target.resolve()))
    except Exception as e:
        p("touch log in CWD: FAIL:", repr(e))

    # Probe: create logs_dir in CWD
    try:
        d = Path("logs_dir")
        d.mkdir(parents=True, exist_ok=True)
        (d / "probe.txt").write_text("ok", encoding="utf-8")
        p("mkdir logs_dir + write: OK ->", str(d.resolve()))
    except Exception as e:
        p("mkdir logs_dir + write: FAIL:", repr(e))

    # Probe: HOME/.gopiai/state.json
    try:
        home = Path.home()
        p("Resolved HOME:", str(home))
        target_dir = home / ".gopiai"
        target_dir.mkdir(parents=True, exist_ok=True)
        state = target_dir / "state.json"
        state.write_text(json.dumps({"probe": True}, ensure_ascii=False, indent=2), encoding="utf-8")
        p("HOME state write: OK ->", str(state))
    except Exception as e:
        p("HOME state write: FAIL:", repr(e))

    # Show directory listings (best-effort)
    try:
        items = [f"{('[D]' if x.is_dir() else '[F]')} {x.name}" for x in Path(".").iterdir()]
        p("CWD listing:", items[:50])
    except Exception as e:
        p("CWD listing FAIL:", repr(e))

    try:
        home = Path.home()
        items = [f"{('[D]' if x.is_dir() else '[F]')} {x.name}" for x in (home / '.gopiai').iterdir()]
        p("HOME/.gopiai listing:", items[:50])
    except Exception as e:
        p("HOME/.gopiai listing FAIL:", repr(e))

if __name__ == "__main__":
    main()
