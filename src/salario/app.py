"""Salary Analysis — kode24 2025."""

import json
import tomllib
from pathlib import Path
from typing import Any

import pandas as pd
import panel as pn
import plotly.graph_objects as go

from salario.config import (
    TABULATOR_FORMATTERS,
    TABULATOR_HEADER_FILTERS,
    TABULATOR_TITLES,
)
from salario.data import ensure_data

_PKG = Path(__file__).resolve().parent
CONFIG_PATH = Path.cwd() / "config.toml"
HELP_PATH = _PKG / "help.md"

pn.extension("tabulator", "plotly", template="fast")

_LONN_MIN = 100_000
_LONN_MAX = 5_000_000
_UTD_MAX = 20  # cap obviously erroneous values (max in data is 45781)
_PLOT_MAX_WIDTH = 1200
_ALL = "All"

_TABLE_COLS = [
    "fag",
    "arbeidssted",
    "jobbtype",
    "kjønn",
    "års utdanning",
    "års erfaring",
    "lønn",
    "inkludert bonus?",
    "inkludert provisjon?",
]

_GRID = dict(showgrid=True, gridcolor="rgba(0,0,0,0.10)", gridwidth=1)


@pn.cache
def _load_data() -> pd.DataFrame:
    data_path = ensure_data()
    records = json.loads(data_path.read_text())
    df = pd.DataFrame(records)
    df = df[
        (df["lønn"] >= _LONN_MIN)
        & (df["lønn"] <= _LONN_MAX)
        & (df["års utdanning"] <= _UTD_MAX)
        & (df["års erfaring"] >= 0)
    ].copy()
    return df[_TABLE_COLS].reset_index(drop=True)


def _load_profile() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("rb") as f:
            return tomllib.load(f)
    return {}


def _load_help() -> str:
    if HELP_PATH.exists():
        return HELP_PATH.read_text()
    return "_help.md not found._"


def _apply_filters(
    df: pd.DataFrame,
    location: str,
    job_type: str,
    utd_range: tuple[int, int],
    exp_range: tuple[int, int],
) -> pd.DataFrame:
    mask = df["års utdanning"].between(int(utd_range[0]), int(utd_range[1])) & df[
        "års erfaring"
    ].between(int(exp_range[0]), int(exp_range[1]))
    if location != _ALL:
        mask &= df["arbeidssted"] == location
    if job_type != _ALL:
        mask &= df["jobbtype"] == job_type
    return df[mask].sort_values("lønn", ascending=False).reset_index(drop=True)


def _histogram(df: pd.DataFrame, my_salary: int) -> go.Figure:
    fig = go.Figure()

    if not df.empty:
        data_range = df["lønn"].max() - df["lønn"].min()
        raw_bin = data_range / 30
        bin_size = max(50_000, round(raw_bin / 50_000) * 50_000)

        fig.add_trace(
            go.Histogram(
                x=df["lønn"],
                xbins=dict(size=bin_size),
                marker_color="steelblue",
                opacity=0.8,
                name="Salary",
                hovertemplate="Salary: %{x:,.0f} NOK<br>Count: %{y}<extra></extra>",
            )
        )

    fig.add_vline(
        x=my_salary,
        line_dash="dash",
        line_color="crimson",
        line_width=2,
        annotation_text=f"Your salary: {my_salary / 1_000:.0f}k",
        annotation_position="top right",
        annotation_font_color="crimson",
    )

    fig.update_layout(
        xaxis_title="Salary (NOK)",
        yaxis_title="Count",
        template="simple_white",
        height=360,
        bargap=0.05,
        margin=dict(t=50, b=50, l=60, r=20),
    )
    fig.update_xaxes(tickformat="~s", **_GRID)
    fig.update_yaxes(**_GRID)
    return fig


