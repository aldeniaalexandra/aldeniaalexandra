# Ube Greenfield Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an original reusable GitHub Action and CLI that renders a polished looping GIF of Ube walking across a user's contribution calendar.

**Architecture:** A GitHub adapter normalizes GraphQL data into a stable 53-by-7 domain model. A deterministic timeline and in-house indexed-pixel renderer turn that model plus an original JSON character pack into frames; a thin `gifenc` adapter writes the GIF. The CLI and JavaScript Action call the same orchestration function.

**Tech Stack:** TypeScript 7.0.2, Node.js 24 for Actions, `gifenc` 1.0.3, Vitest 4.1.10, esbuild 0.28.2.

## Global Constraints

- Do not import, copy, adapt, execute, or retain Awan code, schemas, assets, workflows, or product references.
- Runtime image dependency is limited to `gifenc` 1.0.3; native `fetch` handles GitHub GraphQL.
- `ube.config.json` and `characters/ube.json` use original versioned schemas.
- Rendering is deterministic for identical config, character, calendar, and render date.
- The Action generates files but never stages, commits, or pushes them.
- The default GIF is 960 by 320, 120 frames, and 80 ms per frame.
- Source files remain focused and expose the exact interfaces declared below.

---

## File map

```text
src/
  action.ts                         Action protocol adapter
  cli.ts                            Argument parsing and terminal errors
  generate.ts                       Shared generation orchestration
  config/load.ts                    JSON loading and relative path resolution
  config/schema.ts                  Runtime config validation and types
  contributions/github.ts          Authenticated GraphQL request
  contributions/normalize.ts       Stable 53-by-7 calendar construction
  contributions/types.ts           Contribution domain types
  character/load.ts                 Character JSON loading and validation
  character/types.ts                Character pack types
  animation/timeline.ts             Position, pose, blink, and wake sampling
  render/framebuffer.ts             Indexed pixel storage and clipping
  render/palette.ts                 Hex parsing and palette indexing
  render/primitives.ts              Rectangles and sprite drawing
  render/scene.ts                   Banner composition
  output/gif.ts                     `gifenc` boundary and atomic output
  types/gifenc.d.ts                 Minimal local declaration for `gifenc`
scripts/build.mjs                   CLI and Action bundling
characters/ube.json                 Original Ube sprite pack
tests/fixtures/calendar.json        Deterministic normalized calendar
tests/fixtures/github-response.json Deterministic GraphQL-shaped response
tests/unit/*.test.ts                Focused unit tests
tests/integration/*.test.ts         Offline CLI and GIF tests
action.yml                          Reusable JavaScript Action metadata
ube.config.json                     Default project config
```

### Task 1: Project foundation and configuration contract

**Files:**
- Create: `package.json`
- Create: `package-lock.json`
- Create: `tsconfig.json`
- Create: `vitest.config.ts`
- Create: `scripts/build.mjs`
- Create: `src/config/schema.ts`
- Create: `src/config/load.ts`
- Create: `tests/unit/config.test.ts`
- Create: `ube.config.json`

**Interfaces:**
- Produces: `validateConfig(value: unknown): UbeConfig`
- Produces: `loadConfig(path: string): Promise<ResolvedConfig>`
- Produces: `UbeConfig`, `ResolvedConfig`, and `ConfigError`

- [ ] **Step 1: Add the TypeScript toolchain**

Create `package.json` with ESM, `gifenc` 1.0.3 as the only runtime dependency, exact development versions from the header, Node `>=20`, a `ube` bin pointing to `dist/cli.js`, and scripts for `test`, `typecheck`, `build`, and `generate:fixture`. Create strict TypeScript and Vitest configs plus an esbuild script that bundles `src/cli.ts` and `src/action.ts` for Node.

- [ ] **Step 2: Write the failing configuration tests**

```ts
it("resolves character and output paths from the config directory", async () => {
  const loaded = await loadConfig(fixturePath("valid/ube.config.json"));
  expect(loaded.characterPath).toBe(fixturePath("valid/characters/ube.json"));
  expect(loaded.outputPath).toBe(fixturePath("valid/assets/ube.gif"));
});

it("reports the exact path of an invalid width", () => {
  expect(() => validateConfig(configWith({ output: { width: 0 } })))
    .toThrow("output.width must be an integer between 320 and 1600");
});
```

