# utils/plot_utils.py

import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# -------------------------------
# 🌈 1. Apply Seaborn Theme
# -------------------------------
def apply_theme(style="whitegrid", context="notebook", palette="deep"):
    """
    Apply a consistent Seaborn theme across the project.
    """
    sns.set_theme(style=style, context=context, palette=palette)

# -------------------------------
# 🖌️ 2. Stylize Plot Titles & Labels
# -------------------------------
def stylize_plot(title=None, xlabel=None, ylabel=None, rotate_xticks=0, rotate_yticks=0):
    """
    Set plot title, axis labels, and optional rotation of ticks.
    """
    if title:
        plt.title(title, fontsize=14, fontweight="bold")
    if xlabel:
        plt.xlabel(xlabel, fontsize=12)
    if ylabel:
        plt.ylabel(ylabel, fontsize=12)
    if rotate_xticks:
        plt.xticks(rotation=rotate_xticks)
    if rotate_yticks:
        plt.yticks(rotation=rotate_yticks)
    plt.tight_layout()

# -------------------------------
# 📏 3. Add Reference Lines
# -------------------------------
def add_reference_line(value, axis='h', linestyle='--', color='gray', **kwargs):
    """
    Draw horizontal or vertical line at a specific value.
    """
    if axis == 'h':
        plt.axhline(y=value, linestyle=linestyle, color=color, **kwargs)
    elif axis == 'v':
        plt.axvline(x=value, linestyle=linestyle, color=color, **kwargs)

# -------------------------------
# 💾 4. Save Figure
# -------------------------------
def save_fig(filename, dpi=300):
    """
    Save the current matplotlib figure to a file.
    Auto-creates folders in the path if needed.

    Args:
        filename (str): Full relative path like "exports/01_setup/plot.png"
        dpi (int): Image resolution
    """
    folder = os.path.dirname(filename)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    plt.savefig(filename, dpi=dpi, bbox_inches="tight")
    print(f"✅ Plot saved to {filename}")

# -------------------------------
# 🏷️ 5. Annotate Data Points
# -------------------------------
def annotate_points(x, y, labels=None, offset=0.3):
    """
    Annotate points on a scatterplot.
    """
    for i in range(len(x)):
        label = labels[i] if labels is not None else f"{x[i]}, {y[i]}"
        plt.text(x[i] + offset, y[i], str(label), fontsize=9, color="black")


# -------------------------------
# 📆 6. Format Date X-Axis
# -------------------------------
def format_date_axis(
    ax=None,
    date_format="%b %Y",
    major_locator="month",
    rotate_xticks=45
):
    """
    Format the x-axis for time series plots with readable date labels.

    Args:
        ax (matplotlib axis): Axis to apply formatting to (default: current)
        date_format (str): Date label format (e.g. "%b %Y" for Jan 2024)
        major_locator (str): 'month', 'week', or 'day'
        rotate_xticks (int): Degree of rotation for x-ticks
    """
    if ax is None:
        ax = plt.gca()

    if major_locator == "month":
        ax.xaxis.set_major_locator(mdates.MonthLocator())
    elif major_locator == "week":
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    elif major_locator == "day":
        ax.xaxis.set_major_locator(mdates.DayLocator())

    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
    plt.xticks(rotation=rotate_xticks)
    plt.tight_layout()