def _box_chart(
    df: pd.DataFrame,
    group_col: str,
    height_per_row: int,
    my_salary: int = 0,
) -> go.Figure:
    if df.empty:
        return go.Figure(
            layout=go.Layout(
                template="simple_white",
                height=320,
                annotations=[
                    dict(
                        text="No data",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(size=16),
                    )
                ],
            )
        )

    stats = (
        df.groupby(group_col)
        .agg(
            median=pd.NamedAgg(column="lønn", aggfunc="median"),
            q25=pd.NamedAgg(column="lønn", aggfunc=lambda x: x.quantile(0.25)),
            q75=pd.NamedAgg(column="lønn", aggfunc=lambda x: x.quantile(0.75)),
            min_val=pd.NamedAgg(column="lønn", aggfunc="min"),
            max_val=pd.NamedAgg(column="lønn", aggfunc="max"),
            count=pd.NamedAgg(column="lønn", aggfunc="count"),
        )
        .sort_values("median")
    )

    y_labels = [f"{g} ({int(stats.loc[g, 'count'])})" for g in stats.index]

    fig = go.Figure()

    fig.add_trace(
        go.Box(
            y=y_labels,
            q1=stats["q25"].values,
            median=stats["median"].values,
            q3=stats["q75"].values,
            lowerfence=stats["min_val"].values,
            upperfence=stats["max_val"].values,
            orientation="h",
            boxpoints=False,
            fillcolor="rgba(70,130,180,0.55)",
            line=dict(color="navy", width=1.5),
            marker=dict(color="navy"),
            name="",
            showlegend=False,
        )
    )

    # Median text labels
    fig.add_trace(
        go.Scatter(
            y=y_labels,
            x=stats["median"].values,
            mode="text",
            text=[f" {v / 1_000:.0f}k" for v in stats["median"]],
            textposition="middle right",
            textfont=dict(size=10, color="navy"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    if my_salary:
        fig.add_vline(
            x=my_salary,
            line_dash="dash",
            line_color="crimson",
            line_width=2,
            annotation_text=f"Your salary: {my_salary / 1_000:.0f}k",
            annotation_position="top right",
            annotation_font_color="crimson",
        )

    fig.update_layout(
        xaxis_title="Salary (NOK)",
        template="simple_white",
        height=max(320, len(stats) * height_per_row + 120),
        showlegend=False,
        margin=dict(t=50, b=50, l=20, r=100),
    )
    fig.update_xaxes(tickformat="~s", **_GRID)
    fig.update_yaxes(automargin=True, **_GRID)
    return fig


def _fag_chart(df: pd.DataFrame, my_salary: int = 0) -> go.Figure:
    return _box_chart(df, "fag", 34, my_salary)


def _jobbtype_chart(df: pd.DataFrame, my_salary: int = 0) -> go.Figure:
    return _box_chart(df, "jobbtype", 60, my_salary)


def _scatter(df: pd.DataFrame, my_salary: int = 0, my_exp: int = 0) -> go.Figure:
    fig = go.Figure()

    if not df.empty:
        job_types = sorted(df["jobbtype"].dropna().unique())
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        color_map = {jt: colors[i % len(colors)] for i, jt in enumerate(job_types)}

        for jt in job_types:
            sub = df[df["jobbtype"] == jt]
            fig.add_trace(
                go.Scatter(
                    x=sub["års erfaring"],
                    y=sub["lønn"],
                    mode="markers",
                    name=jt,
                    marker=dict(color=color_map[jt], size=6, opacity=0.7),
                    hovertemplate=(
                        f"<b>{jt}</b><br>"
                        "Experience: %{x} yrs<br>"
                        "Salary: %{y:,.0f} NOK<extra></extra>"
                    ),
                )
            )

    if my_salary:
        fig.add_hline(
            y=my_salary,
            line_dash="dash",
            line_color="crimson",
            line_width=2,
            annotation_text=f"Your salary: {my_salary / 1_000:.0f}k",
            annotation_position="right",
            annotation_font_color="crimson",
        )

    if my_exp:
        fig.add_vline(
            x=my_exp,
            line_dash="dash",
            line_color="crimson",
            line_width=2,
            annotation_text=f"Your exp: {my_exp} yrs",
            annotation_position="top left",
            annotation_font_color="crimson",
        )

    fig.update_layout(
        xaxis_title="Experience (yrs)",
        yaxis_title="Salary (NOK)",
        template="simple_white",
        height=420,
        margin=dict(t=50, b=50, l=60, r=120),
        legend=dict(
            orientation="v",
            x=1.02,
            y=1,
            xanchor="left",
        ),
    )
    fig.update_xaxes(**_GRID)
    fig.update_yaxes(tickformat="~s", **_GRID)
    return fig


class SalarioApp(pn.viewable.Viewer):
    """Panel app for analysing kode24 2025 salary data."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        df = _load_data()
        self._df = df
        profile = _load_profile()

        location_opts = [_ALL, *sorted(df["arbeidssted"].dropna().unique().tolist())]
        job_type_opts = [_ALL, *sorted(df["jobbtype"].dropna().unique().tolist())]
        locations = sorted(df["arbeidssted"].dropna().unique().tolist())
        job_types = sorted(df["jobbtype"].dropna().unique().tolist())

        utd_max = int(df["års utdanning"].max())
        exp_max = int(df["års erfaring"].max())

        # --- Filter widgets ---
        self.location_sel = pn.widgets.Select(
            name="Location", options=location_opts, value=_ALL, width=270
        )
        self.job_type_sel = pn.widgets.Select(
            name="Job Type", options=job_type_opts, value=_ALL, width=270
        )
        self.utd_slider = pn.widgets.RangeSlider(
            name="Education (yrs)",
            start=0,
            end=utd_max,
            value=(0, utd_max),
            step=1,
            width=270,
        )
        self.exp_slider = pn.widgets.RangeSlider(
            name="Experience (yrs)",
            start=0,
            end=exp_max,
            value=(0, exp_max),
            step=1,
            width=270,
        )

        # --- My profile widgets — seeded from config.toml ---
        def _pick(opts: list, key: str, fallback: str) -> str:
            v = profile.get(key, fallback)
            return v if v in opts else (opts[0] if opts else fallback)

        self.my_salary = pn.widgets.IntInput(
            name="Salary (NOK)",
            value=int(profile.get("salary", 700_000)),
            step=50_000,
            width=230,
        )
        self.my_utd = pn.widgets.IntInput(
            name="Education (yrs)",
            value=int(profile.get("education_yrs", 5)),
            start=0,
            end=_UTD_MAX,
            width=230,
        )
        self.my_exp = pn.widgets.IntInput(
            name="Experience (yrs)",
            value=int(profile.get("experience_yrs", 5)),
            start=0,
            end=exp_max,
            width=230,
        )
        self.my_location = pn.widgets.Select(
            name="Location",
            options=locations,
            value=_pick(locations, "location", "Oslo"),
            width=230,
        )
        self.my_job_type = pn.widgets.Select(
            name="Job Type",
            options=job_types,
            value=_pick(job_types, "job_type", job_types[0]),
            width=230,
        )

        # --- Count indicator ---
        self.count_md = pn.pane.Markdown(f"**{len(df)} entries**")

        # --- Tabulator (sorted descending by salary) ---
        initial_table = df.sort_values("lønn", ascending=False).reset_index(drop=True)
        self.table = pn.widgets.Tabulator(
            initial_table,
            pagination="remote",
            page_size=20,
            sizing_mode="stretch_width",
            show_index=False,
            height=750,
            formatters=TABULATOR_FORMATTERS,
            titles=TABULATOR_TITLES,
            header_filters=TABULATOR_HEADER_FILTERS,
        )

        # --- Plot panes ---
        self.hist_pane = pn.pane.Plotly(
            _histogram(df, self.my_salary.value),
            sizing_mode="stretch_width",
            max_width=_PLOT_MAX_WIDTH,
        )
        self.fag_pane = pn.pane.Plotly(
            _fag_chart(df, self.my_salary.value),
            sizing_mode="stretch_width",
            max_width=_PLOT_MAX_WIDTH,
        )
        self.jobbtype_pane = pn.pane.Plotly(
            _jobbtype_chart(df, self.my_salary.value),
            sizing_mode="stretch_width",
            max_width=_PLOT_MAX_WIDTH,
        )
        self.scatter_pane = pn.pane.Plotly(
            _scatter(df, self.my_salary.value, self.my_exp.value),
            sizing_mode="stretch_width",
            max_width=_PLOT_MAX_WIDTH,
        )

        # --- Wire up reactivity ---
        for w in (
            self.location_sel,
            self.job_type_sel,
            self.utd_slider,
            self.exp_slider,
        ):
            w.param.watch(self._on_filter_change, "value")
        for w in (self.my_salary, self.my_exp):
            w.param.watch(self._on_profile_change, "value")

    def _filtered(self) -> pd.DataFrame:
        return _apply_filters(
            self._df,
            self.location_sel.value,
            self.job_type_sel.value,
            self.utd_slider.value,
            self.exp_slider.value,
        )

    def _on_filter_change(self, event: Any = None) -> None:  # noqa: ARG002
        filtered = self._filtered()
        self.count_md.object = f"**{len(filtered)} entries**"
        self.table.value = filtered
        self.hist_pane.object = _histogram(filtered, self.my_salary.value)
        self.fag_pane.object = _fag_chart(filtered, self.my_salary.value)
        self.jobbtype_pane.object = _jobbtype_chart(filtered, self.my_salary.value)
        self.scatter_pane.object = _scatter(filtered, self.my_salary.value, self.my_exp.value)

    def _on_profile_change(self, event: Any = None) -> None:  # noqa: ARG002
        filtered = self._filtered()
        self.hist_pane.object = _histogram(filtered, self.my_salary.value)
        self.fag_pane.object = _fag_chart(filtered, self.my_salary.value)
        self.jobbtype_pane.object = _jobbtype_chart(filtered, self.my_salary.value)
        self.scatter_pane.object = _scatter(filtered, self.my_salary.value, self.my_exp.value)

    def __panel__(self) -> pn.viewable.Viewable:
        filter_box = pn.WidgetBox(
            pn.pane.Markdown("### Filters", margin=(5, 10)),
            self.location_sel,
            self.job_type_sel,
            self.utd_slider,
            self.exp_slider,
            width=310,
        )

        my_box = pn.WidgetBox(
            pn.pane.Markdown("### My Profile", margin=(5, 10)),
            self.my_salary,
            self.my_utd,
            self.my_exp,
            self.my_location,
            self.my_job_type,
            width=310,
        )

        sidebar = pn.Column(filter_box, my_box, width=320)

        _card_kw = dict(
            collapsible=True,
            collapsed=False,
            max_width=_PLOT_MAX_WIDTH,
            align="center",
            margin=(10, 0),
        )
        hist_card = pn.Card(self.hist_pane, title="Salary Distribution", **_card_kw)
        fag_card = pn.Card(self.fag_pane, title="Salary by Field", **_card_kw)
        jobbtype_card = pn.Card(self.jobbtype_pane, title="Salary by Job Type", **_card_kw)
        scatter_card = pn.Card(self.scatter_pane, title="Experience vs. Salary", **_card_kw)

        charts_tab = pn.Column(
            self.count_md,
            hist_card,
            fag_card,
            jobbtype_card,
            scatter_card,
            sizing_mode="stretch_width",
            align="center",
        )

        table_tab = pn.Column(
            self.count_md,
            self.table,
            sizing_mode="stretch_width",
            css_classes=["salario-panel"],
        )

        help_tab = pn.pane.Markdown(
            _load_help(),
            sizing_mode="stretch_width",
            max_width=800,
        )

        tabs = pn.Tabs(
            ("Plots", charts_tab),
            ("Table", table_tab),
            ("Help", help_tab),
            sizing_mode="stretch_width",
        )

        return pn.Row(sidebar, tabs, sizing_mode="stretch_width")


if pn.state.served:
    SalarioApp().servable(title="Salary Analysis — kode24 2025")