- [ ] **Step 3: Run the configuration test and confirm failure**

Run: `npm test -- tests/unit/config.test.ts`

Expected: FAIL because `src/config/load.ts` and `src/config/schema.ts` do not exist.

- [ ] **Step 4: Implement strict config validation**

Define this public shape and reject unknown keys at every object level:

```ts
export interface UbeConfig {
  version: 1;
  github: { username: string };
  character: string;
  output: {
    path: string;
    width: number;
    height: number;
    fps: number;
    durationSeconds: number;
  };
  theme: {
    background: string;
    gridEmpty: string;
    gridLevels: [string, string, string, string];
    accent: string;
  };
}

export interface ResolvedConfig extends UbeConfig {
  configPath: string;
  characterPath: string;
  outputPath: string;
}
```

Validate username with `/^[a-z\d](?:[a-z\d-]{0,37}[a-z\d])?$/i`, colors with `/^#[0-9a-f]{6}$/i`, width `320..1600`, height `160..800`, FPS `1..25`, duration `2..30`, and maximum frame count `300`.

- [ ] **Step 5: Run config tests, typecheck, and commit**

Run: `npm test -- tests/unit/config.test.ts && npm run typecheck`

Expected: PASS.

Commit: `feat: define Ube project configuration`

### Task 2: Original Ube character pack and loader

**Files:**
- Create: `src/character/types.ts`
- Create: `src/character/load.ts`
- Create: `characters/ube.json`
- Create: `tests/unit/character.test.ts`

**Interfaces:**
- Produces: `loadCharacter(path: string): Promise<CharacterPack>`
- Produces: `validateCharacter(value: unknown): CharacterPack`
- Produces: `SpriteFrame`, `CharacterPack`, and `CharacterError`

- [ ] **Step 1: Write failing character contract tests**

```ts
it("loads the original Ube pack with four walk poses", async () => {
  const ube = await loadCharacter(projectPath("characters/ube.json"));
  expect(ube.name).toBe("Ube");
  expect(ube.frames.walk).toHaveLength(4);
  expect(new Set(Object.values(ube.frames).flat(2).map(row => row.length)))
    .toEqual(new Set([12]));
});

it("points to an undeclared symbol", () => {
  expect(() => validateCharacter(packWithFrame(["PX?"])))
    .toThrow("frames.idle[0][2] uses undeclared symbol '?'");
});
```

- [ ] **Step 2: Run the character test and confirm failure**

Run: `npm test -- tests/unit/character.test.ts`

Expected: FAIL because the character loader does not exist.

- [ ] **Step 3: Define and validate the character schema**

```ts
export interface CharacterPack {
  version: 1;
  name: string;
  cellSize: number;
  anchor: { x: number; y: number };
  palette: Record<string, string>;
  frames: {
    idle: SpriteFrame;
    blink: SpriteFrame;
    walk: [SpriteFrame, SpriteFrame, SpriteFrame, SpriteFrame];
  };
}

export type SpriteFrame = readonly string[];
```

Require one-character palette symbols, identical 12-by-8 frames, transparent spaces, valid hex colors, `cellSize` from two through eight, and anchors within the frame.

- [ ] **Step 4: Add the original Ube sprite**

Use a purple yam-like 12-by-8 silhouette with an off-center two-pixel sprout, one-pixel eyes, no drawn mouth, a shaded base, and these four leg rows:

```text
"   PP   PP  "
"  PP     PP "
"    PP PP   "
"    PP  PP  "
```

The pack palette uses `P=#8A63E8`, `H=#BFAAFF`, `S=#6845C6`, and `E=#171225`. Blink replaces the two eye pixels with shadow pixels.

- [ ] **Step 5: Run character tests and commit**

Run: `npm test -- tests/unit/character.test.ts && npm run typecheck`

Expected: PASS.

Commit: `feat: add the original Ube character pack`

### Task 3: Contribution calendar normalization

**Files:**
- Create: `src/contributions/types.ts`
- Create: `src/contributions/normalize.ts`
- Create: `tests/fixtures/calendar.json`
- Create: `tests/unit/normalize.test.ts`

**Interfaces:**
- Produces: `normalizeCalendar(days: readonly RawContributionDay[], endDate: string): ContributionCalendar`
- Produces: `ContributionLevel`, `ContributionDay`, `ContributionCalendar`, and `RawContributionDay`

