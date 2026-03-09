# utils/plot_utils.py

import os
import numpy as np
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


# -------------------------------
# 🎨 7. Create Custom Color Palette
# -------------------------------
def create_color_palette(colors=None, n_colors=None, palette_type="qualitative"):
    """
    Generate a custom color palette.
   
    Args:
        colors (list): List of color names or hex codes
        n_colors (int): Number of colors to generate
        palette_type (str): 'qualitative', 'sequential', or 'diverging'
   
    Returns:
        list: Color palette
    """
    if colors:
        return sns.color_palette(colors, n_colors=n_colors)
    elif palette_type == "sequential":
        return sns.color_palette("Blues", n_colors=n_colors or 8)
    elif palette_type == "diverging":
        return sns.color_palette("RdBu_r", n_colors=n_colors or 11)
    else:  # qualitative
        return sns.color_palette("Set2", n_colors=n_colors or 8)


# -------------------------------
# 📊 8. Plot Comparison (Side-by-Side)
# -------------------------------
def plot_comparison(plot_func, data, params_list, titles, figsize=(15, 5)):
    """
    Create side-by-side plots for comparison.
   
    Args:
        plot_func: Seaborn plotting function
        data: DataFrame to plot
        params_list: List of dictionaries with parameters for each plot
        titles: List of titles for each subplot
        figsize: Figure size tuple
    """
    n_plots = len(params_list)
    fig, axes = plt.subplots(1, n_plots, figsize=figsize)
   
    if n_plots == 1:
        axes = [axes]
   
    for ax, params, title in zip(axes, params_list, titles):
        plot_func(data=data, **params, ax=ax)
        ax.set_title(title, fontweight="bold")
   
    plt.tight_layout()
    return fig, axes


# -------------------------------
# 📈 9. Add Statistical Annotations
# -------------------------------
def add_statistical_annotations(ax, x1, x2, y, p_value, height=0.05):
    """
    Add significance markers to plots.
   
    Args:
        ax: Matplotlib axis
        x1, x2: X positions for comparison
        y: Y position for bracket
        p_value: P-value from statistical test
        height: Height of bracket
    """
    # Determine significance level
    if p_value < 0.001:
        sig_text = "***"
    elif p_value < 0.01:
        sig_text = "**"
    elif p_value < 0.05:
        sig_text = "*"
    else:
        sig_text = "ns"
   
    # Draw bracket
    ax.plot([x1, x1, x2, x2], [y, y+height, y+height, y], 'k-', lw=1.5)
    ax.text((x1+x2)/2, y+height, sig_text, ha='center', va='bottom', fontsize=12)


# -------------------------------
# 💾 10. Export Plot Data
# -------------------------------
def export_plot_data(fig, data, filename, format='csv'):
    """
    Save the data underlying a plot.
   
    Args:
        fig: Figure object (can be None for data-only export)
        data: DataFrame or dict
        filename: Output filename
        format: 'csv', 'xlsx', or 'json'
    """
    import pandas as pd
   
    if data is None:
        return
   
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
   
    folder = os.path.dirname(filename)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
   
    if format == 'csv':
        data.to_csv(filename, index=False)
    elif format == 'xlsx':
        data.to_excel(filename, index=False)
    elif format == 'json':
        data.to_json(filename, orient='records')
   
    print(f"✅ Data exported to {filename}")


# -------------------------------
# 📄 11. Save Publication-Ready Figure
# -------------------------------
def save_publication_figure(fig, filename, formats=['png', 'pdf'], dpi=600, transparent=False):
    """
    Save figure in multiple formats for publication.
   
    Args:
        fig: Matplotlib figure object to save
        filename: Base filename (without extension)
        formats: List of formats to save ('png', 'pdf', 'svg')
        dpi: Resolution (600 or 300 for publications)
        transparent: Transparent background
    """
    for fmt in formats:
        output_file = f"{filename}.{fmt}"
        folder = os.path.dirname(str(output_file))
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
       
        fig.savefig(output_file, dpi=dpi, bbox_inches='tight', 
                   transparent=transparent, format=fmt)
        print(f"✅ Saved: {output_file}")


# -------------------------------
# 🔲 12. Create Plot Grid
# -------------------------------
def create_plot_grid(rows, cols, figsize=None):
    """
    Create a grid of subplots for complex layouts.
   
    Args:
        rows: Number of rows
        cols: Number of columns
        figsize: Figure size (auto-calculated if None)
   
    Returns:
        fig, axes: Figure and axes array
    """
    if figsize is None:
        figsize = (cols * 5, rows * 4)
   
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
   
    # Flatten axes for easier iteration
    if rows == 1 and cols == 1:
        axes = np.array([axes])
    elif rows == 1 or cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
   
    print(f"✅ Created {rows}x{cols} plot grid")
    return fig, axes

