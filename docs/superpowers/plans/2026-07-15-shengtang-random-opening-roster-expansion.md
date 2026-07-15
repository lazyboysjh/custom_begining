# Sanctum Random Opening and 150-Role Roster Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace manual heroine/meeting selection with a cross-era randomized opening reveal, persist its public configuration in MVU, adapt cover and status UI, and expand the researched role roster from 78 to 150.

**Architecture:** Store opening dimensions in one YAML source and inject them into the standalone cover through the existing build synchronizer. The cover samples and locks one opening configuration per generation transaction, sends a causal prompt, and commits public MVU fields only after generation succeeds. Character data remains the single source for cover, status roster and generated world-book profiles; source research is tracked separately from runtime prompts.

**Tech Stack:** Python 3, PyYAML, unittest, standalone HTML/CSS/JavaScript, Zod 4 MVU schema, SillyTavern helper APIs, Git-pinned jsDelivr static delivery.

## Global Constraints

- Always preserve the Sanctum's purification system, cross-world node, ritual rules and hub identity while allowing its outward form to change.
- `user` ability is the only player-controlled opening field; heroine, era, story type, atmosphere, Sanctum form and integration mode are random.
- All 30 story types are available to every heroine without canon-era filtering.
- The cover must not reveal or allow selecting the heroine before generation begins.
- This phase does not add, validate, rewrite or filter age rules.
- Canon and official sources override encyclopedias; high-consensus fan interpretation only fills gaps and never overrides canon.
- Public-figure profiles use verifiable public work and public expression only, without invented private facts.
- MVU must create `角色.${name}` before appending the name to `世界.出场角色`, and multi-role updates remain independent.
- UI must remain free of internal MVU/API/CDN/build copy and pass 360px, 768px and 1280px browser review.

---

## File Structure

- Create `plot/opening_options.yaml`: 30 story types, 10 atmospheres, era seeds, Sanctum forms, integration modes and ability presets.
- Create `plot/character_sources.yaml`: research provenance for every newly added role, excluded from runtime injection.
- Modify `plot/characters.yaml`: add 72 complete profiles to reach 150.
- Modify `build_shengtang_card.py`: validate/sync opening options, validate source coverage and keep cover/status/world-book generation aligned.
- Modify `plot/schema.mvu.js`, `plot/initvar.yaml`, `plot/mvu_update.yaml`: persist public opening configuration.
- Modify `src/shengtang/ui/cover/index.html`: ability-only setup, random configuration engine, reveal animation and transactional generation.
- Modify `src/shengtang/ui/status/index.html`: show story type, atmosphere, Sanctum form and ability summary without exposing hidden configuration.
- Modify `scripts/test_shengtang_regressions.py`, `scripts/superpower_shengtang_review.py`: enforce data, MVU, UI and release requirements.
- Generate `worldbook/角色/*.md`, `dist/shengtang/ui/*` and `圣堂初遇.json` through the existing build.

---

### Task 1: Opening option source and build synchronization

**Files:**
- Create: `plot/opening_options.yaml`
- Modify: `build_shengtang_card.py`
- Modify: `src/shengtang/ui/cover/index.html`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Produces: `load_opening_options() -> dict[str, list[dict]]`
- Produces in cover: `const OPENING_OPTIONS = { story_types, atmospheres, eras, sanctum_forms, integration_modes, ability_presets }`

- [ ] **Step 1: Write failing option-source tests**

Add tests asserting exactly 30 unique story type IDs/titles, non-empty prompt hooks, exactly 10 atmospheres and non-empty era/form/integration/ability collections. Assert every collection is injected once between `SYNC_BEGIN:OPENING_OPTIONS` markers.

- [ ] **Step 2: Run the focused tests and confirm failure**

Run: `python -m unittest scripts.test_shengtang_regressions.OpeningOptionTests -v`

Expected: failures for missing `plot/opening_options.yaml` and synchronization marker.

- [ ] **Step 3: Add the complete option data and loader**

Implement:

```python
def load_opening_options() -> dict:
    data = yaml.safe_load((ROOT / "plot/opening_options.yaml").read_text(encoding="utf-8")) or {}
    required = ("story_types", "atmospheres", "eras", "sanctum_forms", "integration_modes", "ability_presets")
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise SystemExit(f"opening options missing: {', '.join(missing)}")
    return {key: list(data[key]) for key in required}
```

Replace `MEETING_MODES` synchronization with one JSON `OPENING_OPTIONS` block while keeping character synchronization independent.

- [ ] **Step 4: Run focused tests and build sync**

Run: `python -m unittest scripts.test_shengtang_regressions.OpeningOptionTests -v`