- [ ] **Step 1: Write failing normalization tests**

```ts
it("returns 53 Sunday-aligned weeks and fills absent dates", () => {
  const calendar = normalizeCalendar([
    { date: "2026-08-13", count: 3, level: 2 }
  ], "2026-08-13");
  expect(calendar.weeks).toHaveLength(53);
  expect(calendar.weeks.every(week => week.length === 7)).toBe(true);
  expect(calendar.weeks.at(-1)?.[4]).toMatchObject({
    date: "2026-08-13", count: 3, level: 2
  });
});

it("rejects duplicate dates", () => {
  expect(() => normalizeCalendar([day, day], "2026-08-13"))
    .toThrow("duplicate contribution date 2026-08-13");
});
```

- [ ] **Step 2: Run the normalizer tests and confirm failure**

Run: `npm test -- tests/unit/normalize.test.ts`

Expected: FAIL because the calendar domain does not exist.

- [ ] **Step 3: Implement date-only normalization**

Use UTC date arithmetic, map exactly 371 positions from the Sunday 52 weeks before the current display week, preserve contribution counts and levels, fill missing and future dates with zero, and freeze the returned nested arrays.

- [ ] **Step 4: Add a deterministic calendar fixture**

Create `tests/fixtures/calendar.json` from an explicit mathematical pattern: every fifth day is level one, every eleventh day level two, every twenty-third day level three, and every forty-seventh day level four. Store all 371 date/count/level entries so tests never depend on current time.

- [ ] **Step 5: Run normalization tests and commit**

Run: `npm test -- tests/unit/normalize.test.ts && npm run typecheck`

Expected: PASS.

Commit: `feat: normalize contribution calendars`

### Task 4: GitHub GraphQL adapter

**Files:**
- Create: `src/contributions/github.ts`
- Create: `tests/fixtures/github-response.json`
- Create: `tests/unit/github.test.ts`

**Interfaces:**
- Consumes: `RawContributionDay` from `src/contributions/types.ts`
- Produces: `fetchContributionDays(options: FetchContributionOptions): Promise<RawContributionDay[]>`
- `FetchContributionOptions` contains `username`, `token`, `from`, `to`, optional `fetchImpl`, and optional `timeoutMs`.

- [ ] **Step 1: Write failing GitHub adapter tests**

```ts
it("maps GraphQL levels without leaking the token", async () => {
  const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(githubFixture));
  const days = await fetchContributionDays({
    username: "aldeniaalexandra",
    token: "secret-token",
    from: "2025-08-10T00:00:00Z",
    to: "2026-08-13T23:59:59Z",
    fetchImpl
  });
  expect(days[0]).toEqual({ date: "2025-08-10", count: 0, level: 0 });
  expect(fetchImpl).toHaveBeenCalledWith("https://api.github.com/graphql", expect.objectContaining({ method: "POST" }));
});

it("classifies rate limiting", async () => {
  const fetchImpl = vi.fn().mockResolvedValue(new Response("", { status: 403 }));
  await expect(fetchContributionDays(validOptions(fetchImpl)))
    .rejects.toThrow("GitHub rate limit or permission error");
});
```

- [ ] **Step 2: Run the GitHub tests and confirm failure**

Run: `npm test -- tests/unit/github.test.ts`

Expected: FAIL because the adapter does not exist.

- [ ] **Step 3: Implement the isolated GraphQL client**

Query only `user.contributionsCollection.contributionCalendar.weeks.contributionDays` with `date`, `contributionCount`, and `contributionLevel`. Map `NONE`, `FIRST_QUARTILE`, `SECOND_QUARTILE`, `THIRD_QUARTILE`, and `FOURTH_QUARTILE` to zero through four. Use `AbortSignal.timeout(10_000)` by default and never include authorization headers in error messages.

- [ ] **Step 4: Run GitHub tests and commit**

Run: `npm test -- tests/unit/github.test.ts && npm run typecheck`

Expected: PASS.

Commit: `feat: fetch GitHub contribution data`

### Task 5: Indexed framebuffer, palette, and sprite primitives

**Files:**
- Create: `src/render/framebuffer.ts`
- Create: `src/render/palette.ts`
- Create: `src/render/primitives.ts`
- Create: `tests/unit/framebuffer.test.ts`
- Create: `tests/unit/primitives.test.ts`

