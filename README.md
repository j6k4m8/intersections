# intersections

Generate stylized maps of signal-dense street intersections from OpenStreetMap.

The repository now follows a simple scientific workflow layout:

```text
analysis/
config/
data/
  raw/
  provided/
  generated/
notebooks/
results/
  data/
  figures/
src/
tests/
Snakefile
```

## Quick start

```bash
uv sync
uv run snakemake --cores 1
```

That will:

1. Download raw traffic-signal data into `data/raw/`.
2. Cluster candidate intersections into `data/generated/`.
3. Render final gallery figures into `results/figures/`.
4. Write gallery manifests into `results/data/`.

## Common commands

Run the full pipeline without Snakemake:

```bash
uv run intersections run --city Boston --count 24
```

Rebuild the workflow:

```bash
uv run snakemake --cores 1 --forcerun render_gallery
```

## Viewer

Open [index.html](index.html) through a local web server after generating results. It loads `results/data/latest_manifest.json` by default.

## Notes

-   `config/defaults.toml` controls the default city, output count, clustering radius, and render settings.
-   Use a place name that OpenStreetMap exposes as an area name, for example `Baltimore` or `Boston`.