Run: `python build_shengtang_card.py`

Expected: option tests pass and build reports 30 story types.

- [ ] **Step 5: Commit the opening option source**

```powershell
git add plot/opening_options.yaml build_shengtang_card.py src/shengtang/ui/cover/index.html scripts/test_shengtang_regressions.py
git commit -m "Add cross-era Sanctum opening options"
```

### Task 2: MVU public opening state

**Files:**
- Modify: `plot/schema.mvu.js`
- Modify: `plot/initvar.yaml`
- Modify: `plot/mvu_update.yaml`
- Modify: `worldbook/00_世界观.md`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Produces: `世界.时代背景`, `世界.故事类型`, `世界.故事氛围`, `世界.圣堂形态`, `世界.开局摘要`
- Preserves: `世界.出场角色: string[]` and `角色: Record<string, RoleState>`

- [ ] **Step 1: Write failing schema and initialization tests**

Assert the five fields exist in schema and initvar, use string prefaults, and are listed as opening-readonly fields in update rules.

- [ ] **Step 2: Run focused MVU tests and confirm failure**

Run: `python -m unittest scripts.test_shengtang_regressions.MultiRoleStateTests -v`

Expected: failures naming the missing world fields.

- [ ] **Step 3: Add idempotent Zod fields and update rules**

Add to `世界`:

```javascript
时代背景: z.string().prefault('待生成'),
故事类型: z.string().prefault('待生成'),
故事氛围: z.string().prefault('待生成'),
圣堂形态: z.string().prefault('圣言堂'),
开局摘要: z.string().prefault('待生成'),
```

Initialize the same keys and mark them opening-readonly after the first transaction. Document that later plot changes update `场景` and `回合`, not the opening identity.

- [ ] **Step 4: Run focused and full regressions**

Run: `python scripts/test_shengtang_regressions.py`

Expected: all tests pass.

- [ ] **Step 5: Commit MVU state expansion**

```powershell
git add plot/schema.mvu.js plot/initvar.yaml plot/mvu_update.yaml worldbook/00_世界观.md scripts/test_shengtang_regressions.py
git commit -m "Persist randomized Sanctum opening state"
```

### Task 3: Random configuration engine and causal prompt

**Files:**
- Modify: `src/shengtang/ui/cover/index.html`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Produces: `sampleOpeningConfig({ randomAbility: boolean }): OpeningConfig`
- Produces: `lockOpeningConfig(config): void`
- Consumes: `OPENING_OPTIONS`, `CHARACTERS`
- `OpeningConfig` keys: `character`, `era`, `storyType`, `atmosphere`, `sanctumForm`, `integrationMode`, `ability`

- [ ] **Step 1: Write failing lifecycle tests**

Assert no character card grid or meeting mode grid is rendered, `startGame()` samples a configuration before generation, both normal and one-click buttons exist, all six random dimensions enter `buildPrompt`, and the final patches create the role before replacing `出场角色`.

- [ ] **Step 2: Run focused lifecycle tests and confirm failure**

Run: `python -m unittest scripts.test_shengtang_regressions.OpeningLifecycleTests -v`

Expected: failures for old manual `modeId`/`charId` flow and missing sampler.

- [ ] **Step 3: Implement unbiased sampling and configuration locking**

Use `crypto.getRandomValues` when available with a `Math.random` fallback:

```javascript
function randomIndex(length) {
  if (!Number.isInteger(length) || length < 1) throw new Error('当前没有可用的随机选项。');
  if (globalThis.crypto?.getRandomValues) {
    const max = Math.floor(0x100000000 / length) * length;
    const value = new Uint32Array(1);
    do crypto.getRandomValues(value); while (value[0] >= max);
    return value[0] % length;
  }
  return Math.floor(Math.random() * length);
}

const pickOne = list => list[randomIndex(list.length)];
```

Normal start uses the selected/manual ability; one-click start samples an ability preset. All other dimensions always sample from full collections and remain locked in `activeOpening.config` until completion/cancel/failure.

- [ ] **Step 4: Rewrite prompt and patches around `OpeningConfig`**

The prompt must explicitly require the five-part causal explanation, core-personality preservation and functional ability adaptation. Patches write public world fields, protagonist ability, role record and then `世界.出场角色` in that order.

- [ ] **Step 5: Run focused and full regressions**

Run: `python scripts/test_shengtang_regressions.py`

Expected: all tests pass and no old manual heroine selector remains.

- [ ] **Step 6: Commit the opening engine**

```powershell
git add src/shengtang/ui/cover/index.html scripts/test_shengtang_regressions.py
git commit -m "Randomize cross-era Sanctum openings"
```

