
from __future__ import annotations

import calendar
import re
from io import StringIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import pearsonr, spearmanr
import requests
import streamlit as st

REPO = "AdamTheisen/ARM-Climatologies"
BRANCH = "main"
RESULTS_DIR = "results"
API_URL = f"https://api.github.com/repos/{REPO}/contents/{RESULTS_DIR}"
FILENAME_RE = re.compile(
    r"^(?P<datastream>.+?)_(?P<variable>.+)_(?P<frequency>MS|YS)\.csv$"
)

st.set_page_config(page_title="ARM Climatology Dashboard", layout="wide")


@st.cache_data(ttl=900)
def discover_results() -> pd.DataFrame:
    response = requests.get(
        API_URL,
        params={"ref": BRANCH},
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )
    response.raise_for_status()

    rows = []
    for item in response.json():
        if item.get("type") != "file":
            continue
        match = FILENAME_RE.match(item["name"])
        if not match:
            continue
        datastream = match.group("datastream")
        rows.append(
            {
                "name": item["name"],
                "datastream": datastream,
                "site": datastream[:3].upper(),
                "variable": match.group("variable"),
                "frequency": match.group("frequency"),
                "url": item["download_url"],
            }
        )

    if not rows:
        raise RuntimeError("No result CSV files were found.")

    return pd.DataFrame(rows).sort_values(
        ["site", "variable", "datastream", "frequency"]
    )


@st.cache_data(ttl=900)
def load_csv(url: str) -> pd.DataFrame:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text))
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    for col in [
        "average", "count", "minimum", "maximum",
        "standard_deviation", "standard_error",
    ]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["time"]).sort_values("time")
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    return df


def pretty(name: str) -> str:
    return name.replace("_", " ").title()


def add_completeness_columns(
    df: pd.DataFrame,
    frequency: str,
    threshold: float = 0.90,
) -> pd.DataFrame:
    """Calculate expected minutely samples and flag incomplete periods."""
    out = df.copy()

    if frequency == "MS":
        # Number of calendar days in each represented month × 1,440 minutes/day.
        out["expected_count"] = (
            out["time"].dt.days_in_month.astype("int64") * 24 * 60
        )
    elif frequency == "YS":
        # Handles leap years automatically.
        out["expected_count"] = np.where(
            out["time"].dt.is_leap_year,
            366 * 24 * 60,
            365 * 24 * 60,
        )
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")

    out["completeness_fraction"] = out["count"] / out["expected_count"]
    out["completeness_percent"] = 100 * out["completeness_fraction"]
    out["below_threshold"] = out["completeness_fraction"] < threshold
    return out


