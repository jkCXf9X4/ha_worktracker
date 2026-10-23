# Deep dive — improve organization: rooms/areas, helpers, templates, scripts, automations

Status: **analysis, not deployed.** Reflects the live instance 2026-10-23 (area
registry + device registry pulled read-only over SSH) and `config/` mirror.
Every proposal is gated on owner decision; workspace candidates are logged in
`WORKTRACK/NEXT.md` (#030+). Best-practice baseline: `docs/BEST_PRACTICES.md`.

---

## 1. Room grouping — the foundation everything else builds on

### What the registry actually looks like today

Live registry pulled 2026-10-23 (read-only over SSH): **15 areas, 46 devices.
Only 8 of 46 devices are assigned to an area**; 15 physical devices are
**unmapped**. No labels exist; no freeze of entity-level area assignments
(everything is device-level).

### Owner corrections (2026-10-23) — incorporated into the plan

- **`Uteljussensor` is house-wide**, not a room — do **not** tuck it under
  `Ute framsida`/`Uterum`. It applies to the whole house's outdoor light.
  (Verdict → leave unassigned, or a small house-level "Utomhus" area; owner's call.)
- **`Utebelysning` = the outdoor lighting area, front AND back.** Keep it;
  merge `Ute framsida` into it (`Ute huvudentré` → `Utebelysning`).
- **Real corridors:** an **entrance hall**, a **bathroom corridor** and the
  **kitchen corridor**.
- **`Carport korridor` is misnamed → rename to kitchen corridor/hallway** (not
  delete).
- **`Kvällsbelysning` is NOT an area** — those are window/holiday lights that
  belong to their actual rooms. Dissolve it: `Slinga uterum (P10)` → `Uterum`;
  `Julslinga (P11)` → outdoor, so → **`Utebelysning`** (owner).
- **`Kitchen` is a real room** but has no smart lights — **keep** (as `Kök`).
  (owner)
- **`Korridor` = the bathroom corridor** → rename **`Badrum korridor`** (owner).
- **`Carport ingång (l3_2)` and `Groventre (l3_1)`** — "night-corner" corridor
  lights (see skill: night-corner `light.l3_1`/`l3_2`). Proposal:
  `l3_2` → `Kök korridor` (carport entry = kitchen corridor), `l3_1` →
  `Entré hall` (groventré). **Owner confirm** in the device-map round.

### Owner corrections (2026-10-23) — final decisions on the area questions

| Question | Answer |
|----------|--------|
| `Kitchen` room | **Real room**, keep (as `Kök`) — no smart lights, stays empty |
| `Korridor` = bathroom corridor? | **Yes** → rename `Badrum korridor` |
| `P11 Julslinga` (was Kvällsbelysning) | **Outdoor** → `Utebelysning` |

### Area review — consolidation targets (concrete)

Origin: most non-Swedish areas are **Hue bridge `Room` groupings** carried over
from the bridge era (the `hue_zha_migration.md` lists the same names; the bridge
is dead, these are scaffolding, not rooms).

| Area now | Devices | Verdict / consolidation |
|----------|---------|--------------------------|
| `CarPort` | 0 | **EMPTY legacy** — delete (carport lighting lives under `Utebelysning`) |
| `Carport korridor` | 0 | **RENAME → Kök korridor** (kitchen corridor/hallway, owner) — keep |
| `Gästrum` | 0 | Real room, keep — seed with `Gästrum tak` + `Gästrum fönster` |
| `Hall` | 0 | Real room, keep → rename `Entré hall` — seed with `Entré hall tak` |
| `Isacs rum` | 0 | Real room, keep — seed with `Isacs rum tak` + `Isacs sänglampa` + `Hue-dimmer Isacs` |
| `Kitchen` | 0 | **Real room, keep** as `Kök` (owner) — no smart lights, stays empty |
| `Korridor` | 0 | **Rename → `Badrum korridor`** (owner: it is the bathroom corridor) — seed `Korridor tak` + `Korridor 2` |
| `Kvällsbelysning` | 2 (`P10`,`P11`) | **Dissolve** — P10→`Uterum`, P11→`Utebelysning` (outdoor, owner) |
| `Other` | 0 | **EMPTY junk** — delete |
| `OutsideRoom` | 1 (Uteljussensor) | Keep → rename `Uterum`; move Uteljussensor out (house-wide) |
| `Sovrum` | 1 (Sovrum dimmer) | Keep — good |
| `Träningsrum` | 0 | **EMPTY legacy** — delete (no devices) |
| `Ute framsida` | 1 (Ute huvudentré) | **MERGE → `Utebelysning`** (outdoor lighting = front + back) |
| `Utebelysning` | 0 | **KEEP** — the outdoor lighting area (owner); seed `Ute huvudentré` |
| `Vardagsrum` | 3 (P1, dimmer, bokhylla) | Keep — good |

**Summary of consolidation actions:**
1. `CarPort` + `Other` + `Träningsrum` → **delete** (empty legacy). `Kitchen` →
   **keep** as `Kök` (no smart lights, real room).
2. `Ute framsida` → **merge into** `Utebelysning`.
3. `OutsideRoom` → rename `Uterum`; `Kvällsbelysning` → **dissolve** (P10→Uterum,
   P11→Utebelysning); `Carport korridor` → rename **Kök korridor**.
4. `Hall` → `Entré hall`; `Korridor` → `Badrum korridor`.
5. `Uteljussensor` stays house-level (no room area).

Verdict: the **area registry is the single biggest unrealized lever** here.
Areas give: area-targetable automations, dashboard area cards that never go
stale, room filtering, and a foundation for labels/floors.

### What the best practice is

| Tool | Is for | Used correctly here? |
|------|--------|-----------------------|
| **Area** | physical room; device → one area; automation target | ⚠️ exists, half-English, ~⅓ of devices mapped |
| **Floor** | group areas (e.g. våning 1 / våning 2) | ❌ unused |
| **Label** | cross-cutting concerns, many per entity, target in automations | ❌ unused |
| **Group integration** | merge entities into ONE controllable entity | ✅ ceiling_lamps / night_lamps (control groups — correct use) |

`groups.yaml`'s `ceiling_lamps`/`night_lamps` are **control** groups (we want to
turn the whole set on/off as one entity) — those stay. **Room placement has no
business in a group; it belongs in the area registry.**

### Proposal (#030): normalize areas + map every device

1. **Rename to consistent Swedish** (match dashboard + families):
   `Hall` → **Entré & hall**, `Kitchen` → **Kök**, `CarPort` → **Carport**,
   `OutsideRoom` → **Uterum**, `Träningsrum` → **Hobbyrum** (or keep —
   see device map note), `Other` → delete (empty), `Carport korridor` → delete
   (empty; carport-corridor light is `korridor_tak`'s area question — ask owner).
2. **Assign every physical device to an area** (read-only mapping table below —
   same device names as the registry dump).
3. **Optional: floors** `Våning 1` / `Våning 2` (owner confirms the split).
4. After mapping, **dashboard Belysning view** can drop its hard-coded room
   cards in favour of **area cards** (one per room) → membership auto-updates.

### Proposed device → area map (verify names against dashboard / floor plan)

| Device (registry name) | Area |
|------------------------|------|
| Entré hall tak | Entré & hall |
| Korridor tak | Korridor |
| Korridor 2 (E14 opal) | Korridor |
| Gästrum tak | Gästrum |
| Gästrum fönster (läslampa P7) | Gästrum |
| Vardagsrum dimmer | Vardagsrum |
| Bokhylla höger | Vardagsrum |
| Hörnlampa/Tvättstuga (P1) | Vardagsrum (device name says "Tvättstuga" — **owner confirm** which room) |
| Sovrum dimmer | Sovrum |
| Isacs rum tak | Isacs rum |
| Isacs sänglampa (p6) | Isacs rum |
| Hue-dimmer Isacs (RWL021) | Isacs rum |
| Groventre (l3_1) | **Kök korridor** (fished, by the bedroom) |
| Carport ingång (l3_2) | **Kök korridor** (fished, by the carport entrance) |
| Bilvärmare (P4) | Utebelysning (outdoor, carport plug) |
| Uttag P2 | Kök (proposed — owner maybe) |
| Isacs lekstuga (TRETAKT plug) | **Vardagsrum** (fished, Isacs playhouse — owner: lekstuga is part of living room) |
| STYRBAR Isacs lekstuga (remote) | **Vardagsrum** (with the playhouse) |
| Hobbyrum fönster (innr) | **Hobbyrum** (fished, window lamp) |
| Slinga uterum (P10) | **Uterum** (fished, outdoor pergola light) |
| Julslinga (P11) | Utebelysning (outdoor, owner) |
| Ute huvudentré | **Utebelysning** (fished, outdoor main entrance) |
| Korridor tak | **Badrum korridor** (fished, by the kitchen) |
| Korridor 2 | **Badrum korridor** (fished, by the carport entrance) |
| Gästrum tak | **Gästrum** (fished, ceiling) |
| Vardagsrum dimmer | **Vardagsrum** (fished, ceiling) |
| Sovrum dimmer | **Sovrum** (fished, ceiling) |
| Bokhylla höger | **Vardagsrum** (fished, bookshelf) |
| Entré hall tak | **Entré hall** (fished) |
| Uteljussensor | house-wide (no room area) |
| (phones/persons) | — |

### Proposal (#031): labels for cross-cutting concerns

Once areas exist, add **labels** for the things that cut across rooms:

- `säsong` on the Christmas sockets (`p10`, `p11`, `p1`, `p6`) → an automation
  can target the label instead of the `christmas_sockets` group; dissolves the
  #020/#028 group-editing churn.
- `utebelysning` on outside lights → dashboard/automation "all outside" target.
- `godnatt_ignorera`/manual-override labels if we later want pause logic.

Rule from best practices: **one entity can have many labels but exactly one
area.** Security/seasonal/usage groups become labels; control groups stay
groups.

---

## 2. Helpers — already strong; two real gaps

### What's right
`input_datetime` (wake/bedtime ×4, sovrum ×2, isac ×1), `input_number`
(lux ×2, brightness ×3), `input_boolean` (`light_outside`, `ha_started`,
`christmas_lights`) — all scoped, Swedish-named, `initial:`-free so edits
survive boot (P10 fix). This is the textbook "helpers = knobs, automations read
the knobs" model.

### Proposal (#032): pause toggles for common automation sets
Best practice (which-tool-to-use): a **toggle helper = "pause this automation"**
so the family can disable a behavior from the dashboard without editing YAML.
Today there is no way to stop e.g. night lamps or the ceiling automation except
editing config. Add, wired as conditions:

- `input_boolean.automatik_taklampor` (gate ceiling_lights automations)
- `input_boolean.automatik_nattlampor` (gate night_lights automations)
- `input_boolean.automatik_uteljus` (gate outside_light + night-lamp daylight part)

Each automation gains one `condition: state` check on its toggle. Family flips
them on the Schema/Översikt dashboard. Minimal blast, real usability win.

No other new helpers are warranted (avoid helper sprawl).

---

## 3. Templates — one good machine, one optional win

### What's right
`sensor.home_status` (`template/home_status.yaml`) is a clean state machine with
an explicit `availability` guard; time values flow from `input_datetime` helpers.
No template sprawl.

### Proposal
- **#024 already logged:** simplify the `as_timestamp` math to a
  lexicographic `HH:MM:SS` compare (~70% shorter, same output). Defer to owner.
- **Optional (#033):** a derived `next_event` template sensor for the dashboard —
  `sensor.next_bedtime` / `sensor.next_wake` (next wake/sleep boundary computed
  from the same helpers) so the family sees "nästa läggdags: 21:00". Reuses the
  `home_status` math once; not worth it until #024 lands.
- Keep everything else as-is; templates should stay as derived *ground truth*,
  not logic duplication.

---

## 4. Scripts — already models; one convenience add

### What's right
- `light_on_with_transition` — the reusable field-driven script (entity +
  brightness + transition), consumed by sovrum + isac automations. Exactly the
  "shared steps in a script" best practice.
- `nattmode` — dynamic night-corner brightness (correct replacement for the
  non-templatable scene; P10 fix).
- `korridor_blink` — named action that surfaces to the chat agent as a native
  `script.*` tool. This is the HA-blessed "named action" pattern.

### Proposal (#034): one convenience script — `goodnight`
A single voice/dashboard action "god natt" that does what sleep currently does
in pieces: ceiling off (`group.ceiling_lamps`) → night-corner on at helper
brightness (`script.nattmode`) → lock doors (`lock.lock` both). One script the
family can trigger from Assist/Voice/dashboard without waiting for the
home_status edge. Low effort, high family value. Owner sign-off only if
behaviour is wanted as a manual action in addition to the automatic sleep.

Everything else in scripts stays.

---

## 5. Automations — good set; three consolidations

### What's right
17 automations across 9 files + 2 blueprints (`zha_remote_lights.yaml`,
`zha_remote_switch.yaml` for the remotes). Edge-trigger + full-condition
reconciliation after boot; `ha_started` grace gate; helper-driven times. Modern
`trigger:`/`action:` and `trigger: device` in blueprints. All verified live.

### Proposal
- **#025 (already logged):** startup-grace gate repeated in 11 automations →
  optional blueprint.
- **#026 (already logged):** the 4 ceiling automations are one shape → the
  Taras data-driven consolidation.
- **#035 (new):** after #030 (areas), two automations can shrink by targeting
  **areas/labels** instead of hard-coded entity lists:
  - `night_lights.yaml` Christmas branch → target label `säsong` (kills the
    `christmas_sockets` group + its keep-in-sync maintenance; also resolves the
    #020 seasonal grouping question).
  - Dashboard/`scenes.yaml` membership stays in sync automatically via area
    ownership instead of the "keep in sync with groups.yaml" comment.
- No other automation changes warranted; interplay toggles from #032 are the
  main new wiring.

---

## 6. Summary of new candidates (all ⬜ owner-decision first)

| # | What | Effort | Risk | Depends on |
|---|------|--------|------|------------|
| #030 | Normalize area registry (rename/delete legacy) + map all 46 devices; dashboard area cards | M | low (registry only; revertible) | owner OK on room/English→Swedish mapping |
| #031 | Add `säsong`/`utebelysning` labels; target them from automations | S | low | #030 |
| #032 | Pause-toggle helpers for ceiling/night/outside automations | M | low | — |
| #033 | `next_wake`/`next_bedtime` template sensor (after #024) | S | low | #024 |
| #034 | `script.goodnight` convenience action | S | low | — |
| #035 | Christmas sockets via label; scenes/groups de-duplication | S | low | #030/#031 |

Already-logged related items: #024 (home_status math), #025 (startup-grace
blueprint), #026 (ceiling consolidation), #028 (labels for seasonal sockets —
superseded/sharpen by #031).

---

## Owner decisions needed before any edit

**Resolved + APPLIED 2026-10-23** (area registry live on the VM, exporter
`643e941`, `ha core check` green):

- Kitchen real room → kept as `Kök` (no smart lights).
- `Korridor` = bathroom corridor → **Badrum korridor**.
- `P11` Julslinga + `P4` Bilvärmare → **Utebelysning** (outdoor, front+back).
- `Uteljussensor` house-wide (no room area).
- `Carport korridor` → **Kök korridor**; `Kvällsbelysning` dissolved
  (P10→Uterum, P11→Utebelysning); `Ute framsida` merged → Utebelysning.
- Deleted legacy: `CarPort`, `Other`, `Träningsrum`.
- **Fished + mapped (confirmed by blinking):** l3_1/l3_2 → Kök korridor;
  korridor_tak/Korridor 2 → Badrum korridor; entre_hall_tak → Entré hall;
  gastrum_tak + laslampa → Gästrum; dimmer_fixed_livingroom_light +
  bokhylla + isac_lekstuga + STYRBAR → Vardagsrum; dimmer_fixed_bedroom_light_2
  → Sovrum; ute_huvudentre → Utebelysning; hobby_rum_fonster → Hobbyrum (new);
  p10 → Uterum; p2 → Kök. Full log: `docs/fishing_log.md`.

Remaining (small):
1. Enable pause toggles (#032), `goodnight` script (#034)?
2. Christmas sockets: switch from group to label (#035) — resolves #020?
3. Dashboard Belysning view: switch room cards to **area cards** (membership now
   lives in the registry).