### Task 4: Cover reveal experience and responsive states

**Files:**
- Modify: `src/shengtang/ui/cover/index.html`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Produces: `startReveal(config): Promise<void>`
- Produces: `finishReveal(config): void`
- Consumes: locked `OpeningConfig`

- [ ] **Step 1: Write failing product UI tests**

Assert reveal markup includes an accessible live region, role name/work/blurb slots, progress copy, cancel action and reduced-motion styling. Assert animation completion and generation completion are represented by separate state flags.

- [ ] **Step 2: Run ProductUiTests and confirm failure**

Run: `python -m unittest scripts.test_shengtang_regressions.ProductUiTests -v`

- [ ] **Step 3: Replace manual selection pages with ability setup and reveal page**

Keep C2 material tokens. Provide ability mode segmented controls, preset select, manual textarea, “生成开局” and “一键随机开始”. The reveal uses a bounded name reel, then fixes the selected name/work/blurb while textual generation progress remains active.

- [ ] **Step 4: Add reduced-motion and container behavior**

At 360px show one candidate line and stacked actions; at 768px and above show a wider reveal stage. Under `prefers-reduced-motion: reduce`, skip reel translation and fade directly to the result.

- [ ] **Step 5: Run regressions and local browser audit**

Run: `python scripts/test_shengtang_regressions.py`

Expected: all tests pass; browser audit finds no overflow, clipped buttons, hidden controls or console errors.

- [ ] **Step 6: Commit the reveal UI**

```powershell
git add src/shengtang/ui/cover/index.html scripts/test_shengtang_regressions.py
git commit -m "Add Sanctum heroine reveal experience"
```

### Task 5: Status bar integration

**Files:**
- Modify: `src/shengtang/ui/status/index.html`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Consumes: five new `世界` fields and `主角.能力摘要`
- Preserves: role selection from `世界.出场角色`

- [ ] **Step 1: Write failing status tests**

Assert status renders story type, atmosphere and Sanctum form, provides a compact ability summary, never renders integration mode, and still selects only names present in `世界.出场角色`.

- [ ] **Step 2: Run status tests and confirm failure**

Run: `python -m unittest scripts.test_shengtang_regressions.StatusLifecycleTests -v`

- [ ] **Step 3: Implement compact public opening summary**

Extend the scene header with three semantic spans and add a collapsible/compact ability line within the existing shell. Do not add a separate nested card or expose prompt terminology.

- [ ] **Step 4: Verify multi-role and responsive behavior**

Run full regressions and browser demo with one, three and six present roles at 360px, 768px and 1280px.

- [ ] **Step 5: Commit status integration**

```powershell
git add src/shengtang/ui/status/index.html scripts/test_shengtang_regressions.py
git commit -m "Show randomized opening context in Sanctum status"
```

### Task 6: Character source registry and roster validation

**Files:**
- Create: `plot/character_sources.yaml`
- Modify: `build_shengtang_card.py`
- Modify: `scripts/test_shengtang_regressions.py`
- Modify: `scripts/superpower_shengtang_review.py`

**Interfaces:**
- Produces: `load_character_sources() -> dict[str, dict]`
- Source keys match new `plot/characters.yaml` IDs exactly.

- [ ] **Step 1: Write failing source and profile-quality tests**

Assert every newly added ID has source records, each profile has all existing fields, at least three background/relation items, unique aliases, a non-template filth seed and a distinct agency anchor.

- [ ] **Step 2: Run character tests and confirm failure**

Run: `python -m unittest scripts.test_shengtang_regressions.CharacterSourceTests -v`

- [ ] **Step 3: Add source registry schema and reviewer checks**

Each source record contains `name`, `category`, `primary_sources`, `secondary_sources`, and `notes`. Runtime build validates coverage but excludes this file from cover/status/world-book injection.

- [ ] **Step 4: Run focused tests**

Expected: source-schema tests pass with the current roster baseline and fail whenever an added role lacks provenance.

- [ ] **Step 5: Commit validation infrastructure**

```powershell
git add plot/character_sources.yaml build_shengtang_card.py scripts/test_shengtang_regressions.py scripts/superpower_shengtang_review.py
git commit -m "Add researched roster quality gates"
```

### Task 7: Expand anime and game profiles

**Files:**
- Modify: `plot/characters.yaml`
- Modify: `plot/character_sources.yaml`
- Generate: `worldbook/角色/*.md`

- [ ] **Step 1: Research and add the approved anime/game batch**