**Interfaces:**
- Produces: `class FrameBuffer { readonly pixels: Uint8Array; setPixel(); fillRect(); clear(); }`
- Produces: `class Palette { index(hex: string): number; toRgb(): number[][]; }`
- Produces: `drawSprite(buffer, frame, pack, originX, baselineY): void`

- [ ] **Step 1: Write failing raster tests**

```ts
it("clips rectangles without reallocating", () => {
  const frame = new FrameBuffer(4, 3, 0);
  frame.fillRect(-1, 1, 3, 3, 2);
  expect([...frame.pixels]).toEqual([0,0,0,0, 2,2,0,0, 2,2,0,0]);
});

it("draws transparent sprite cells and respects the anchor", () => {
  drawSprite(frame, [" P", "PP"], pack, 2, 4);
  expect(frame.getPixel(2, 3)).toBe(0);
  expect(frame.getPixel(3, 3)).toBe(purpleIndex);
});
```

- [ ] **Step 2: Run raster tests and confirm failure**

Run: `npm test -- tests/unit/framebuffer.test.ts tests/unit/primitives.test.ts`

Expected: FAIL because the render modules do not exist.

- [ ] **Step 3: Implement the indexed pixel core**

Store one palette index per canvas pixel. Clip at primitive boundaries, validate all dimensions before allocation, reserve palette index zero for the configured background, deduplicate uppercase hex values, and reject the 257th color. `drawSprite` expands each source cell by `character.cellSize` and skips spaces.

- [ ] **Step 4: Run raster tests and commit**

Run: `npm test -- tests/unit/framebuffer.test.ts tests/unit/primitives.test.ts && npm run typecheck`

Expected: PASS.

Commit: `feat: add indexed pixel renderer`

### Task 6: Distance-driven animation timeline

**Files:**
- Create: `src/animation/timeline.ts`
- Create: `src/animation/walk-cycle.ts`
- Create: `tests/unit/timeline.test.ts`

**Interfaces:**
- Produces: `sampleTimeline(frameIndex: number, options: TimelineOptions): TimelineSample`
- `TimelineSample` is `{ x: number; bob: 0 | -1; pose: 0 | 1 | 2 | 3; blink: boolean; wakeColumn: number }`.

- [ ] **Step 1: Write failing motion tests**

```ts
it("starts and ends fully outside the canvas", () => {
  expect(sampleTimeline(0, options).x).toBe(-options.characterWidth);
  expect(sampleTimeline(119, options).x).toBeGreaterThanOrEqual(options.canvasWidth);
});

it("advances gait by distance instead of elapsed frames", () => {
  const samples = [20, 21, 22, 23].map(i => sampleTimeline(i, options));
  for (let i = 1; i < samples.length; i += 1) {
    if (samples[i].x === samples[i - 1].x) {
      expect(samples[i].pose).toBe(samples[i - 1].pose);
    }
  }
});
```

- [ ] **Step 2: Run timeline tests and confirm failure**

Run: `npm test -- tests/unit/timeline.test.ts`

Expected: FAIL because the animation modules do not exist.

- [ ] **Step 3: Implement deterministic motion**

Interpolate the anchor from `-characterWidth` to `canvasWidth + characterWidth` across 120 frames. Quantize x to integer pixels. Select the four walk poses with `Math.floor(distance / stridePixels) % 4`, derive bob from poses one and three, blink on fixed frame windows 34-35 and 82-83, and compute the wake column by comparing Ube's center with the grid bounds.

- [ ] **Step 4: Run motion tests and commit**

Run: `npm test -- tests/unit/timeline.test.ts && npm run typecheck`

Expected: PASS.

Commit: `feat: animate Ube with a distance-driven gait`

### Task 7: Contribution scene composition

**Files:**
- Create: `src/render/scene.ts`
- Create: `tests/unit/scene.test.ts`

**Interfaces:**
- Consumes: `ContributionCalendar`, `CharacterPack`, `ResolvedConfig`, and `TimelineSample`.
- Produces: `createScene(config, character): Scene`
- Produces: `Scene.render(calendar, frameIndex): IndexedFrame`
- `IndexedFrame` is `{ width: number; height: number; pixels: Uint8Array; palette: number[][] }`.

- [ ] **Step 1: Write failing scene snapshot tests**

