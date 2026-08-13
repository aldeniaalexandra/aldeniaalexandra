# Ube greenfield design

## Summary

Ube is an original, reusable GitHub profile generator. It turns a user's rolling contribution calendar into a polished looping GIF where a small purple pixel character walks above the graph. The project owns its source code, configuration format, assets, character design, animation system, renderer, GitHub integration, CLI, and Action packaging.

The implementation must not import, copy, adapt, or execute Awan code. Legacy Awan configuration, workflow, character, and generated assets will be removed rather than migrated.

## Goals

- Produce a clean, charming banner that reads well in light and dark GitHub themes.
- Keep every animation deterministic so the same config and contribution fixture produce identical frames.
- Offer one reusable JavaScript Action and one local CLI backed by the same engine.
- Require only the GitHub-provided token in Actions and one small generic GIF encoder at runtime.
- Keep the renderer independent of GitHub so it can be tested entirely offline.
- Make the default Ube character original, compact, recognizable, and easy to replace with another valid sprite pack.

## Non-goals

- A general terminal companion or general-purpose animation engine.
- Interactive browser editing in the first release.
- Text dialogue, weather, music, mini-games, or unrelated profile statistics.
- Automatic git commits inside the Action. The consumer workflow owns repository writes.
- Compatibility with Awan files or character schemas.

## Technology

- TypeScript compiled to bundled JavaScript.
- Node.js 24 for the JavaScript Action.
- Native `fetch` for GitHub GraphQL requests.
- A fixed indexed palette and an in-house pixel framebuffer and compositor.
- `gifenc` as the only runtime image dependency. Ube provides indexed pixels directly, so it does not need third-party quantization or rasterization.
- Vitest for development tests and a bundler for the checked-in Action artifact.

## Repository layout

```text
src/
  action.ts
  cli.ts
  config/
    load.ts
    schema.ts
  contributions/
    github.ts
    normalize.ts
    types.ts
  character/
    load.ts
    types.ts
  animation/
    timeline.ts
    walk-cycle.ts
  render/
    framebuffer.ts
    primitives.ts
    scene.ts
    palette.ts
  output/
    gif.ts
characters/
  ube.json
tests/
  fixtures/
  unit/
  integration/
action.yml
ube.config.json
package.json
tsconfig.json
vitest.config.ts
```

## Public interfaces

### Configuration

`ube.config.json` is an original, versioned schema:

```json
{
  "version": 1,
  "github": {
    "username": "aldeniaalexandra"
  },
  "character": "characters/ube.json",
  "output": {
    "path": "assets/ube.gif",
    "width": 960,
    "height": 320,
    "fps": 12.5,
    "durationSeconds": 9.6
  },
  "theme": {
    "background": "#0d1117",
    "gridEmpty": "#21262d",
    "gridLevels": ["#0e4429", "#006d32", "#26a641", "#39d353"],
    "accent": "#8a63e8"
  }
}
```

Unknown keys and invalid ranges fail fast with the exact JSON path in the error. Paths resolve relative to the config file.

### Character pack

`characters/ube.json` contains a schema version, palette, pixel scale, anchor, and named frame matrices. It does not contain executable code. All frames have identical dimensions and may reference only declared palette symbols.

The initial pack defines `idle`, `blink`, and four asymmetric walk frames. Ube has a compact yam-like silhouette, a small off-center sprout, dot eyes, no permanent mouth, and short feet. The walk cycle alternates contact and passing poses, while the timeline adds a restrained one-pixel vertical bob.

### CLI

```text
ube generate --config ube.config.json
ube generate --config ube.config.json --fixture tests/fixtures/calendar.json
ube validate --config ube.config.json
```

`generate` reads `GITHUB_TOKEN` unless an explicit fixture is supplied. Fixture mode never contacts the network.

### GitHub Action

The Action accepts `config`, `token`, and optional `output` inputs. It generates the banner and exposes the resolved output path. It never stages, commits, or pushes files.

## Data flow

