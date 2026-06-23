"""Programmatic builder for ``cs3_arctic_seaice.ipynb``.

This script generates a Jupyter notebook that loads the CS3 pipeline output
(produced by ``mosaic run tests/fixtures/cs3_offline.yaml``) and reproduces
the figures used in the Results section of the CAGEO paper. Mirrors
``_build_cs1_notebook.py``; the plotting recipes are shared with
``_export_cs3_figures.py`` (which renders the same figures headlessly for
the paper itself).

Run from the repository root:

    python notebooks/_build_cs3_notebook.py
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "cs3_arctic_seaice.ipynb"
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
            "case_study": "CS3 — Arctic sea-ice retreat, September 2012",
            "pipeline": "tests/fixtures/cs3_offline.yaml",
            "purpose": "Companion notebook for CAGEO Results section",
        },
    }

    cells: list[nbf.NotebookNode] = []

    # 1. Title + scope ---------------------------------------------------
    cells.append(
        md(
            "# CS3 — Arctic sea-ice retreat, September 2012\n"
            "\n"
            "Companion notebook for the *Computers & Geosciences* paper "
            "*An Open Python Framework for Reproducible Multi-Source Ocean Data "
            "Integration*. It loads the Zarr output produced by the offline "
            "fixture pipeline (`tests/fixtures/cs3_offline.yaml`) and "
            "reproduces the figures used in the Results section.\n"
            "\n"
            "**Reproducibility contract.** Re-running this notebook from a fresh "
            "checkout regenerates the identical content hash printed in the final "
            "section. The pipeline is declarative (YAML) and the data sources are "
            "deterministic Beaufort/Chukchi-shaped fixtures that ship with the "
            "repository, so no external credentials are required.\n"
            "\n"
            "**Scope note.** There is no live NSIDC connector in this codebase yet "
            "— the sea-ice field and its climatology are read through "
            "`LocalNetcdfSource`. `populate-fixtures` is the only fully automated "
            "reproduction path today (see `docs/datasets.md`)."
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
            "PIPELINE = Path('tests/fixtures/cs3_offline.yaml')\n"
            "OUTPUT   = Path('out/cs3_arctic_seaice_offline.zarr')\n"
            "SIDECAR  = OUTPUT.with_suffix(OUTPUT.suffix + '.stac.json')\n"
            "\n"
            "if not OUTPUT.exists():\n"
            "    # Build synthetic fixtures (deterministic) and run the pipeline.\n"
            "    from tests.fixtures.build_cs3_fixtures import build_all\n"
            "    build_all(REPO_ROOT / 'tests' / 'fixtures' / 'cs3')\n"
            "    import mosaic as ms\n"
            "    ms.run(str(PIPELINE))\n"
            "\n"
            "print(f'output: {OUTPUT} ({OUTPUT.exists()})')\n"
            "print(f'sidecar: {SIDECAR} ({SIDECAR.exists()})')"
        )
    )

    # 3. Load --------------------------------------------------------------
    cells.append(md("## 2. Load the integrated dataset and its provenance sidecar"))
    cells.append(
        code(
            "import pandas as pd\n"
            "import xarray as xr\n"
            "\n"
            "ds = xr.open_zarr(OUTPUT, consolidated=True)\n"
            "with open(SIDECAR) as fh:\n"
            "    stac = json.load(fh)\n"
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

    # 4. SIC evolution -------------------------------------------------
    cells.append(
        md(
            "## 3. Sea-ice concentration evolution\n"
            "\n"
            "Four-panel snapshot of `sea_ice_area_fraction` (harmonised from the "
            "NSIDC-like `sic` field) over the Beaufort/Chukchi sector, 1--15 "
            "September 2012, with the 15% and 50% SIC contours overlaid."
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
            "for ax, t in zip(axes, panel_days):\n"
            "    sic = ds['sea_ice_area_fraction'].isel(time=t)\n"
            "    ax.pcolormesh(\n"
            "        sic.longitude, sic.latitude, sic.values,\n"
            "        cmap='Blues_r', vmin=0.0, vmax=1.0, shading='auto',\n"
            "    )\n"
            "    ax.contour(sic.longitude, sic.latitude, sic.values, levels=[0.15, 0.5], colors='k', linewidths=0.6)\n"
            "    ax.set_title(pd.to_datetime(ds['time'].isel(time=t).values).strftime('%Y-%m-%d'))\n"
            "    ax.set_xlabel('lon (°E)')\n"
            "axes[0].set_ylabel('lat (°N)')\n"
            "sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=0.0, vmax=1.0), cmap='Blues_r')\n"
            "fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02, label='SIC (1)')\n"
            "fig.suptitle('CS3 — Arctic sea-ice concentration, Sept 2012', y=1.03)\n"
            "plt.show()"
        )
    )

    # 5. SIC anomaly ----------------------------------------------------
    cells.append(
        md(
            "## 4. SIC anomaly against the long-term climatology\n"
            "\n"
            "`sic_anomaly = sea_ice_area_fraction − "
            "sea_ice_area_fraction_climatology`, against a published "
            "September 1991-2020 climatology. The -0.3 contour highlights the "
            "strongest retreat."
        )
    )
    cells.append(
        code(
            "fig, axes = plt.subplots(1, 4, figsize=(13, 3.4), sharey=True)\n"
            "amax = float(np.nanmax(np.abs(ds['sic_anomaly'].values)))\n"
            "for ax, t in zip(axes, panel_days):\n"
            "    a = ds['sic_anomaly'].isel(time=t)\n"
            "    ax.pcolormesh(\n"
            "        a.longitude, a.latitude, a.values,\n"
            "        cmap='RdBu', vmin=-amax, vmax=amax, shading='auto',\n"
            "    )\n"
            "    ax.contour(a.longitude, a.latitude, a.values, levels=[-0.3], colors='k', linewidths=0.6)\n"
            "    ax.set_title(pd.to_datetime(ds['time'].isel(time=t).values).strftime('%Y-%m-%d'))\n"
            "    ax.set_xlabel('lon (°E)')\n"
            "axes[0].set_ylabel('lat (°N)')\n"
            "sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=-amax, vmax=amax), cmap='RdBu')\n"
            "fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02, label='SIC anomaly (1)')\n"
            "fig.suptitle('CS3 — SIC anomaly (Sept 2012 minus 1991-2020 climatology)', y=1.03)\n"
            "plt.show()"
        )
    )

    # 6. Melt-pond proxy --------------------------------------------------
    cells.append(
        md(
            "## 5. Melt-pond proxy mask\n"
            "\n"
            "`melt_pond_proxy = (sea_ice_area_fraction < 0.5) & "
            "(air_temperature > 273.15 K)` — a derived variable combining low "
            "SIC and above-freezing surface air from ERA5."
        )
    )
    cells.append(
        code(
            "fig, axes = plt.subplots(1, 4, figsize=(13, 3.4), sharey=True)\n"
            "for ax, t in zip(axes, panel_days):\n"
            "    m = ds['melt_pond_proxy'].isel(time=t).astype('uint8')\n"
            "    ax.pcolormesh(m.longitude, m.latitude, m.values, cmap='Greys', vmin=0, vmax=1, shading='auto')\n"
            "    ax.set_title(pd.to_datetime(ds['time'].isel(time=t).values).strftime('%Y-%m-%d'))\n"
            "    ax.set_xlabel('lon (°E)')\n"
            "axes[0].set_ylabel('lat (°N)')\n"
            "fig.suptitle('CS3 — melt-pond proxy (SIC < 0.5 AND t2m > 273.15 K)', y=1.03)\n"
            "plt.tight_layout()\n"
            "plt.show()\n"
            "\n"
            "print(f\"melt-pond proxy cells flagged (full window): \"\n"
            "      f\"{int(ds['melt_pond_proxy'].astype('uint8').sum().values)}\")"
        )
    )

    # 7. Total ice area + flagged-cell time series ------------------------
    cells.append(
        md(
            "## 6. Sectorial ice area and melt-pond footprint over time\n"
            "\n"
            "Total sea-ice area in the domain (in 10⁶ km², accounting for the "
            "latitude-dependent grid-cell area), against the daily count of "
            "`melt_pond_proxy` cells."
        )
    )
    cells.append(
        code(
            "# area per cell ~ d_lat * d_lon * cos(lat) * 111^2 km^2\n"
            "lat = ds['sea_ice_area_fraction'].latitude.values\n"
            "dlon = float(np.diff(ds['sea_ice_area_fraction'].longitude.values).mean())\n"
            "dlat = float(np.diff(lat).mean())\n"
            "cell_area = (dlon * 111.0) * (dlat * 111.0) * np.cos(np.deg2rad(lat))[:, None]\n"
            "sic_area_km2 = (\n"
            "    ds['sea_ice_area_fraction'] * cell_area[None, :, :]\n"
            ").sum(dim=('latitude', 'longitude')).values * 1e-6  # in million km²\n"
            "flagged = ds['melt_pond_proxy'].astype('uint8').sum(dim=('latitude', 'longitude')).values\n"
            "\n"
            "fig, ax1 = plt.subplots(figsize=(7.5, 3.6))\n"
            "ax2 = ax1.twinx()\n"
            "ax1.plot(ds['time'].values, sic_area_km2, color='tab:blue', label='ice area (10⁶ km²)')\n"
            "ax2.bar(ds['time'].values, flagged, color='tab:red', alpha=0.4, width=0.7,\n"
            "        label='melt-pond cells')\n"
            "ax1.set_ylabel('ice area (10⁶ km²)', color='tab:blue')\n"
            "ax2.set_ylabel('melt-pond proxy cells', color='tab:red')\n"
            "ax1.set_xlabel('date')\n"
            "fig.autofmt_xdate()\n"
            "ax1.set_title('CS3 — sectorial ice area and melt-pond proxy footprint')\n"
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
            "*Notebook generated by `notebooks/_build_cs3_notebook.py`. Do not "
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
