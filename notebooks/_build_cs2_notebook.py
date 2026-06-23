"""Programmatic builder for ``cs2_atlantic_hurricane.ipynb``.

This script generates a Jupyter notebook that loads the CS2 pipeline output
(produced by ``mosaic run tests/fixtures/cs2_offline.yaml``) and reproduces
the figures used in the Results section of the CAGEO paper. Mirrors
``_build_cs1_notebook.py``; the plotting recipes are shared with
``_export_cs2_figures.py`` (which renders the same figures headlessly for
the paper itself).

Run from the repository root:

    python notebooks/_build_cs2_notebook.py
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "cs2_atlantic_hurricane.ipynb"
REPO_ROOT = Path(__file__).resolve().parents[1]


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(src: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(src)


def build() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        "mosaic": {
            "case_study": "CS2 — Atlantic hurricane (Ida-like), Aug-Sep 2021",
            "pipeline": "tests/fixtures/cs2_offline.yaml",
            "purpose": "Companion notebook for CAGEO Results section",
        },
    }

    cells: list[nbf.NotebookNode] = []

    # 1. Title + scope ---------------------------------------------------
    cells.append(
        md(
            "# CS2 — Atlantic hurricane (Ida-like), August–September 2021\n"
            "\n"
            "Companion notebook for the *Computers & Geosciences* paper "
            "*An Open Python Framework for Reproducible Multi-Source Ocean Data "
            "Integration*. It loads the Zarr output produced by the offline "
            "fixture pipeline (`tests/fixtures/cs2_offline.yaml`) and "
            "reproduces the figures used in the Results section.\n"
            "\n"
            "**Reproducibility contract.** Re-running this notebook from a fresh "
            "checkout regenerates the identical content hash printed in the final "
            "section. The pipeline is declarative (YAML) and the data sources are "
            "deterministic Gulf-of-Mexico-shaped fixtures that ship with the "
            "repository, so no external credentials are required.\n"
            "\n"
            "**Scope note.** The bundled IBTrACS-style storm track is a synthetic, "
            "Ida-like CSV used only to overlay the storm path on the figures below "
            "for visual context — it is not a pipeline source and does not enter "
            "the harmonized dataset or the `mosaic:content_hash`."
        )
    )

    # 2. Bootstrap ---------------------------------------------------------
    cells.append(md("## 1. Bootstrap — run the pipeline if its output is missing"))
    cells.append(
        code(
            "from __future__ import annotations\n"
            "\n"
            "import json\n"
            "import os\n"
            "from pathlib import Path\n"
            "\n"
            "# Resolve the repository root regardless of where the notebook is launched.\n"
            "NB_DIR = Path.cwd()\n"
            "if NB_DIR.name == 'notebooks':\n"
            "    REPO_ROOT = NB_DIR.parent\n"
            "else:\n"
            "    REPO_ROOT = NB_DIR\n"
            "os.chdir(REPO_ROOT)\n"
            "\n"
            "PIPELINE  = Path('tests/fixtures/cs2_offline.yaml')\n"
            "OUTPUT    = Path('out/cs2_atlantic_hurricane_offline.zarr')\n"
            "SIDECAR   = OUTPUT.with_suffix(OUTPUT.suffix + '.stac.json')\n"
            "TRACK_CSV = Path('tests/fixtures/cs2/ibtracs_ida_like.csv')\n"
            "\n"
            "if not OUTPUT.exists():\n"
            "    # Build synthetic fixtures (deterministic) and run the pipeline.\n"
            "    from tests.fixtures.build_cs2_fixtures import build_all\n"
            "    build_all(REPO_ROOT / 'tests' / 'fixtures' / 'cs2')\n"
            "    import mosaic as ms\n"
            "    ms.run(str(PIPELINE))\n"
            "\n"
            "print(f'output: {OUTPUT} ({OUTPUT.exists()})')\n"
            "print(f'sidecar: {SIDECAR} ({SIDECAR.exists()})')\n"
            "print(f'track: {TRACK_CSV} ({TRACK_CSV.exists()})')"
        )
    )

    # 3. Load --------------------------------------------------------------
    cells.append(
        md(
            "## 2. Load the integrated dataset, its provenance sidecar, and the storm track"
        )
    )
    cells.append(
        code(
            "import pandas as pd\n"
            "import xarray as xr\n"
            "\n"
            "ds = xr.open_zarr(OUTPUT, consolidated=True)\n"
            "with open(SIDECAR) as fh:\n"
            "    stac = json.load(fh)\n"
            "track = pd.read_csv(TRACK_CSV, parse_dates=['ISO_TIME'])\n"
            "\n"
            "print(ds)"
        )
    )
    cells.append(
        code(
            "props = stac['properties']\n"
            "summary = {\n"
            "    'pipeline_hash': props['mosaic:pipeline_hash'],\n"
            "    'content_hash':  props['mosaic:content_hash'],\n"
            "    'sources':       [s['source_id'] for s in props['mosaic:inputs']],\n"
            "    'mapping_accuracy': props['mosaic:harmonization']['mapping_accuracy'],\n"
            "    'derived_variables': props['mosaic:harmonization']['derived']['derived'],\n"
            "}\n"
            "summary"
        )
    )

    # 4. MSLP + wind quiver evolution ---------------------------------------
    cells.append(
        md(
            "## 3. Mean sea-level pressure and wind evolution\n"
            "\n"
            "Four-panel snapshot of `air_pressure_at_mean_sea_level` with 10 m wind "
            "vectors and the storm track overlaid, across the Ida-like landfall "
            "window (26 Aug — 2 Sep 2021)."
        )
    )
    cells.append(
        code(
            "import matplotlib.pyplot as plt\n"
            "import numpy as np\n"
            "\n"
            "plt.rcParams.update({'figure.dpi': 110, 'font.size': 9})\n"
            "\n"
            "n = ds.sizes['time']\n"
            "panel_days = np.linspace(0, n - 1, 4, dtype=int)\n"
            "panel_days"
        )
    )
    cells.append(
        code(
            "fig, axes = plt.subplots(1, 4, figsize=(13, 3.4), sharey=True)\n"
            "pmin = float(ds['air_pressure_at_mean_sea_level'].min())\n"
            "pmax = float(ds['air_pressure_at_mean_sea_level'].max())\n"
            "step = 3\n"
            "for ax, t in zip(axes, panel_days):\n"
            "    p = ds['air_pressure_at_mean_sea_level'].isel(time=t)\n"
            "    u = ds['eastward_wind'].isel(time=t)\n"
            "    v = ds['northward_wind'].isel(time=t)\n"
            "    pcm = ax.pcolormesh(\n"
            "        p.longitude, p.latitude, p.values, cmap='viridis_r',\n"
            "        vmin=pmin, vmax=pmax, shading='auto',\n"
            "    )\n"
            "    ax.contour(p.longitude, p.latitude, p.values, levels=[980, 990, 1000], colors='white', linewidths=0.5)\n"
            "    ax.quiver(\n"
            "        u.longitude[::step], u.latitude[::step],\n"
            "        u.values[::step, ::step], v.values[::step, ::step],\n"
            "        scale=300, color='k', alpha=0.55, width=0.004,\n"
            "    )\n"
            "    ax.plot(track['LON'], track['LAT'], 'r-', lw=1.0, alpha=0.8)\n"
            "    ax.plot(track['LON'], track['LAT'], 'r.', ms=3)\n"
            "    ax.set_title(str(ds['time'].isel(time=t).values)[:10])\n"
            "    ax.set_xlabel('lon (°E)')\n"
            "axes[0].set_ylabel('lat (°N)')\n"
            "fig.colorbar(pcm, ax=axes, fraction=0.025, pad=0.02, label='MSLP (hPa)')\n"
            "fig.suptitle('CS2 — MSLP + 10 m wind, Ida-like landfall (Aug 26 — Sep 2, 2021)', y=1.03)\n"
            "plt.show()"
        )
    )

    # 5. SST cold-wake panels -------------------------------------------
    cells.append(
        md(
            "## 4. SST cold wake\n"
            "\n"
            "`sea_surface_temperature` harmonised from CMEMS Global L4 SST "
            "(`analysed_sst`), showing the cold wake left by the storm along its track."
        )
    )
    cells.append(
        code(
            "fig, axes = plt.subplots(1, 4, figsize=(13, 3.4), sharey=True)\n"
            "sst = ds['sea_surface_temperature'] - 273.15\n"
            "vmin, vmax = float(sst.min()), float(sst.max())\n"
            "for ax, t in zip(axes, panel_days):\n"
            "    pcm = ax.pcolormesh(\n"
            "        sst.longitude, sst.latitude, sst.isel(time=t).values,\n"
            "        cmap='RdYlBu_r', vmin=vmin, vmax=vmax, shading='auto',\n"
            "    )\n"
            "    ax.plot(track['LON'], track['LAT'], 'k-', lw=0.8, alpha=0.6)\n"
            "    ax.plot(track['LON'], track['LAT'], 'k.', ms=2)\n"
            "    ax.set_title(str(ds['time'].isel(time=t).values)[:10])\n"
            "    ax.set_xlabel('lon (°E)')\n"
            "axes[0].set_ylabel('lat (°N)')\n"
            "fig.colorbar(pcm, ax=axes, fraction=0.025, pad=0.02, label='SST (°C)')\n"
            "fig.suptitle('CS2 — SST with cold wake along the storm track', y=1.03)\n"
            "plt.show()"
        )
    )

    # 6. Hurricane-zone mask snapshots -----------------------------------
    cells.append(
        md(
            "## 5. Hurricane-zone mask\n"
            "\n"
            "`hurricane_zone = (wind_speed > 17 m s⁻¹) & "
            "(air_pressure_at_mean_sea_level < 980 hPa)` — a derived variable "
            "combining the harmonised wind and pressure fields."
        )
    )
    cells.append(
        code(
            "fig, axes = plt.subplots(1, 4, figsize=(13, 3.4), sharey=True)\n"
            "for ax, t in zip(axes, panel_days):\n"
            "    m = ds['hurricane_zone'].isel(time=t).astype('uint8')\n"
            "    ax.pcolormesh(m.longitude, m.latitude, m.values, cmap='Greys', vmin=0, vmax=1, shading='auto')\n"
            "    ax.plot(track['LON'], track['LAT'], 'r-', lw=0.8, alpha=0.7)\n"
            "    ax.plot(track['LON'], track['LAT'], 'r.', ms=2)\n"
            "    ax.set_title(str(ds['time'].isel(time=t).values)[:10])\n"
            "    ax.set_xlabel('lon (°E)')\n"
            "axes[0].set_ylabel('lat (°N)')\n"
            "fig.suptitle('CS2 — hurricane zone (wind > 17 m/s AND MSLP < 980 hPa)', y=1.03)\n"
            "plt.tight_layout()\n"
            "plt.show()\n"
            "\n"
            "print(f\"hurricane-zone cells flagged (full window): \"\n"
            "      f\"{int(ds['hurricane_zone'].astype('uint8').sum().values)}\")"
        )
    )

    # 7. Storm intensity + flagged-cell time series ----------------------
    cells.append(
        md(
            "## 6. Storm intensity and hurricane-zone footprint over time\n"
            "\n"
            "`storm_intensity = 1013.0 - air_pressure_at_mean_sea_level`, plotted "
            "against the daily count of `hurricane_zone` cells."
        )
    )
    cells.append(
        code(
            "intensity_max = ds['storm_intensity'].max(dim=('latitude', 'longitude'))\n"
            "flagged_per_day = ds['hurricane_zone'].astype('uint8').sum(dim=('latitude', 'longitude'))\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(7.5, 4.0))\n"
            "ax.plot(intensity_max.time, intensity_max.values, color='tab:blue',\n"
            "        label='max storm_intensity (hPa)')\n"
            "ax2 = ax.twinx()\n"
            "ax2.bar(flagged_per_day.time, flagged_per_day.values,\n"
            "        color='tab:red', alpha=0.4, width=0.7,\n"
            "        label='flagged cells')\n"
            "ax.set_xlabel('date')\n"
            "ax.set_ylabel('max storm_intensity (hPa)', color='tab:blue')\n"
            "ax2.set_ylabel('flagged cells (count)', color='tab:red')\n"
            "ax.set_title('CS2 — storm intensity and hurricane-zone footprint')\n"
            "fig.autofmt_xdate()\n"
            "plt.show()"
        )
    )

    # 8. Provenance --------------------------------------------------------
    cells.append(
        md(
            "## 7. Provenance — content addressing of the result\n"
            "\n"
            "Every MOSAIC run emits a STAC sidecar that pins the exact pipeline "
            "and the bit-exact output. The hashes below should match across "
            "machines and Python versions when the fixture-based pipeline is used."
        )
    )
    cells.append(
        code(
            "for k in ('mosaic:pipeline_hash', 'mosaic:content_hash'):\n"
            "    print(f'{k:<25} {props[k]}')\n"
            "\n"
            "print()\n"
            "print('inputs:')\n"
            "for inp in props['mosaic:inputs']:\n"
            "    print(f\"  - {inp['source_id']:<10} {inp['plugin']:<14} {inp.get('uri', '')}\")\n"
            "\n"
            "print()\n"
            "print('derived:')\n"
            "for d in props['mosaic:harmonization']['derived']['derived']:\n"
            "    print(f'  + {d}')"
        )
    )
    cells.append(
        md(
            "---\n"
            "*Notebook generated by `notebooks/_build_cs2_notebook.py`. Do not "
            "edit by hand — regenerate from the script to keep the build auditable.*"
        )
    )

    nb.cells = cells
    return nb


def main() -> None:
    nb = build()
    NB_PATH.write_text(nbf.writes(nb), encoding="utf-8")
    print(f"wrote {NB_PATH}")


if __name__ == "__main__":
    main()
