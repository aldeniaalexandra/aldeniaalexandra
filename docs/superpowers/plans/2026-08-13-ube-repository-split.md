# Ube Repository Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the complete Ube project into a new public `aldeniaalexandra/ube` repository and restore `aldeniaalexandra/aldeniaalexandra` as a personal profile repository that only consumes Ube.

**Architecture:** The public Ube repository owns the Action, CLI, renderer, tests, character engine, and project documentation. The profile repository keeps its personal README, a generated GIF, profile configuration, character override, and a scheduled consumer workflow. The Ube repository is created and verified before any implementation files are removed from the profile repository.

**Tech Stack:** Git, GitHub CLI, Node.js 20/24, TypeScript, Vitest, esbuild, GitHub Actions

## Global Constraints

- Create public repository `aldeniaalexandra/ube` with default branch `main`.
- Never force-push either repository.
- Preserve Inventory, Quest Log, Trophy Cabinet, Party Up, badges, links, and personal copy in the profile README.
- The profile hero must render `assets/ube.gif` and must not contain Ube product documentation.
- The profile workflow must call `aldeniaalexandra/ube@main`.
- Do not remove Ube implementation files from the profile repository until the new repository has passed its complete verification suite and pushed successfully.

---

### Task 1: Build a clean local Ube repository

**Files:**
- Create repository: `C:/Users/Sandra/orca/ube`
- Copy: `.gitattributes`, `.gitignore`, `.github/workflows/ube.yml`, `LICENSE`, `README.md`, `action.yml`, `assets/ube.gif`, `characters/ube.json`, `dist/**`, `package.json`, `package-lock.json`, `scripts/**`, `src/**`, `tests/**`, `tsconfig.json`, `ube.config.json`, `vitest.config.ts`

**Interfaces:**
- Consumes: verified Ube implementation at profile commit `c2eda2e`
- Produces: standalone local Git repository with branch `main` and one clean launch commit

- [ ] **Step 1: Verify the destination does not already exist**

```powershell
$ubeRepository = "C:\Users\Sandra\orca\ube"
if (Test-Path -LiteralPath $ubeRepository) {
  throw "Destination already exists: $ubeRepository"
}
```

- [ ] **Step 2: Export only Ube-owned files**

```powershell
$ubeRepository = "C:\Users\Sandra\orca\ube"
$archivePath = Join-Path ([System.IO.Path]::GetTempPath()) "ube-repository-split-$([guid]::NewGuid()).tar"
git archive --format=tar --output=$archivePath HEAD -- .gitattributes .gitignore .github/workflows/ube.yml LICENSE README.md action.yml assets/ube.gif characters/ube.json dist package.json package-lock.json scripts src tests tsconfig.json ube.config.json vitest.config.ts
New-Item -ItemType Directory -Path $ubeRepository | Out-Null
tar -xf $archivePath -C $ubeRepository
Remove-Item -LiteralPath $archivePath
```

- [ ] **Step 3: Initialize clean history**

```powershell
$ubeRepository = "C:\Users\Sandra\orca\ube"
git -C $ubeRepository init -b main
git -C $ubeRepository add --all
git -C $ubeRepository commit -m "feat: launch Ube contribution companion"
```

- [ ] **Step 4: Install and verify Ube**

```powershell
$ubeRepository = "C:\Users\Sandra\orca\ube"
Set-Location -LiteralPath $ubeRepository
npm ci
npm run typecheck
npm test
npm run build
npm run generate:fixture
git diff --check
git status --porcelain=v1
```

Expected: 32 tests pass, typecheck and build pass, fixture generates 120 frames at 960 by 320, and the worktree stays clean.

### Task 2: Publish the dedicated Ube repository

**Files:**
- External repository: `https://github.com/aldeniaalexandra/ube`

**Interfaces:**
- Consumes: clean verified repository from Task 1
- Produces: public GitHub Action address `aldeniaalexandra/ube@main`

- [ ] **Step 1: Reconfirm the name is available and authentication is active**

```powershell
$ubeRepository = "C:\Users\Sandra\orca\ube"
gh auth status
gh repo view aldeniaalexandra/ube
```