```ts
it("renders the graph at a stable 53 by 7 layout", () => {
  const frame = scene.render(calendarFixture, 60);
  expect(countCellOrigins(frame.pixels, scene.layout)).toBe(371);
  expect(frame.width).toBe(960);
  expect(frame.height).toBe(320);
});

it("produces stable hashes for entrance, midpoint, and exit", () => {
  expect([0, 60, 119].map(i => sha256(scene.render(calendarFixture, i).pixels)))
    .toEqual(EXPECTED_FRAME_HASHES);
});
```

- [ ] **Step 2: Run scene tests and confirm failure**

Run: `npm test -- tests/unit/scene.test.ts`

Expected: FAIL because scene composition does not exist.

- [ ] **Step 3: Compose the original banner**

Center a 53-by-7 grid with ten-pixel cells and five-pixel gaps in the lower half. Paint three subtle background bands derived from the configured background and accent. Place Ube's baseline eight pixels above the graph. Render the true contribution level first, then brighten only the current wake column by one palette step. Draw Ube last so the silhouette remains crisp.

- [ ] **Step 4: Freeze the accepted frame hashes and commit**

Run the scene test once to capture the three actual SHA-256 values, place those literal hashes in `EXPECTED_FRAME_HASHES`, rerun the test, and visually inspect exported PNG debug frames at native scale before removing those untracked debug files.

Run: `npm test -- tests/unit/scene.test.ts && npm run typecheck`

Expected: PASS with the literal hashes.

Commit: `feat: render Ube contribution scenes`

### Task 8: GIF output and shared generation pipeline

**Files:**
- Create: `src/types/gifenc.d.ts`
- Create: `src/output/gif.ts`
- Create: `src/generate.ts`
- Create: `tests/integration/gif.test.ts`

**Interfaces:**
- Produces: `encodeGif(frames: readonly IndexedFrame[], delayMs: number): Uint8Array`
- Produces: `writeGifAtomic(path: string, bytes: Uint8Array): Promise<void>`
- Produces: `generate(options: GenerateOptions): Promise<GenerateResult>`
- `GenerateOptions` contains `configPath`, optional `outputPath`, optional `fixturePath`, optional `token`, and optional `now`.

- [ ] **Step 1: Write a failing offline GIF integration test**

```ts
it("generates a looping 960 by 320 GIF with 120 frames", async () => {
  const result = await generate({
    configPath: projectPath("ube.config.json"),
    fixturePath: fixturePath("calendar.json"),
    outputPath,
    now: new Date("2026-08-13T12:00:00Z")
  });
  const bytes = await readFile(outputPath);
  expect(bytes.subarray(0, 6).toString("ascii")).toBe("GIF89a");
  expect(readLogicalScreen(bytes)).toEqual({ width: 960, height: 320 });
  expect(countGraphicControlExtensions(bytes)).toBe(120);
  expect(hasInfiniteLoopExtension(bytes)).toBe(true);
  expect(result.frames).toBe(120);
});
```

- [ ] **Step 2: Run the GIF test and confirm failure**

Run: `npm test -- tests/integration/gif.test.ts`

Expected: FAIL because encoding and orchestration do not exist.

- [ ] **Step 3: Implement the narrow `gifenc` adapter**

Pass the shared RGB palette and each indexed frame to `GIFEncoder().writeFrame()` with `delay: 80`, `repeat: 0`, and full-frame disposal. Finish once and copy `encoder.bytes()` into a standalone `Uint8Array`. Keep every `gifenc` type inside `src/types/gifenc.d.ts` and `src/output/gif.ts`.

- [ ] **Step 4: Implement orchestration and atomic writes**

Load config and character, load a normalized fixture or fetch GitHub days, create 120 scene frames, encode them, write `<output>.tmp`, and rename only after success. Delete only the temporary file when generation fails.

- [ ] **Step 5: Run GIF tests and commit**

Run: `npm test -- tests/integration/gif.test.ts && npm run typecheck`

Expected: PASS.

Commit: `feat: generate deterministic Ube GIFs`

### Task 9: CLI, JavaScript Action, and profile workflow

**Files:**
- Create: `src/cli.ts`
- Create: `src/action.ts`
- Create: `action.yml`
- Create: `tests/integration/cli.test.ts`
- Replace: `.github/workflows/awan.yml` with `.github/workflows/ube.yml`
- Create: `dist/cli.js`
- Create: `dist/action.js`