def time_series(
    rows: pd.DataFrame,
    uncertainty: str,
    show_minmax: bool,
    trend: bool,
    completeness_threshold: float,
    show_anomaly: bool,
    baseline_start_year: int,
    baseline_end_year: int,
    scale_mode: str,
):
    fig = go.Figure()

    for _, row in rows.iterrows():
        df = add_completeness_columns(
            load_csv(row["url"]),
            row["frequency"],
            completeness_threshold,
        )
        label = f"{row['site']} · {row['variable']} · {row['datastream']}"

        baseline_mask = (
            df["year"].between(baseline_start_year, baseline_end_year)
            & ~df["below_threshold"]
            & df["average"].notna()
        )
        baseline_average = df.loc[baseline_mask, "average"].mean()

        complete_values = df.loc[
            ~df["below_threshold"] & df["average"].notna(),
            "average",
        ]
        series_mean = complete_values.mean()
        series_std = complete_values.std()

        if show_anomaly:
            if pd.isna(baseline_average):
                st.warning(
                    f"No complete baseline data are available for {label} "
                    f"from {baseline_start_year} through {baseline_end_year}."
                )
                continue
            raw_display = df["average"] - baseline_average
            value_label = "Deviation from baseline"
        else:
            raw_display = df["average"]
            value_label = "Average"

        if scale_mode == "Standardized (z-score)":
            if pd.isna(series_std) or series_std == 0:
                st.warning(f"Cannot standardize {label}: zero or missing variability.")
                continue
            if show_anomaly:
                df["display_value"] = raw_display / series_std
            else:
                df["display_value"] = (raw_display - series_mean) / series_std
            value_label = "Standardized value"
        else:
            df["display_value"] = raw_display

        if (
            scale_mode == "Raw values"
            and uncertainty != "None"
            and uncertainty in df
        ):
            valid = df[["time", "display_value", uncertainty]].dropna()
            if not valid.empty:
                upper = valid["display_value"] + valid[uncertainty]
                lower = valid["display_value"] - valid[uncertainty]
                fig.add_trace(
                    go.Scatter(
                        x=pd.concat([valid["time"], valid["time"].iloc[::-1]]),
                        y=pd.concat([upper, lower.iloc[::-1]]),
                        fill="toself",
                        fillcolor="rgba(100,100,100,0.15)",
                        line=dict(color="rgba(255,255,255,0)"),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

        if (
            scale_mode == "Raw values"
            and show_minmax
            and {"minimum", "maximum"}.issubset(df.columns)
        ):
            min_values = (
                df["minimum"] - baseline_average if show_anomaly else df["minimum"]
            )
            max_values = (
                df["maximum"] - baseline_average if show_anomaly else df["maximum"]
            )
            fig.add_trace(go.Scatter(
                x=df["time"], y=min_values, mode="lines",
                line=dict(width=1, dash="dot"), opacity=0.35,
                name=f"{label} minimum",
            ))
            fig.add_trace(go.Scatter(
                x=df["time"], y=max_values, mode="lines",
                line=dict(width=1, dash="dot"), opacity=0.35,
                name=f"{label} maximum",
            ))

        fig.add_trace(go.Scatter(
            x=df["time"],
            y=df["display_value"],
            mode="lines+markers",
            name=label,
            customdata=np.column_stack([
                df["count"].fillna(0),
                df["expected_count"],
                df["completeness_percent"],
                df.get("standard_deviation", pd.Series(np.nan, index=df.index)),
                np.full(len(df), baseline_average),
            ]),
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>"
                f"{value_label}: %{{y:.3f}}<br>"
                "Count: %{customdata[0]:,.0f}<br>"
                "Expected: %{customdata[1]:,.0f}<br>"
                "Completeness: %{customdata[2]:.1f}%<br>"
                "Std. dev.: %{customdata[3]:.3f}<br>"
                "Baseline average: %{customdata[4]:.3f}<extra>%{fullData.name}</extra>"
            ),
        ))

        flagged = df[df["below_threshold"] & df["display_value"].notna()]
        if not flagged.empty:
            fig.add_trace(go.Scatter(
                x=flagged["time"],
                y=flagged["display_value"],
                mode="markers",
                marker=dict(symbol="x", size=12, line=dict(width=2)),
                name=f"{label} < {completeness_threshold * 100:.0f}% complete",
                customdata=np.column_stack([
                    flagged["count"],
                    flagged["expected_count"],
                    flagged["completeness_percent"],
                ]),
                hovertemplate=(
                    "%{x|%Y-%m-%d}<br>"
                    "FLAGGED: insufficient samples<br>"
                    "Count: %{customdata[0]:,.0f}<br>"
                    "Expected: %{customdata[1]:,.0f}<br>"
                    "Completeness: %{customdata[2]:.1f}%<extra>%{fullData.name}</extra>"
                ),
            ))

        if trend:
            valid = df.loc[
                ~df["below_threshold"],
                ["time", "display_value"],
            ].dropna()
            if len(valid) >= 3:
                x_days = (
                    valid["time"] - valid["time"].min()
                ).dt.total_seconds().to_numpy(dtype=float) / 86400.0
                y_values = valid["display_value"].to_numpy(dtype=float)

                slope_per_day, intercept = np.polyfit(x_days, y_values, 1)
                fitted = slope_per_day * x_days + intercept
                slope_per_year = slope_per_day * 365.2425

                ss_res = np.sum((y_values - fitted) ** 2)
                ss_tot = np.sum((y_values - np.mean(y_values)) ** 2)
                r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

                trend_label = (
                    f"{label} trend: {slope_per_year:+.4g}/yr "
                    f"(R²={r_squared:.2f})"
                )
                fig.add_trace(go.Scatter(
                    x=valid["time"],
                    y=fitted,
                    mode="lines",
                    line=dict(dash="dash"),
                    name=trend_label,
                    hovertemplate=(
                        f"Slope: {slope_per_year:+.6g} per year<br>"
                        f"R²: {r_squared:.3f}<extra>{label}</extra>"
                    ),
                ))

    if show_anomaly:
        fig.add_hline(
            y=0,
            line_dash="dot",
            annotation_text=(
                f"Baseline mean ({baseline_start_year}–{baseline_end_year})"
            ),
            annotation_position="top left",
        )

    fig.update_layout(
        template="plotly_white",
        height=620,
        xaxis_title="Time",
        yaxis_title=(
            "Standardized value (z-score)"
            if scale_mode == "Standardized (z-score)"
            else (
                f"Deviation from {baseline_start_year}–{baseline_end_year} baseline"
                if show_anomaly else "Average"
            )
        ),
        hovermode="x unified",
        legend_title="Datastream",
    )
    return fig


def seasonal_cycle(
    rows: pd.DataFrame,
    completeness_threshold: float,
    scale_mode: str,
):
    fig = go.Figure()
    for _, row in rows.iterrows():
        df = add_completeness_columns(
            load_csv(row["url"]),
            row["frequency"],
            completeness_threshold,
        )
        complete = df.loc[
            ~df["below_threshold"] & df["average"].notna()
        ].copy()

        if complete.empty:
            continue

        if scale_mode == "Standardized (z-score)":
            series_mean = complete["average"].mean()
            series_std = complete["average"].std()
            if pd.isna(series_std) or series_std == 0:
                continue
            complete["plot_value"] = (
                complete["average"] - series_mean
            ) / series_std
            y_label = "Standardized climatological average"
        else:
            complete["plot_value"] = complete["average"]
            y_label = "Climatological average"

        grouped = (
            complete.groupby("month", as_index=False)
            .agg(
                mean=("plot_value", "mean"),
                interannual_std=("plot_value", "std"),
                years=("year", "nunique"),
                periods=("plot_value", "count"),
            )
        )
        grouped["month_name"] = grouped["month"].map(
            lambda x: calendar.month_abbr[x]
        )
        label = f"{row['site']} · {row['variable']} · {row['datastream']}"
        fig.add_trace(go.Scatter(
            x=grouped["month_name"],
            y=grouped["mean"],
            error_y=dict(
                type="data",
                array=grouped["interannual_std"],
                visible=True,
            ),
            mode="lines+markers",
            name=label,
            customdata=grouped[["years", "periods"]],
            hovertemplate=(
                "%{x}<br>Mean: %{y:.3f}<br>"
                "Years: %{customdata[0]}<br>"
                "Complete periods: %{customdata[1]}"
                "<extra>%{fullData.name}</extra>"
            ),
        ))
    fig.update_layout(
        template="plotly_white",
        height=580,
        xaxis_title="Month",
        yaxis_title=y_label if "y_label" in locals() else "Climatological average",
        hovermode="x unified",
        legend_title="Variable · Datastream",
    )
    return fig


def heatmap(row: pd.Series):
    df = load_csv(row["url"])
    pivot = df.pivot(index="year", columns="month", values="average")
    pivot = pivot.reindex(columns=range(1, 13))

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[calendar.month_abbr[m] for m in range(1, 13)],
        y=pivot.index,
        colorbar_title="Average",
        hovertemplate="Year: %{y}<br>Month: %{x}<br>Average: %{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_white",
        height=650,
        xaxis_title="Month",
        yaxis_title="Year",
    )
    return fig


