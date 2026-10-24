# Deep dive — the `home_status` state machine (awake / sleep / away)

> **Status: COMPLETED/APPLIED 2026-10-24 — archived reference.** Option B
> (lexicographic `HH:MM:SS` compare) was implemented as #024 in
> `template/home_status.yaml`; the `next_wake`/`next_bedtime` attributes land as
> #033 in the same file. Nothing here is pending — kept for the decision record.
> Live state: `WORKTRACK/NEXT.md`.

Historical analysis (original header): **analysis + candidate patch, not yet deployed**
(written 2026-10-23; review alongside `docs/BEST_PRACTICES.md` §1).

## The machine today

`config/` `template/home_status.yaml` renders a `sensor.home_status` every
minute (`time_pattern`): `away` if `group.family` not home, else `awake` when
`wake ≤ now < bed`, else `sleep`. About 20 automations in 5 files depend on it
(value conditions + edge triggers).

### What it really computes

- **away** — presence only (person.* via group.family).
- **wake** = `input_datetime.wake_time_weekday|weekend` (Mon–Fri / Sat–Sun).
- **bed** = `input_datetime.bedtime_weekday|weekend` (Sun–Thu / Fri–Sat).

Two *independent* weekday axes. That's the source of the template's length: it
picks two helpers by two different weekday rules, converts to timestamps, then
compares `wake ≤ now < bed`.

### What is sound about it

- The **helpers are the values** — the family edits times in the dashboard /
  via chat, the automations just read. Direct hit on the build goal.
- The `availability` guard is correct and protective.
- Edge-triggered automations (sovrum/ceiling/locks) + `homeassistant: start`
  triggers with full conditions give correct boot reconciliation.

## Option A — replace with a native `schedule` helper (the "modern way"… not here)

HA's `schedule` helper + `Schedule block started` trigger / `schedule.is_on`
condition was the plan doc's stated target. Reasoning it through:

**Pros** — no weekday math, no `time_pattern` polling, no `as_timestamp`,
cleaner `schedule.is_on` conditions.

**Blockers for THIS build** (why it's the wrong tool *here*):

1. **No runtime service to edit block times.** Schedule blocks are defined in
   the UI or in YAML (`schedule:` domain); the only actions are
   `schedule.get_schedule` (read) and `schedule.reload` (re-read YAML). There is
   **no `schedule.set`** — a chat agent or dashboard picker cannot change a
   block's times via a service call the way they edit `input_datetime`. The
   whole build premise is that *family + chat agent edit times via helpers*.
   A schedule helper would freeze the times to UI/YAML editing, off the
   versioned `input_*` path.
2. **Sleep is the complement of awake across midnight.** A time block cannot
   cross midnight (docs: "no overlapping blocks", "cannot cross midnight" —
   keep it on across midnight requires *two touching blocks* on consecutive
   days). You'd express `sleep` as "everything not in the awake block", which
   works for *conditions* but is awkward for *triggers* and adds two blocks per
   day anyway.
3. **Two weekday axes don't map 1:1.** Awake-window Mon is `weekday wake → weekday bed`,
   Sat is `weekend wake → weekend bed`, Sun is `weekend wake → weekday bed`. You'd
   hand-encode five day-specific blocks that *duplicate* the helper values, then
   keep the helpers in sync by hand — a new drift source.

**Verdict:** the `schedule` helper is the right tool for *fixed* recurring
windows (heating, fixed work hours). For *family-editable* wake/bed times it is
a regression. **Keep the input_datetime-helper design.** This overrides the
optimistic "worth prioritizing" line in BEST_PRACTICES.md §2.4.

## Option B (recommended) — same design, less math

The template's timestamp juggling is unnecessary: both helpers are
zero-padded `HH:MM:SS`, bed is always later than wake within the same day, and
the awake window never spans midnight. So a lexicographic string compare on
`HH:MM:SS` is equivalent and ~70% shorter:

```yaml
- triggers:
    - trigger: time_pattern
      minutes: "/1"
  sensor:
    - name: Home status
      unique_id: home_status
      icon: mdi:home-outline
      state: >
        {% if not is_state('group.family', 'home') %}
          away
        {%- else -%}
          {%- set wd = now().weekday() -%}
          {%- set w = states('input_datetime.wake_time_weekday' if wd <= 4
                             else 'input_datetime.wake_time_weekend') -%}
          {%- set b = states('input_datetime.bedtime_weekday' if wd in [0,1,2,3,6]
                             else 'input_datetime.bedtime_weekend') -%}
          {%- set t = now().strftime('%H:%M:%S') -%}
          {{ 'awake' if w <= t < b else 'sleep' }}
        {% endif %}
      availability: >
        {{ states('group.family') not in ['unavailable', 'unknown']
           and states('input_datetime.wake_time_weekday') not in ['unavailable', 'unknown']
           and states('input_datetime.wake_time_weekend') not in ['unavailable', 'unknown']
           and states('input_datetime.bedtime_weekday') not in ['unavailable', 'unknown']
           and states('input_datetime.bedtime_weekend') not in ['unavailable', 'unknown'] }}
```

Equivalent output for every combination of the current helper values. The
`input_datetime` entities `input_datetime.wake_time_weekday` etc. (the *helper
entities*, not the YAML keys `wake_time_weekday:`) are zero-padded, so `<`
compares correctly.

**Caveat 1 — pick the right selectors.** Keep the `time_pattern: /1` + template
so the transition fires at wake/bed editing even if no other entity changes
(this is a *template sensor*, so the render cadence is the heartbeat; the
automations are edge-triggered on `sensor.home_status`).
**Caveat 2 — test around midnight.** With healthy values (wake 06:xx / bed
21:xx/21:30) the compare is safe; if someone ever edits `wake > bed`, the
window silently flips to "sleep 00:00–…" — worth an owner note, identical to
the current behavior (no regression).
**Verification:** `ha core check`, then force transitions via
`conversation/process` or by temporarily editing a helper; watch a trace on one
dependent automation (e.g. ceiling_lights) to confirm the edge trigger still
fires.

## Option C — per-room: schedulen (no)

Mixing a native `schedule` for sovrum (fixed Mon–Fri window) is a *smaller*
win (sovrum already uses `input_datetime.sovrum_on_time` + a `weekday`
condition, which is fine) and would split the edit surface. Skip.

## Anything else the audit found near the machine?

- `group.family` → correct presence primitive (person.*).
- Locks + ceiling + night lights all read the same `home_status`/`ha_started`
  pair, so a future consolidation (BEST_PRACTICES.md §2.1/§2.2) reduces these
  duplications too — but only as readability work, not behavior.

## Decision needed from owner

1. Adopt Option B (string-compare refactor) as part of a future tidy-up? — yes / no.
2. Verify the wake/bed Saturday/Sunday edge mappings actually match
   family intent (weekend = Sat wake..Sun bed is the current math: Sat falls in
   the weekend bed axis because `wd == 5`, Sundays get weekday bed). Confirm
   "Sunday bedtime is weekday-bed" is intended.