1. Load and validate the project and character configs.
2. Fetch the rolling contribution calendar through GitHub GraphQL, or load an explicit fixture.
3. Normalize dates into 53 ordered weeks with seven days each and levels from zero through four.
4. Build a deterministic timeline from frame index, FPS, and duration.
5. Render each frame into an indexed pixel buffer using Ube's fixed palette.
6. Pass the indexed frames and delays to the GIF adapter.
7. Write to a temporary sibling file and rename it to the final output only after encoding succeeds.

No GitHub response objects enter the renderer. No network or filesystem calls occur inside animation and rendering modules.

## Visual and motion design

The default canvas is 960 by 320 pixels with a 3:1 aspect ratio. The composition uses a quiet dark background, generous empty space, and the familiar five contribution intensities without copying GitHub's surrounding UI.

The 53 by 7 contribution grid sits in the lower half as a continuous trail. Ube walks on a thin baseline immediately above it. The character remains large enough to read when GitHub scales the banner down, but small enough that the contribution year stays central.

The 9.6-second loop contains exactly 120 frames at an 80 ms GIF delay and has three beats:

1. Ube enters from outside the left edge and settles into the walk.
2. Ube crosses the calendar at a constant pixel cadence with a four-frame gait, periodic deterministic blinks, and a one-pixel bob.
3. Ube exits fully beyond the right edge. The first and final visible frames therefore share the same character-free background and loop without a jump.

Contribution cells light with a subtle left-to-right wake as Ube passes. The effect changes brightness within the existing palette and never obscures the actual contribution level.

## GitHub integration

The client queries the selected user's contribution calendar over GitHub GraphQL with a bearer token supplied by the caller. It requests only fields required for date and contribution level. The token is never persisted or logged.

The client validates usernames, enforces a request timeout, checks HTTP and GraphQL errors, and rejects malformed calendars. The normalizer explicitly fills missing dates with zero-level cells so renderer input always has a stable shape.

## Error handling

- Configuration errors name the file and JSON path.
- Character errors name the frame, row, column, and unknown palette symbol.
- API errors distinguish authentication, user-not-found, rate limiting, timeout, and malformed responses.
- Rendering errors reject invalid dimensions, palette overflow, and impossible frame counts before allocation.
- Output is written atomically, leaving the previous GIF intact on failure.
- The Action reports errors through a nonzero exit and a concise workflow annotation.

## Testing

- Unit tests cover config parsing, path resolution, username validation, calendar normalization, timeline states, gait selection, framebuffer clipping, and palette mapping.
- Character contract tests verify frame dimensions, symbols, anchors, and required states.
- Determinism tests hash selected rendered frames from a fixed calendar fixture.
- Integration tests generate a complete GIF offline and verify its signature, dimensions, loop metadata, frame count, and nonempty frame payloads.
- CLI tests cover successful fixture generation and representative failure messages.
- Build verification confirms the bundled Action starts on Node 24 without `node_modules` in the consumer repository.

## Consumer workflow

The profile workflow checks out the repository, runs the Ube Action, then commits only when `assets/ube.gif` changed. Its permissions are limited to `contents: write`. It runs manually, on relevant source changes, and once per day for fresh contributions.

## Migration

The implementation removes:

- `.github/workflows/awan.yml`
- `awan.json`
- `characters/mine.toml`
- `assets/awan.gif`

It replaces them with Ube source, configs, workflow, generated output, tests, and a product README. No compatibility shim or copied legacy asset remains.

## Acceptance criteria

- A fresh checkout can install, test, build, and generate the fixture-backed banner locally.
- The generated GIF is deterministic and loops without a visible reset.
- Ube's sprite and gait are original and defined only in the new character pack.
- A reusable JavaScript Action generates a banner from GitHub contribution data.
- The profile workflow refreshes the banner without any Awan reference or dependency.
- Repository-wide search finds no Awan references in product, runtime, workflow, asset, or README files. Historical design documents may name the removed dependency only to record the independence requirement.
