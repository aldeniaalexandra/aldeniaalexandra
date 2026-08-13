# Ube repository split design

## Goal

Keep `aldeniaalexandra/aldeniaalexandra` as a personal profile repository. Move Ube's reusable implementation and product documentation into a dedicated public repository at `aldeniaalexandra/ube`.

The profile README must retain its existing identity and sections. Ube appears only as the animated hero at the top of that README.

## Repository boundaries

### `aldeniaalexandra/ube`

The new public repository owns:

- the TypeScript renderer and animation engine;
- GitHub contribution fetching and normalization;
- the canonical Ube character pack;
- the CLI and JavaScript Action;
- tests, fixtures, build scripts, bundled Action files, license, and product documentation;
- the deterministic demonstration GIF.

The repository starts with a clean project-focused history rather than carrying the profile repository's unrelated history. Its default branch is `main`.

### `aldeniaalexandra/aldeniaalexandra`

The profile repository owns:

- the personal profile README;
- the generated `assets/ube.gif` displayed by that README;
- `ube.config.json` and a profile-owned character override used to customize the banner;
- a small scheduled workflow that calls `aldeniaalexandra/ube@main`, refreshes the GIF, and commits it only when it changes.

It must not contain Ube's source tree, tests, bundled runtime, package metadata, product README, or internal design documents.

## Profile presentation

Restore the README from the last profile-focused revision. Preserve the Inventory, Quest Log, Trophy Cabinet, Party Up, badges, links, and personal copy. Replace the old Awan hero reference with:

```markdown
![Ube walking through my contribution year](assets/ube.gif)
```

No Ube installation guide or project documentation belongs in the profile README.

## Action flow

The profile workflow checks out the profile repository, runs the Action from `aldeniaalexandra/ube@main`, and commits only `assets/ube.gif` when generation changes it.

The Action reads the profile repository's `ube.config.json`, uses the supplied GitHub token to fetch contribution data, and writes the configured GIF path. Ube's Action repository remains the implementation source; the profile repository remains the data and presentation consumer.

## Migration

1. Create a clean local Ube repository from the current Ube implementation.
2. verify its tests, typecheck, build, bundled Action, fixture generation, and independence from the old Awan implementation;
3. create the public `aldeniaalexandra/ube` repository and push `main`;
4. restore the profile README and reduce the profile repository to its consumer files;
5. update the profile workflow to call `aldeniaalexandra/ube@main`;
6. verify the profile README references valid local assets and the workflow contains no local Action dependency;
7. push the corrected profile repository only after both local repositories are clean and verified.

## Failure handling

If creation or push of the Ube repository fails, do not strip the implementation from the profile repository yet. If profile verification fails, keep the corrective commit local and leave the remote profile untouched. Never force-push either repository.

## Verification

The Ube repository must pass `npm ci`, `npm run typecheck`, `npm test`, `npm run build`, and deterministic fixture generation. Its bundled files must match a fresh build.

The profile repository must contain the restored personal sections, render `assets/ube.gif`, keep only the intended Ube consumer files, and have a workflow that references `aldeniaalexandra/ube@main`. Both worktrees must be clean before any push.