Expected: authentication succeeds and repository lookup reports that the repository does not exist.

- [ ] **Step 2: Create and push without force**

```powershell
$ubeRepository = "C:\Users\Sandra\orca\ube"
gh repo create aldeniaalexandra/ube --public --source $ubeRepository --remote origin --push --description "A tiny original pixel companion for your GitHub contribution year."
```

- [ ] **Step 3: Verify remote state**

```powershell
$ubeRepository = "C:\Users\Sandra\orca\ube"
gh repo view aldeniaalexandra/ube --json nameWithOwner,visibility,defaultBranchRef,url
git -C $ubeRepository status --short --branch
```

Expected: visibility is `PUBLIC`, default branch is `main`, and local `main` tracks `origin/main` without divergence.

### Task 3: Restore the profile repository

**Files:**
- Modify: `README.md`
- Modify: `.github/workflows/ube.yml`
- Keep: `assets/ube.gif`
- Keep: `ube.config.json`
- Keep: `characters/ube.json`
- Delete: `.gitattributes`, `LICENSE`, `action.yml`, `dist/**`, `package.json`, `package-lock.json`, `scripts/**`, `src/**`, `tests/**`, `tsconfig.json`, `vitest.config.ts`, `docs/**`

**Interfaces:**
- Consumes: public Action `aldeniaalexandra/ube@main`
- Produces: profile-only repository with Ube as a consumer dependency

- [ ] **Step 1: Restore the personal README content**

Write `README.md` from commit `f359afe` and replace only the hero block with:

```markdown
<div align="center">

![Ube walking through my contribution year](assets/ube.gif)

</div>
```

Keep every personal section and link below that block unchanged.

- [ ] **Step 2: Make the workflow consume the external Action**

Set the render step in `.github/workflows/ube.yml` to:

```yaml
- name: Render contribution companion
  uses: aldeniaalexandra/ube@main
  with:
    token: ${{ github.token }}
```

Restrict push path filters to `.github/workflows/ube.yml`, `characters/ube.json`, and `ube.config.json`.

- [ ] **Step 3: Remove project-owned implementation files**

```powershell
git rm -r -- dist docs scripts src tests
git rm -- .gitattributes LICENSE action.yml package.json package-lock.json tsconfig.json vitest.config.ts
```

- [ ] **Step 4: Verify the profile boundary**

```powershell
rg -n "Inventory|Quest Log|Trophy Cabinet|Party Up|assets/ube.gif" README.md
rg -n "uses: aldeniaalexandra/ube@main" .github/workflows/ube.yml
git ls-files src dist tests package.json action.yml
git diff --check
```

Expected: all profile sections and the Ube hero are present, the external Action reference is present, and the implementation-file query returns no paths.

- [ ] **Step 5: Commit the correction**

```powershell
git add --all
git commit -m "fix: restore profile README and consume Ube"
```

### Task 4: Push and verify both repositories

**Files:**
- Remote profile: `https://github.com/aldeniaalexandra/aldeniaalexandra`
- Remote project: `https://github.com/aldeniaalexandra/ube`

**Interfaces:**
- Consumes: verified commits from Tasks 2 and 3
- Produces: live profile README plus standalone public Ube project

- [ ] **Step 1: Pull safely and push the profile correction**

```powershell
git pull --ff-only
git push origin main
```

- [ ] **Step 2: Verify live repository contents**

```powershell
gh api repos/aldeniaalexandra/aldeniaalexandra/readme --jq .html_url
gh api repos/aldeniaalexandra/ube/readme --jq .html_url
gh api repos/aldeniaalexandra/aldeniaalexandra/contents/src
```

Expected: both README endpoints exist and the profile `src` endpoint returns HTTP 404.

- [ ] **Step 3: Confirm clean synchronized worktrees**

```powershell
$ubeRepository = "C:\Users\Sandra\orca\ube"
git status --short --branch
git -C $ubeRepository status --short --branch
```

Expected: both repositories are clean and each `main` branch matches `origin/main`.