For every profile, record canon/official references first, then complete all required runtime fields. Preserve speech, motivation, refusal boundary and recognizable capability rather than generic appeal.

- [ ] **Step 2: Generate world-book profiles and run character tests**

Run: `python build_shengtang_card.py`

Run: `python -m unittest scripts.test_shengtang_regressions.CharacterSourceTests scripts.test_shengtang_regressions.AntiSycophancyTests -v`

- [ ] **Step 3: Review duplicates and commit the batch**

```powershell
git add plot/characters.yaml plot/character_sources.yaml worldbook/角色
git commit -m "Expand Sanctum anime and game roster"
```

### Task 8: Expand Chinese web-novel profiles

**Files:**
- Modify: `plot/characters.yaml`
- Modify: `plot/character_sources.yaml`
- Generate: `worldbook/角色/*.md`

- [ ] **Step 1: Research original novel text and add the web-novel batch**

Use novel canon for identity, experiences, powers and speech. Adaptation-only facts must not replace novel facts; fan consensus may fill mundane reactions only.

- [ ] **Step 2: Build, test and inspect generated profiles**

Run the full regression suite and reviewer; reject profiles with generic motivation, repeated filth seeds or instant attraction.

- [ ] **Step 3: Commit the batch**

```powershell
git add plot/characters.yaml plot/character_sources.yaml worldbook/角色
git commit -m "Add Chinese web-novel heroines to Sanctum"
```

### Task 9: Expand classical, mythic and historical-literary profiles

**Files:**
- Modify: `plot/characters.yaml`
- Modify: `plot/character_sources.yaml`
- Generate: `worldbook/角色/*.md`

- [ ] **Step 1: Research primary texts and add the batch**

For Red Chamber and classical characters, distinguish textual facts from later screen adaptations and popular fan interpretation. Keep period-specific speech and social constraints while allowing runtime cross-era reconstruction.

- [ ] **Step 2: Build and run content-quality checks**

Expected: no aliases collide, each classical profile names its source work, and every role has a distinct active objective.

- [ ] **Step 3: Commit the batch**

```powershell
git add plot/characters.yaml plot/character_sources.yaml worldbook/角色
git commit -m "Add classical heroines to Sanctum"
```

### Task 10: Expand public-figure profiles and reach exactly 150

**Files:**
- Modify: `plot/characters.yaml`
- Modify: `plot/character_sources.yaml`
- Generate: `worldbook/角色/*.md`

- [ ] **Step 1: Add the requested public-figure batch from public sources**

Use public career history, representative works, interviews and publicly observable professional style. Do not invent private events, private relationships or hidden psychology.

- [ ] **Step 2: Enforce exact roster count and complete build**

Run: `python scripts/test_shengtang_regressions.py`

Expected: exactly 150 profiles, 150 generated world-book profiles, all source and independence checks pass.

- [ ] **Step 3: Commit the completed roster**

```powershell
git add plot/characters.yaml plot/character_sources.yaml worldbook/角色 src/shengtang/ui/cover/index.html src/shengtang/ui/status/index.html
git commit -m "Complete Sanctum 150-role roster"
```

### Task 11: Integrated browser, card and release review

**Files:**
- Modify if defects found: source files owned by Tasks 1-10
- Generate: `dist/shengtang/ui/cover/index.html`
- Generate: `dist/shengtang/ui/status/index.html`
- Generate: `圣堂初遇.json`

- [ ] **Step 1: Run full regressions and Superpower review**

Run: `python scripts/test_shengtang_regressions.py`

Run: `python scripts/superpower_shengtang_review.py`

Expected: zero test failures and zero reviewer errors.

- [ ] **Step 2: Audit real Chrome rendering**

Exercise ability preset/manual/random, normal generation, one-click random, reveal, cancel, retry and status multi-role switching at 360x800, 768x1024 and 1280x720. Assert no page/body overflow, clipped/offscreen buttons, internal copy or console errors.

- [ ] **Step 3: Commit and push static release**

Copy static UI, force-add only the two release HTML files, commit and push. Record the full immutable static commit SHA.

- [ ] **Step 4: Rebuild card against the immutable SHA**

Set `ST_CDN_REF` to the full static SHA and increment `ST_CDN_V`, then run `python build_shengtang_card.py`. Verify card cover/status URLs contain that exact SHA and version.

- [ ] **Step 5: Commit and push the card release**

Commit `圣堂初遇.json`, integrate any bot bundle commit without force-pushing, and push `main`.

- [ ] **Step 6: Verify immutable delivery**

Check both pinned CDN URLs return HTTP 200 and contain the new reveal/status markers. Re-run full regressions and reviewer after fetching the final remote state.