**Interfaces:**
- Consumes: `generate()` and `loadConfig()`.
- Produces: CLI commands `generate` and `validate`.
- Produces: Action output `path` through `$GITHUB_OUTPUT`.

- [ ] **Step 1: Write failing CLI tests**

```ts
it("generates from a fixture and prints the output path", async () => {
  const result = await runCli(["generate", "--config", configPath, "--fixture", fixturePath]);
  expect(result.exitCode).toBe(0);
  expect(result.stdout).toContain("Generated 120 frames");
});

it("requires a token outside fixture mode", async () => {
  const result = await runCli(["generate", "--config", configPath], { GITHUB_TOKEN: "" });
  expect(result.exitCode).toBe(1);
  expect(result.stderr).toContain("GITHUB_TOKEN is required unless --fixture is used");
});
```

- [ ] **Step 2: Run CLI tests and confirm failure**

Run: `npm test -- tests/integration/cli.test.ts`

Expected: FAIL because CLI and Action adapters do not exist.

- [ ] **Step 3: Implement dependency-free adapters**

Parse the declared CLI flags without a parser library. In the Action, read `INPUT_CONFIG`, `INPUT_TOKEN`, and `INPUT_OUTPUT`, sanitize workflow command text, append `path=<resolved path>` to `$GITHUB_OUTPUT`, and set a nonzero exit code on error. Never print the token.

- [ ] **Step 4: Add Action metadata and original workflow**

Set `runs.using` to `node24` and `runs.main` to `dist/action.js`. The profile workflow checks out the repository, passes `${{ github.token }}`, commits only `assets/ube.gif` when changed, and runs on manual dispatch, a daily schedule, and pushes affecting Ube source/config.

- [ ] **Step 5: Bundle, test, and commit**

Run: `npm run build && npm test && npm run typecheck`

Expected: PASS and both bundles exist without runtime imports outside Node built-ins.

Commit: `feat: ship Ube CLI and GitHub Action`

### Task 10: Remove legacy integration and publish the original README

**Files:**
- Delete: `awan.json`
- Delete: `characters/mine.toml`
- Delete: `assets/awan.gif`
- Create: `assets/ube.gif`
- Replace: `README.md`
- Create: `LICENSE`

**Interfaces:**
- Consumes: bundled CLI and fixture generation command.
- Produces: a self-contained public project with installation and workflow documentation.

- [ ] **Step 1: Generate the checked-in banner from the fixture**

Run: `npm run generate:fixture`

Expected: `assets/ube.gif` is created with 960-by-320 dimensions and 120 frames.

- [ ] **Step 2: Remove the legacy files**

Delete only the three explicit legacy paths listed above after confirming their resolved paths remain inside the repository. Confirm `.github/workflows/awan.yml` was replaced in Task 9.

- [ ] **Step 3: Write the product README and license**

The English README leads with the generated Ube GIF and the line "Your contribution graph has a tiny resident." It explains the one-workflow setup, configuration, character format, local commands, architecture, privacy, and development checks. Keep the voice playful and concise, without RPG terminology or claims that depend on Awan. Add the MIT license under `Aldenia Alexandra` for 2026.

- [ ] **Step 4: Run repository-wide independence and quality checks**

Run:

```powershell
npm ci
npm run typecheck
npm test
npm run build
npm run generate:fixture
git diff --check
rg -n -i "awan|codewithwan" --glob "!docs/superpowers/**" --glob "!.git/**"
```

Expected: all build and test commands pass; the final search returns no matches.

- [ ] **Step 5: Inspect the final GIF and commit**

Inspect the native-size animation and confirm the silhouette, blink, gait, contribution levels, wake, and loop are readable. Verify `git status --short` contains only intended Ube changes.

Commit: `feat: launch the original Ube contribution companion`

## Final verification

- [ ] Run `npm ci && npm run typecheck && npm test && npm run build` from a clean dependency install.
- [ ] Generate twice from the fixture and verify both GIF files have the same SHA-256 hash.
- [ ] Confirm the bundled Action contains no unresolved package imports.
- [ ] Confirm all tracked legacy files are absent and the repository-wide Awan search is empty outside historical design documents.
- [ ] Review the generated GIF at original size and at an 840-pixel README width.
