#!/usr/bin/env python3
"""Generate docs/SCHEDULES.md + docs/AUTOMATIONS.md from the YAML config.

Source of truth: the config mirror at ha_config/config (Git Exporter syncs it
from /config on the VM). Run:  python3 tools/summarize.py
Re-run + commit on every config change so docs never drift from reality.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO / "ha_config" / "config"


def load_yaml(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return None
    except yaml.YAMLError as e:
        print(f"  WARN: could not parse {path.name}: {e}", file=sys.stderr)
        return None


def load_helpers(config: Path) -> dict:
    """Collect all input_* helpers as {entity: {config, file}}."""
    helpers: dict[str, dict] = {}
    for domain in ("input_boolean", "input_datetime", "input_number", "input_select"):
        d = config / domain
        if not d.is_dir():
            continue
        for yf in sorted(d.glob("*.yaml")):
            data = load_yaml(yf)
            if not isinstance(data, dict):
                continue
            for name, cfg in data.items():
                if cfg is None:
                    cfg = {}
                helpers[f"{domain}.{name}"] = {"config": cfg, "file": yf.relative_to(config)}
    return helpers


def load_automations(config: Path) -> list[dict]:
    """Collect all automations from automations/ + automations.yaml."""
    automations: list[dict] = []
    adir = config / "automations"
    if adir.is_dir():
        for yf in sorted(adir.glob("*.yaml")):
            data = load_yaml(yf)
            if isinstance(data, list):
                for a in data:
                    if a:
                        a["_file"] = yf.relative_to(config)
                        automations.append(a)
    main = config / "automations.yaml"
    data = load_yaml(main)
    if isinstance(data, list):
        for a in data:
            if a:
                automations.append(a)
    return automations


def weekday_label(days: list[str]) -> str:
    if not days:
        return "all days"
    mapping = {
        "mon": "Mån", "tue": "Tis", "wed": "Ons", "thu": "Tor",
        "fri": "Fre", "sat": "Lör", "sun": "Sön",
    }
    order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    sel = [d for d in order if d in days]
    if not sel:
        sel = days
    if sorted(sel) == order:
        return "all days"
    if sel == order[:5]:
        return "vardagar (mån–fre)"
    if sel == order[5:]:
        return "helg (lör–sön)"
    joined = ", ".join(mapping.get(d, d) for d in sel)
    return joined or "all days"


def trigger_time(t: dict) -> str | None:
    at = t.get("at")
    if at is None:
        return None
    if isinstance(at, str):
        helper = [x for x in at.split() if x.startswith("input_datetime.")]
        if helper:
            return f"klockan ({helper[0]})"
        return at
    return None


def describe_automation(a: dict) -> str:
    alias = a.get("alias", a.get("id", "?"))
    trig = a.get("trigger") or []
    if not isinstance(trig, list):
        trig = [trig]
    bits: list[str] = []
    time_at = []
    weekdays = []
    for t in trig:
        p = t.get("platform")
        if p == "time":
            if ta := trigger_time(t):
                time_at.append(ta)
        elif p == "time_pattern":
            bits.append("tidsintervall")
        elif p == "homeassistant":
            bits.append("vid HA-start" if t.get("event") == "start" else "HA-händelse")
        elif p == "state":
            bits.append(f"när {t.get('entity_id')} → {t.get('to')}")
        elif p == "numeric_state":
            above = t.get("above")
            below = t.get("below")
            cond = []
            if above is not None:
                cond.append(f"> {above}")
            if below is not None:
                cond.append(f"< {below}")
            bits.append(f"när {t.get('entity_id')} {' & '.join(cond)}")
        elif p == "device":
            bits.append(f"fjärrkontroll {t.get('type')} ({t.get('subtype')})")
        elif p == "event":
            bits.append(f"event {t.get('event_type')}")
        elif p == "sun":
            bits.append(f"sol {t.get('event')}")
        else:
            bits.append(p)
    conds = a.get("condition") or []
    if not isinstance(conds, list):
        conds = [conds]
    for c in conds:
        cp = c.get("condition")
        if cp == "state":
            wd = c.get("weekday")
            if wd:
                weekdays = wd
            elif c.get("entity_id") == "sensor.home_status":
                bits.append(f"om hemstatus = {c.get('state')}")
        elif cp == "time":
            if wd := c.get("weekday"):
                weekdays = wd
        elif cp == "template":
            bits.append("villkor (template)")
    for wd in time_at:
        bits.append(wd)
    if weekdays:
        bits.append(weekday_label(weekdays))
    actions = a.get("action") or []
    if not isinstance(actions, list):
        actions = [actions]
    svc: list[str] = []
    for act in actions:
        s = act.get("service") or act.get("action")
        if isinstance(s, str):
            svc.append(s)
        elif isinstance(s, dict):
            svc.append(s.get("service"))
    body = " · ".join(bits) if bits else "—"
    desc = f"{alias}: {body}"
    if svc:
        desc += f"  →  {', '.join(s for s in svc if s)}"
    return desc


def render_schedules(helpers: dict, automations: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Scheman")
    lines.append("")
    lines.append("Automatiskt genererat av `tools/summarize.py` — **ändra aldrig "
                 "den här filen för hand.** Kör om + committa på varje "
                 "konfigurationsändring så att den aldrig driver från verkligheten.")
    lines.append("")
    lines.append("## Schema-hjälpvariabler (input_*)")
    lines.append("")
    lines.append("| Enhet | Beskrivning | Värde-id | Fil |")
    lines.append("|-------|-------------|----------|-----|")
    sched_keys = ["input_datetime.wake_time_weekday", "input_datetime.wake_time_weekend",
                  "input_datetime.bedtime_weekday", "input_datetime.bedtime_weekend",
                  "input_datetime.sovrum_on_time", "input_datetime.sovrum_off_time",
                  "input_datetime.isac_on_time", "input_number.sovrum_brightness",
                  "input_number.isac_brightness", "input_number.night_corner_brightness",
                  "input_number.outside_light_on_threshold",
                  "input_number.outside_light_off_threshold"]
    for key in sched_keys:
        h = helpers.get(key)
        if not h:
            continue
        cfg = h["config"]
        name = cfg.get("name", key)
        kind = "tid" if cfg.get("has_time") else "siffra"
        lines.append(f"| `{key}` | {name} ({kind}) | {cfg.get('initial', '—')} | `{h['file']}` |")
    lines.append("")
    lines.append("## Tidstyrda automations")
    lines.append("")
    lines.append("| Automation | När | Gör |")
    lines.append("|------------|-----|-----|")
    for a in sorted(automations, key=lambda x: (x.get("alias") or "").lower()):
        trig = a.get("trigger")
        if not isinstance(trig, list):
            trig = [trig]
        if not any(t.get("platform") == "time" for t in trig):
            continue
        alias = a.get("alias", a.get("id", "?"))
        when = []
        for t in trig:
            if t.get("platform") == "time":
                if ta := trigger_time(t):
                    when.append(ta)
        conds = a.get("condition")
        if isinstance(conds, list):
            for c in conds:
                if c.get("condition") == "time" and c.get("weekday"):
                    when.append(weekday_label(c["weekday"]))
        actions = a.get("action")
        if not isinstance(actions, list):
            actions = [actions]
        svc = []
        for act in actions:
            s = act.get("service") or act.get("action")
            if isinstance(s, dict):
                s = s.get("service")
            if isinstance(s, str):
                svc.append(s)
        lines.append(f"| {alias} | {' · '.join(when)} | {', '.join(svc)} |")
    lines.append("")
    return "\n".join(lines)


def render_automations(automations: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Automationer")
    lines.append("")
    lines.append("Automatiskt genererat av `tools/summarize.py` — **ändra aldrig "
                 "den här filen för hand.** Kör om + committa på varje "
                 "konfigurationsändring.")
    lines.append("")
    lines.append("| Automation | När | Utför | Källa |")
    lines.append("|------------|-----|-------|-------|")
    for a in sorted(automations, key=lambda x: (x.get("alias") or "").lower()):
        alias = a.get("alias", a.get("id", "?"))
        trig = a.get("trigger")
        if not isinstance(trig, list):
            trig = [trig]
        when = []
        for t in trig:
            p = t.get("platform")
            if p == "time":
                ta = trigger_time(t)
                when.append(ta or "klockslag")
            elif p == "time_pattern":
                when.append("tidsintervall")
            elif p == "homeassistant":
                when.append("HA-start" if t.get("event") == "start" else "HA-händelse")
            elif p == "state":
                when.append(f"{t.get('entity_id')} → {t.get('to')}")
            elif p == "numeric_state":
                above = t.get("above")
                below = t.get("below")
                cond = []
                if above is not None:
                    cond.append(f"över {above}")
                if below is not None:
                    cond.append(f"under {below}")
                when.append(f"{t.get('entity_id')} {' & '.join(cond)}")
            elif p == "device":
                when.append(f"fjärris (`{t.get('subtype')}`)")
            elif p == "sun":
                when.append(f"sol {t.get('event')}")
            else:
                when.append(p)
        conds = a.get("condition")
        if isinstance(conds, list):
            for c in conds:
                if c.get("condition") == "time" and c.get("weekday"):
                    when.append(weekday_label(c["weekday"]))
        actions = a.get("action")
        if not isinstance(actions, list):
            actions = [actions]
        svc = []
        for act in actions:
            s = act.get("service") or act.get("action")
            if isinstance(s, dict):
                s = s.get("service")
            if isinstance(s, str):
                svc.append(s)
        what = ", ".join(svc) or "—"
        src = a.get("_file", "—")
        lines.append(f"| {alias} | {' · '.join(when) or '—'} | {what} | `{src}` |")
    lines.append("")
    lines.append("## Läs mer")
    lines.append("")
    lines.append("- `docs/PLAN.md` — hela bygget · `docs/ADMIN.md` — drift/återställning")
    lines.append("- Familjen: ringa schemat i appen/chatten (agenten styr samma `input_*`).")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                    help="path to the config mirror (default: ha_config/config)")
    ap.add_argument("--out", type=Path, default=REPO / "docs",
                    help="output dir (default: docs/)")
    args = ap.parse_args()

    config: Path = args.config
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    helpers = load_helpers(config)
    automations = load_automations(config)
    print(f"helpers: {len(helpers)} · automations: {len(automations)}")

    (out / "SCHEDULES.md").write_text(render_schedules(helpers, automations), encoding="utf-8")
    (out / "AUTOMATIONS.md").write_text(render_automations(automations), encoding="utf-8")
    print(f"wrote {out / 'SCHEDULES.md'} · {out / 'AUTOMATIONS.md'}")

    # Consistency check: every scheduled time trigger references a live helper
    refs = set(helpers)
    bad = []
    for a in automations:
        trig = a.get("trigger")
        if not isinstance(trig, list):
            trig = [trig]
        for t in trig:
            if t.get("platform") == "time" and (at := t.get("at")):
                if isinstance(at, str):
                    for token in at.split():
                        if token.startswith("input_") and token not in refs:
                            bad.append(token)
    if bad:
        print("WARN: scheduled triggers reference unknown helpers:", sorted(set(bad)), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())