# ARM Climatology Dashboard

This is a standalone Streamlit dashboard for the CSV files in:

`AdamTheisen/ARM-Climatologies/results`

This was created using ChatGPT and tested by the PR submitter


## Run it

From a terminal in this folder:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, normally:

```text
http://localhost:8501
```

Open that address in a web browser.

## Why this version

A Jupyter notebook only displays `ipywidgets` after all cells are executed, and
GitHub's notebook preview does not run those widgets. This Streamlit version
launches as a normal browser dashboard and reads the current results directly
from GitHub.


## Data completeness flags

The dashboard assumes one expected sample per minute:

- Monthly expected count = number of calendar days × 1,440
- Yearly expected count = 525,600 for a normal year or 527,040 for a leap year
- A period is flagged when `count / expected_count < 0.90`

The threshold can be changed in the dashboard sidebar.


## Trend and baseline features

- Linear trend slopes are reported in variable units per year.
- The legend and hover text include the slope and R².
- Trend fitting excludes periods below the selected completeness threshold.
- A selectable baseline start/end year can be used to plot anomalies:
  `displayed value = period average - baseline average`.
- The baseline average is calculated independently for each datastream and
  excludes periods below the completeness threshold.


## Multi-variable comparisons

A separate analysis mode now provides:

1. Pearson or Spearman correlation matrix
2. Interactive scatter comparison with optional linear fit
3. Lag-correlation analysis

All analyses join records by timestamp and exclude periods below the selected
completeness threshold before calculating statistics.


## Multiple variables on climatology plots

The single-site climatology mode now supports selecting multiple variables and
variable/datastream combinations for the time-series and seasonal-cycle plots.

Two display scales are available:

- **Raw values** for variables with comparable units
- **Standardized (z-score)** for comparing variables with different units or
  numerical ranges

Seasonal-cycle calculations exclude periods below the selected completeness
threshold. Time-series trend and baseline calculations retain their existing
per-series completeness filtering.


## Site and variable comparison scopes

The climatology plotting interface now provides two selectable workflows:

1. **One variable · multiple sites**
   - Select one variable
   - Select any number of sites
   - Overlay matching site/datastream series

2. **Multiple variables · one site**
   - Select one site
   - Select several variables
   - Use raw values or standardized z-scores

Both workflows are available for time-series and monthly seasonal-cycle plots.
