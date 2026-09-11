# Notebooks

Jupyter notebooks, talks and hands-on material by Manuel Behrendt.

## MERA documentation notebooks

[Mera.jl](https://github.com/ManuelBehrendt/Mera.jl) is a Julia package for analysing AMR and
particle data from astrophysical simulations.

### → [Mera-Docs/version_1.1](https://github.com/ManuelBehrendt/Notebooks/tree/master/Mera-Docs/version_1.1)

**These notebooks are the source of the documentation.** Every generated page on the
[Mera documentation site](https://manuelbehrendt.github.io/Mera.jl/stable/) is produced from the
notebook of the same name, so the notebook is the thing to read, edit and run. Each of these is
stored with its outputs, so you can read one on GitHub without running anything.

They work through first inspection of a simulation, loading and selecting data, subregions,
calculations and derived fields, masking and filtering, projections including off-axis, profiles and
phase diagrams, radiative transfer, cosmology, star formation, clump finding, provenance and
reproducibility, covering hydro, particles, gravity, clumps, sinks and RT data.

To run one against your own simulation, change the path and the output number at the top. To run it
against data you can download, use Mera's `download_testdata()`.

Inside that folder:

| | |
|---|---|
| [`gallery/`](https://github.com/ManuelBehrendt/Notebooks/tree/master/Mera-Docs/version_1.1/gallery) | complete workflows, each in its own numbered folder with the environment it ran in, so a result can be reproduced rather than just described. Contributions welcome: see the folder's README and `TEMPLATE/`. |
| [`examples/`](https://github.com/ManuelBehrendt/Notebooks/tree/master/Mera-Docs/version_1.1/examples) | exporting and importing data, and loading from existing outputs |
| [`paraview/`](https://github.com/ManuelBehrendt/Notebooks/tree/master/Mera-Docs/version_1.1/paraview) | taking Mera output into ParaView for 3D rendering |

## Talks and hands-on sessions

* [RAMSES 2023 MERA hands-on session in Oxford](https://github.com/ManuelBehrendt/RUM2023)
* [RAMSES 2023 MERA presentation in Oxford](https://github.com/ManuelBehrendt/Notebooks/blob/master/RUM2023/RUM2023.pdf)
* [USM/LMU Code-Coffee 06/02/2020, Munich: Tmux, terminal multiplexer](https://github.com/ManuelBehrendt/Notebooks/tree/master/USMCodeCoffee/2020_06_02-Tmux)
* [CAST group retreat 01/10/2019, Prien am Chiemsee: MERA status update](https://github.com/ManuelBehrendt/Notebooks/blob/master/CAST_Retreat2019/MERA_Status_CASTretreat2019.pdf)
* [USM/LMU Code-Coffee 12/02/2019, Munich: Julia, a fresh approach to scientific computing](https://github.com/ManuelBehrendt/Notebooks/blob/master/USMCodeCoffee/2019_02_12-Julia.pdf)
* [RAMSES Hackathon 2018, Lyon: MERA preview, post processing in Julia](https://github.com/ManuelBehrendt/Notebooks/blob/master/RUM2018/RUM2018_presentation.ipynb)
