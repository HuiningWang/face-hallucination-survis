# Face Super-Resolution and Blind Face Restoration

SurVis companion repository for a COMP4126 Coursework 3 literature review on face super-resolution and blind face restoration.

## Repository Contents

- `src/`: the SurVis web app
- `src/data/generated/`: generated data consumed by the site
- `bib/references.bib`: the bibliography used to build the visualization
- `update_data.py`: the local script for regenerating SurVis data files

## Local Preview

From this folder:

```powershell
python update_data.py --once
python -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

The root page redirects to `src/index.html`, so the same setup works for local preview and future GitHub Pages deployment.

Or you can directly visit https://huiningwang.github.io/face-hallucination-survis/