def completeness(row: pd.Series, completeness_threshold: float):
    df = add_completeness_columns(
        load_csv(row["url"]),
        row["frequency"],
        completeness_threshold,
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["time"],
        y=df["completeness_percent"],
        customdata=np.column_stack([
            df["count"],
            df["expected_count"],
            df["below_threshold"],
        ]),
        name="Completeness",
        hovertemplate=(
            "%{x|%Y-%m-%d}<br>"
            "Completeness: %{y:.1f}%<br>"
            "Count: %{customdata[0]:,.0f}<br>"
            "Expected: %{customdata[1]:,.0f}<br>"
            "Flagged: %{customdata[2]}<extra></extra>"
        ),
    ))

    fig.add_hline(
        y=completeness_threshold * 100,
        line_dash="dash",
        annotation_text=f"{completeness_threshold * 100:.0f}% threshold",
        annotation_position="top left",
    )

    flagged = df[df["below_threshold"]]
    if not flagged.empty:
        fig.add_trace(go.Scatter(
            x=flagged["time"],
            y=flagged["completeness_percent"],
            mode="markers",
            marker=dict(symbol="x", size=12, line=dict(width=2)),
            name="Flagged period",
            customdata=np.column_stack([
                flagged["count"],
                flagged["expected_count"],
            ]),
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>"
                "FLAGGED: %{y:.1f}% complete<br>"
                "Count: %{customdata[0]:,.0f}<br>"
                "Expected: %{customdata[1]:,.0f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        template="plotly_white",
        height=500,
        xaxis_title="Time",
        yaxis_title="Completeness (%)",
        yaxis_range=[0, 105],
    )
    return fig



def prepare_multivariable_data(selected_rows, completeness_threshold):
    merged = None
    labels = {}
    for _, row in selected_rows.iterrows():
        df = add_completeness_columns(
            load_csv(row["url"]), row["frequency"], completeness_threshold
        )
        df = df.loc[
            ~df["below_threshold"] & df["average"].notna(),
            ["time", "average"],
        ].copy()
        key = f"v{len(labels)}"
        labels[key] = f"{row['variable']} · {row['datastream']}"
        df = df.rename(columns={"average": key})
        merged = df if merged is None else merged.merge(df, on="time", how="outer")
    return (pd.DataFrame() if merged is None else merged.sort_values("time")), labels


def correlation_matrix_figure(data, labels, method):
    cols = list(labels)
    corr = data[cols].corr(method=method.lower(), min_periods=3)
    names = [labels[c] for c in cols]
    text = np.where(corr.notna(), corr.round(2).astype(str), "")
    fig = go.Figure(go.Heatmap(
        z=corr.to_numpy(), x=names, y=names, zmin=-1, zmax=1,
        colorscale="RdBu", reversescale=True, text=text,
        texttemplate="%{text}", colorbar_title=f"{method} r",
        hovertemplate="%{y}<br>%{x}<br>r=%{z:.3f}<extra></extra>",
    ))
    fig.update_layout(template="plotly_white", height=max(500, 85 * len(cols)))
    return fig


def scatter_comparison_figure(data, labels, x_col, y_col, color_mode, trendline):
    valid = data[["time", x_col, y_col]].dropna().copy()
    valid["month"] = valid["time"].dt.month
    valid["year"] = valid["time"].dt.year
    marker = {"size": 9, "opacity": 0.75}
    if color_mode == "Month":
        marker.update(color=valid["month"], colorscale="Turbo",
                      colorbar={"title": "Month"})
    elif color_mode == "Year":
        marker.update(color=valid["year"], colorscale="Viridis",
                      colorbar={"title": "Year"})

    fig = go.Figure(go.Scatter(
        x=valid[x_col], y=valid[y_col], mode="markers", marker=marker,
        customdata=valid["time"].dt.strftime("%Y-%m-%d"),
        hovertemplate=(
            "Time: %{customdata}<br>"
            f"{labels[x_col]}: %{{x:.4g}}<br>"
            f"{labels[y_col]}: %{{y:.4g}}<extra></extra>"
        ),
        name="Complete overlapping periods",
    ))

    stats = {"n": len(valid), "pearson_r": np.nan, "pearson_p": np.nan,
             "spearman_r": np.nan, "spearman_p": np.nan,
             "slope": np.nan, "r_squared": np.nan}
    if len(valid) >= 2:
        stats["pearson_r"], stats["pearson_p"] = pearsonr(valid[x_col], valid[y_col])
        stats["spearman_r"], stats["spearman_p"] = spearmanr(valid[x_col], valid[y_col])

    if trendline and len(valid) >= 3:
        x = valid[x_col].to_numpy(float)
        y = valid[y_col].to_numpy(float)
        slope, intercept = np.polyfit(x, y, 1)
        fitted = slope * x + intercept
        ss_res = np.sum((y - fitted) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
        stats["slope"], stats["r_squared"] = slope, r2
        order = np.argsort(x)
        fig.add_trace(go.Scatter(
            x=x[order], y=fitted[order], mode="lines",
            line={"dash": "dash"},
            name=f"Fit: slope={slope:+.4g}, R²={r2:.2f}",
        ))

    fig.update_layout(
        template="plotly_white", height=600,
        xaxis_title=labels[x_col], yaxis_title=labels[y_col],
    )
    return fig, stats


def lag_correlation_figure(data, labels, x_col, y_col, max_lag, method):
    rows = []
    for lag in range(-max_lag, max_lag + 1):
        temp = data[[x_col, y_col]].copy()
        temp["y_shifted"] = temp[y_col].shift(-lag)
        valid = temp[[x_col, "y_shifted"]].dropna()
        if len(valid) >= 3:
            if method == "Pearson":
                corr, pval = pearsonr(valid[x_col], valid["y_shifted"])
            else:
                corr, pval = spearmanr(valid[x_col], valid["y_shifted"])
        else:
            corr = pval = np.nan
        rows.append({"lag": lag, "correlation": corr, "p_value": pval, "n": len(valid)})

    result = pd.DataFrame(rows)
    fig = go.Figure(go.Scatter(
        x=result["lag"], y=result["correlation"], mode="lines+markers",
        customdata=np.column_stack([result["p_value"], result["n"]]),
        hovertemplate=(
            "Lag: %{x}<br>Correlation: %{y:.3f}<br>"
            "p-value: %{customdata[0]:.3g}<br>N: %{customdata[1]:.0f}<extra></extra>"
        ),
    ))
    fig.add_hline(y=0, line_dash="dot")
    fig.add_vline(x=0, line_dash="dot")
    if result["correlation"].notna().any():
        best = result.loc[result["correlation"].abs().idxmax()]
        fig.add_trace(go.Scatter(
            x=[best["lag"]], y=[best["correlation"]],
            mode="markers+text", marker={"size": 13, "symbol": "diamond"},
            text=[f"Max |r|: lag {int(best['lag'])}"], textposition="top center",
            name="Strongest lag",
        ))
    fig.update_layout(
        template="plotly_white", height=550, yaxis_range=[-1.05, 1.05],
        xaxis_title=(
            f"Lag in displayed periods "
            f"(positive = {labels[y_col]} follows {labels[x_col]})"
        ),
        yaxis_title=f"{method} correlation",
    )
    return fig, result

st.title("ARM Climatology Dashboard")

try:
    catalog = discover_results()
except Exception as exc:
    st.error(f"Could not read the GitHub results directory: {exc}")
    st.stop()

analysis_mode = st.radio(
    "Analysis mode",
    ["Single-variable climatology", "Multi-variable comparisons"],
    horizontal=True,
)

if analysis_mode == "Multi-variable comparisons":
    st.caption(
        "All analyses use only overlapping periods where every variable "
        "meets the minimum completeness threshold."
    )

    frequency = st.sidebar.selectbox(
        "Comparison frequency", sorted(catalog["frequency"].unique()),
        key="mv_frequency",
    )
    subset = catalog[catalog["frequency"] == frequency].copy()
    site = st.sidebar.selectbox(
        "Comparison site", sorted(subset["site"].unique()), key="mv_site"
    )
    subset = subset[subset["site"] == site].copy()
    threshold_pct = st.sidebar.number_input(
        "Minimum completeness (%)", 0.0, 100.0, 90.0, 1.0, key="mv_threshold"
    )
    threshold = threshold_pct / 100.0
    subset["display_name"] = subset["variable"] + " · " + subset["datastream"]
    options = subset["display_name"].tolist()
    selected = st.sidebar.multiselect(
        "Variables", options, default=options[:min(4, len(options))],
        key="mv_variables",
    )
    if len(selected) < 2:
        st.info("Select at least two variables.")
        st.stop()

    rows = subset[subset["display_name"].isin(selected)].copy()
    mv_data, mv_labels = prepare_multivariable_data(rows, threshold)
    if mv_data.empty:
        st.warning("No data are available for this comparison.")
        st.stop()

    tab1, tab2, tab3 = st.tabs([
        "Correlation matrix", "Scatter comparison", "Lag correlation"
    ])

    with tab1:
        method = st.radio(
            "Correlation method", ["Pearson", "Spearman"],
            horizontal=True, key="matrix_method"
        )
        st.plotly_chart(
            correlation_matrix_figure(mv_data, mv_labels, method),
            use_container_width=True,
        )
        overlap = mv_data[list(mv_labels)].notna().astype(int).T.dot(
            mv_data[list(mv_labels)].notna().astype(int)
        )
        overlap.index = [mv_labels[c] for c in overlap.index]
        overlap.columns = [mv_labels[c] for c in overlap.columns]
        with st.expander("Overlapping sample counts"):
            st.dataframe(overlap, use_container_width=True)

    with tab2:
        c1, c2, c3 = st.columns(3)
        x_col = c1.selectbox(
            "X variable", list(mv_labels),
            format_func=lambda c: mv_labels[c], key="scatter_x"
        )
        y_col = c2.selectbox(
            "Y variable", [c for c in mv_labels if c != x_col],
            format_func=lambda c: mv_labels[c], key="scatter_y"
        )
        color_mode = c3.selectbox(
            "Color by", ["None", "Month", "Year"], key="scatter_color"
        )
        show_fit = st.checkbox("Show linear fit", True, key="scatter_fit")
        fig, stats = scatter_comparison_figure(
            mv_data, mv_labels, x_col, y_col, color_mode, show_fit
        )
        st.plotly_chart(fig, use_container_width=True)
        a, b, c, d = st.columns(4)
        a.metric("Overlapping periods", f"{stats['n']:,}")
        b.metric("Pearson r", f"{stats['pearson_r']:.3f}")
        c.metric("Spearman ρ", f"{stats['spearman_r']:.3f}")
        d.metric(
            "Fit R²",
            "—" if pd.isna(stats["r_squared"]) else f"{stats['r_squared']:.3f}"
        )
        st.caption(
            f"Pearson p={stats['pearson_p']:.3g}; "
            f"Spearman p={stats['spearman_p']:.3g}."
        )

    with tab3:
        c1, c2, c3 = st.columns(3)
        lead = c1.selectbox(
            "Leading variable", list(mv_labels),
            format_func=lambda c: mv_labels[c], key="lag_x"
        )
        follow = c2.selectbox(
            "Following variable", [c for c in mv_labels if c != lead],
            format_func=lambda c: mv_labels[c], key="lag_y"
        )
        method = c3.selectbox(
            "Correlation method", ["Pearson", "Spearman"], key="lag_method"
        )
        maximum = 24 if frequency == "MS" else 10
        default = 12 if frequency == "MS" else 5
        max_lag = st.slider("Maximum lag", 1, maximum, default)
        fig, lag_table = lag_correlation_figure(
            mv_data, mv_labels, lead, follow, max_lag, method
        )
        st.plotly_chart(fig, use_container_width=True)
        if lag_table["correlation"].notna().any():
            best = lag_table.loc[lag_table["correlation"].abs().idxmax()]
            st.info(
                f"Strongest absolute correlation: lag {int(best['lag'])}, "
                f"r={best['correlation']:.3f}, p={best['p_value']:.3g}, "
                f"N={int(best['n'])}. Positive lag means "
                f"{mv_labels[follow]} follows {mv_labels[lead]}."
            )
        with st.expander("Lag statistics"):
            st.dataframe(lag_table, use_container_width=True, hide_index=True)

    st.stop()

st.caption("Interactive exploration of the CSV results in AdamTheisen/ARM-Climatologies.")

all_years = []
for url in catalog["url"].unique():
    try:
        data_years = load_csv(url)["year"].dropna().astype(int).tolist()
        all_years.extend(data_years)
    except Exception:
        continue

if all_years:
    minimum_available_year = int(min(all_years))
    maximum_available_year = int(max(all_years))
else:
    minimum_available_year = 1990
    maximum_available_year = pd.Timestamp.now().year

with st.sidebar:
    st.header("Selections")

    comparison_scope = st.radio(
        "Comparison scope",
        [
            "One variable · multiple sites",
            "Multiple variables · one site",
        ],
        help=(
            "Compare one measurement across sites, or compare several "
            "measurements at a single site."
        ),
    )
    frequency = st.radio("Frequency", ["MS", "YS"], horizontal=True)

    frequency_catalog = catalog[
        catalog["frequency"] == frequency
    ].copy()

    if comparison_scope == "One variable · multiple sites":
        available_variables = sorted(
            frequency_catalog["variable"].unique().tolist()
        )
        selected_variable = st.selectbox(
            "Variable",
            available_variables,
        )

        variable_catalog = frequency_catalog[
            frequency_catalog["variable"] == selected_variable
        ].copy()
        available_sites = sorted(
            variable_catalog["site"].unique().tolist()
        )
        selected_sites = st.multiselect(
            "Sites",
            available_sites,
            default=available_sites,
            help=(
                "Each selected site can contribute one or more matching "
                "datastreams."
            ),
        )
        subset = variable_catalog[
            variable_catalog["site"].isin(selected_sites)
        ].copy()

        subset["selection_label"] = (
            subset["site"] + " · " + subset["datastream"]
        )
        available_series = sorted(
            subset["selection_label"].unique().tolist()
        )
        selected_series = st.multiselect(
            "Site · datastream series",
            available_series,
            default=available_series,
        )
        scale_mode = "Raw values"
        site = "Multiple sites"

    else:
        site = st.selectbox(
            "Site",
            sorted(frequency_catalog["site"].unique().tolist()),
        )
        subset = frequency_catalog[
            frequency_catalog["site"] == site
        ].copy()

        available_variables = sorted(
            subset["variable"].unique().tolist()
        )
        selected_variables = st.multiselect(
            "Variables",
            available_variables,
            default=available_variables[: min(3, len(available_variables))],
            help=(
                "Selected variables can be overlaid on the time-series and "
                "seasonal-cycle plots."
            ),
        )
        subset = subset[
            subset["variable"].isin(selected_variables)
        ].copy()

        subset["selection_label"] = (
            subset["variable"] + " · " + subset["datastream"]
        )
        available_series = sorted(
            subset["selection_label"].unique().tolist()
        )
        selected_series = st.multiselect(
            "Variable · datastream series",
            available_series,
            default=available_series,
        )

        scale_mode = st.radio(
            "Multi-variable scale",
            ["Raw values", "Standardized (z-score)"],
            help=(
                "Use standardized values when selected variables have "
                "different units or numerical ranges."
            ),
        )

    view_options = ["Time series", "Summary"]
    if frequency == "MS":
        view_options[1:1] = ["Seasonal cycle", "Year–month heatmap"]
    view_options.insert(-1, "Completeness")
    view = st.radio("View", view_options)

    completeness_threshold_pct = st.number_input(
        "Minimum completeness (%)",
        min_value=0.0,
        max_value=100.0,
        value=90.0,
        step=1.0,
        help=(
            "Periods with fewer than this percentage of the expected "
            "one-minute samples are flagged."
        ),
    )
    completeness_threshold = completeness_threshold_pct / 100.0

    uncertainty = st.selectbox(
        "Uncertainty envelope",
        ["standard_error", "standard_deviation", "None"],
    )
    show_minmax = st.checkbox("Show minimum and maximum")
    trend = st.checkbox("Show linear trend")

    if scale_mode == "Standardized (z-score)":
        st.caption(
            "Uncertainty and minimum/maximum envelopes are hidden in "
            "standardized mode."
        )

    st.subheader("Baseline deviation")
    show_anomaly = st.checkbox(
        "Plot deviation from baseline",
        help=(
            "Subtracts the mean of complete periods within the selected "
            "baseline years from each displayed monthly or yearly average."
        ),
    )
    baseline_start_year, baseline_end_year = st.slider(
        "Baseline years",
        min_value=minimum_available_year,
        max_value=maximum_available_year,
        value=(
            max(minimum_available_year, maximum_available_year - 29),
            maximum_available_year,
        ),
    )

rows = subset[subset["selection_label"].isin(selected_series)]

if rows.empty:
    st.info("Select at least one site/variable and datastream series.")
    st.stop()

selected_variable_names = sorted(
    rows["variable"].unique().tolist()
)
heading_variables = ", ".join(
    pretty(v) for v in selected_variable_names
)

if comparison_scope == "One variable · multiple sites":
    selected_site_names = ", ".join(
        sorted(rows["site"].unique().tolist())
    )
    st.subheader(
        f"{heading_variables} · {selected_site_names} · {frequency}"
    )
else:
    st.subheader(
        f"{site} · {heading_variables} · {frequency}"
    )

if view == "Time series":
    st.plotly_chart(
        time_series(
            rows,
            uncertainty,
            show_minmax,
            trend,
            completeness_threshold,
            show_anomaly,
            baseline_start_year,
            baseline_end_year,
            scale_mode,
        ),
        use_container_width=True,
    )

    if show_anomaly:
        baseline_rows = []
        for _, row in rows.iterrows():
            baseline_df = add_completeness_columns(
                load_csv(row["url"]),
                row["frequency"],
                completeness_threshold,
            )
            baseline_valid = baseline_df[
                baseline_df["year"].between(
                    baseline_start_year,
                    baseline_end_year,
                )
                & ~baseline_df["below_threshold"]
                & baseline_df["average"].notna()
            ]
            baseline_rows.append({
                "site": row["site"],
                "datastream": row["datastream"],
                "baseline_start": baseline_start_year,
                "baseline_end": baseline_end_year,
                "baseline_average": baseline_valid["average"].mean(),
                "periods_used": len(baseline_valid),
            })

        st.dataframe(
            pd.DataFrame(baseline_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "baseline_average": st.column_config.NumberColumn(
                    "Baseline average",
                    format="%.4f",
                ),
            },
        )

elif view == "Seasonal cycle":
    st.plotly_chart(
        seasonal_cycle(
            rows,
            completeness_threshold,
            scale_mode,
        ),
        use_container_width=True,
    )

elif view == "Year–month heatmap":
    chosen = rows.iloc[0]
    st.caption(
        "The heatmap uses the first selected variable · datastream series."
    )
    st.plotly_chart(heatmap(chosen), use_container_width=True)

elif view == "Completeness":
    chosen = rows.iloc[0]
    st.caption(
        "Expected counts assume one sample per minute: 1,440 samples per day. "
        "Calendar month length and leap years are handled automatically."
    )
    st.plotly_chart(
        completeness(chosen, completeness_threshold),
        use_container_width=True,
    )

else:
    summary_rows = []
    for _, row in rows.iterrows():
        df = add_completeness_columns(
            load_csv(row["url"]),
            row["frequency"],
            completeness_threshold,
        )
        valid = df.dropna(subset=["average"])
        summary_rows.append({
            "site": row["site"],
            "datastream": row["datastream"],
            "variable": row["variable"],
            "frequency": row["frequency"],
            "start": df["time"].min().date(),
            "end": df["time"].max().date(),
            "periods": len(df),
            "valid_periods": len(valid),
            "missing_periods": int(df["average"].isna().sum()),
            "mean_of_averages": valid["average"].mean(),
            "minimum_average": valid["average"].min(),
            "maximum_average": valid["average"].max(),
            "total_samples": df["count"].fillna(0).sum(),
            "flagged_periods": int(df["below_threshold"].sum()),
            "minimum_completeness_percent": df["completeness_percent"].min(),
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

st.divider()
st.subheader("Completeness flags")

flagged_tables = []
for _, row in rows.iterrows():
    df = add_completeness_columns(
        load_csv(row["url"]),
        row["frequency"],
        completeness_threshold,
    )
    flagged = df[df["below_threshold"]].copy()
    if flagged.empty:
        continue
    flagged["site"] = row["site"]
    flagged["datastream"] = row["datastream"]
    flagged["variable"] = row["variable"]
    flagged["frequency"] = row["frequency"]
    flagged_tables.append(
        flagged[
            [
                "site", "datastream", "variable", "frequency", "time",
                "count", "expected_count", "completeness_percent",
            ]
        ]
    )

if flagged_tables:
    flagged_df = pd.concat(flagged_tables, ignore_index=True)
    flagged_df["time"] = flagged_df["time"].dt.date
    st.warning(
        f"{len(flagged_df)} displayed period(s) contain fewer than "
        f"{completeness_threshold_pct:.0f}% of expected minutely samples."
    )
    st.dataframe(
        flagged_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "completeness_percent": st.column_config.NumberColumn(
                "Completeness (%)",
                format="%.1f",
            ),
            "count": st.column_config.NumberColumn("Count", format="%d"),
            "expected_count": st.column_config.NumberColumn(
                "Expected count",
                format="%d",
            ),
        },
    )
else:
    st.success(
        f"All displayed periods meet the {completeness_threshold_pct:.0f}% "
        "sample-completeness threshold."
    )

with st.expander("About the dashboard"):
    st.markdown(
        """
        The dashboard discovers result files directly from the repository, so newly
        committed `MS` and `YS` CSV files appear automatically. Expected sample counts
        assume one observation per minute and use the actual number of calendar days in
        each month or year, including leap years. Trend slopes are reported per year
        and are fitted only to periods that pass the completeness threshold. Baseline
        deviations subtract the mean of complete periods between the selected start and
        end years. Units are not currently encoded in the result files, so the vertical
        axis is labeled generically.
        """
    )
