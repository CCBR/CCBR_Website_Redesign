from pathlib import Path

import hicstraw
import matplotlib.pyplot as plt
import numpy as np
import pyBigWig
from matplotlib import colors
from matplotlib.collections import PolyCollection
from matplotlib.patches import FancyArrowPatch


HIC_PATH = Path("/Users/jailwalapa/Desktop/ccbr1487/inter_30.hic")
H3K4ME3_PATH = Path("/Users/jailwalapa/Desktop/ccbr1487/H3K4me3.hg38.bigWig")
H3K27AC_PATH = Path("/Users/jailwalapa/Desktop/ccbr1487/H3K27ac.hg38.bigWig")
RUNX2_PATH = Path("/Users/jailwalapa/Desktop/ccbr1487/RUNX2.hg38.bigWig")
CTCF_PATH = Path("/Users/jailwalapa/Desktop/ccbr1487/SAOS2_CTCF.hg38.bigWig")

CHROM = "chr2"
HIC_CHROM = "2"
RUNX2_PEAK_START = 240_369_752
GPC1_TSS = 240_435_636
ROI_START = 240_360_000
ROI_END = 240_440_000
BIN_SIZE = 5_000
TRACK_BINS = 500

OUT_PNG = Path("/Users/jailwalapa/Desktop/Claude_Redesign/figure5_gpc1_roi_240360000_240440000_skip3rows.png")
OUT_PDF = Path("/Users/jailwalapa/Desktop/Claude_Redesign/figure5_gpc1_roi_240360000_240440000_skip3rows.pdf")


def extract_track(path: Path, bins: int = TRACK_BINS) -> tuple[np.ndarray, np.ndarray]:
    bw = pyBigWig.open(str(path))
    values = np.array(bw.stats(CHROM, ROI_START, ROI_END, nBins=bins, type="mean"), dtype=float)
    bw.close()
    values = np.nan_to_num(values, nan=0.0)
    x = np.linspace(ROI_START, ROI_END, bins)
    return x, values


def extract_matrix() -> tuple[np.ndarray, np.ndarray]:
    matrix = hicstraw.strawAsMatrix(
        "observed",
        "NONE",
        str(HIC_PATH),
        f"{HIC_CHROM}:{ROI_START}:{ROI_END}",
        f"{HIC_CHROM}:{ROI_START}:{ROI_END}",
        "BP",
        BIN_SIZE,
    )
    matrix = np.nan_to_num(matrix, nan=0.0)

    bins = np.arange((ROI_START // BIN_SIZE) * BIN_SIZE, ((ROI_END + BIN_SIZE - 1) // BIN_SIZE) * BIN_SIZE + BIN_SIZE, BIN_SIZE)
    if len(bins) != matrix.shape[0] + 1:
        bins = np.arange(matrix.shape[0] + 1) * BIN_SIZE + (ROI_START // BIN_SIZE) * BIN_SIZE
    return matrix, bins


def make_triangle_polygons(matrix: np.ndarray, bins: np.ndarray, skip_rows: int = 1) -> tuple[list[list[tuple[float, float]]], np.ndarray]:
    polys = []
    vals = []
    n = matrix.shape[0]
    for i in range(n):
        start_j = i + max(skip_rows, 0)
        for j in range(start_j, n):
            x0 = bins[i]
            x1 = bins[i + 1]
            y0 = bins[j]
            y1 = bins[j + 1]

            p1 = ((x0 + y0) / 2.0, -(y0 - x0) / 2.0)
            p2 = ((x1 + y0) / 2.0, -(y0 - x1) / 2.0)
            p3 = ((x1 + y1) / 2.0, -(y1 - x1) / 2.0)
            p4 = ((x0 + y1) / 2.0, -(y1 - x0) / 2.0)
            polys.append([p1, p2, p3, p4])
            vals.append(matrix[i, j])
    return polys, np.array(vals, dtype=float)


def mb_formatter(values: list[int]) -> list[str]:
    return [f"{v/1e6:.3f}" for v in values]


def make_coord_ticks(start: int, end: int, step: int = 10_000) -> list[int]:
    first = ((start + step - 1) // step) * step
    ticks = list(range(first, end, step))
    if not ticks:
        ticks = [start, end]
    return ticks


def draw_track(ax, x: np.ndarray, y: np.ndarray, color: str, label: str, transform=None):
    yy = y if transform is None else transform(y)
    ax.fill_between(x, yy, 0, color=color, alpha=0.72, linewidth=0)
    ax.plot(x, yy, color=color, linewidth=1.25)
    ax.set_xlim(ROI_START, ROI_END)
    ax.set_xticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.985, 0.78, label, transform=ax.transAxes, ha="right", va="center", fontsize=11, fontweight="bold")


def main():
    matrix, bins = extract_matrix()
    h3k4_x, h3k4_y = extract_track(H3K4ME3_PATH)
    h3k27_x, h3k27_y = extract_track(H3K27AC_PATH)
    runx2_x, runx2_y = extract_track(RUNX2_PATH)
    ctcf_x, ctcf_y = extract_track(CTCF_PATH)

    polys, vals = make_triangle_polygons(matrix, bins, skip_rows=3)
    nz = vals[vals > 0]
    vmin = float(np.percentile(nz, 10)) if len(nz) else 0.0
    vmax = float(np.percentile(nz, 99)) if len(nz) else 1.0
    norm = colors.PowerNorm(gamma=0.55, vmin=vmin, vmax=vmax)

    fig = plt.figure(figsize=(9.2, 10.8), constrained_layout=False)
    gs = fig.add_gridspec(
        nrows=9,
        ncols=1,
        height_ratios=[0.8, 0.45, 0.55, 0.8, 0.8, 0.8, 0.8, 2.3, 0.35],
        hspace=0.14,
    )

    ax_title = fig.add_subplot(gs[0])
    ax_title.axis("off")
    ax_title.text(
        0.0,
        0.82,
        "Figure 5 ROI. GPC1 custom upstream window",
        fontsize=19,
        fontweight="bold",
        color="#183166",
        ha="left",
        va="center",
    )
    ax_title.text(
        0.0,
        0.44,
        "Fresh 5 kb Hi-C matrix replotted from raw data with window-relative color scaling",
        fontsize=11.5,
        ha="left",
        va="center",
    )
    ax_title.text(
        0.0,
        0.10,
        f"{CHROM}:{ROI_START:,}-{ROI_END:,}",
        fontsize=11,
        color="#555555",
        ha="left",
        va="center",
    )

    ax_coord = fig.add_subplot(gs[1])
    ax_coord.set_xlim(ROI_START, ROI_END)
    coord_ticks = make_coord_ticks(ROI_START, ROI_END)
    ax_coord.set_xticks(coord_ticks)
    ax_coord.set_xticklabels(mb_formatter(coord_ticks), fontsize=10)
    ax_coord.set_yticks([])
    ax_coord.spines["top"].set_visible(False)
    ax_coord.spines["left"].set_visible(False)
    ax_coord.spines["right"].set_visible(False)
    ax_coord.text(0.0, 0.92, "chr2 coordinates (Mb, hg38)", transform=ax_coord.transAxes, ha="left", va="top", fontsize=10)

    ax_gene = fig.add_subplot(gs[2])
    ax_gene.set_xlim(ROI_START, ROI_END)
    ax_gene.set_ylim(0, 1)
    ax_gene.axis("off")
    ax_gene.hlines(0.55, ROI_START, ROI_END, color="black", linewidth=1.1)
    ax_gene.axvline(GPC1_TSS, color="#2E77FF", linestyle="--", linewidth=1.3)
    arrow = FancyArrowPatch((GPC1_TSS - 5_000, 0.55), (GPC1_TSS, 0.55), arrowstyle="-|>", mutation_scale=16, linewidth=1.4, color="black")
    ax_gene.add_patch(arrow)
    ax_gene.text(GPC1_TSS - 300, 0.73, "GPC1 TSS", color="#2E77FF", fontsize=11, fontweight="bold", ha="right", va="center")
    ax_gene.text(ROI_START, 0.87, "GPC1 gene structure (+ strand)", fontsize=10.5, ha="left", va="center")

    ax_h3k4 = fig.add_subplot(gs[3])
    draw_track(ax_h3k4, h3k4_x, h3k4_y, "#4A90E2", "H3K4me3")

    ax_h3k27 = fig.add_subplot(gs[4], sharex=ax_h3k4)
    draw_track(ax_h3k27, h3k27_x, h3k27_y, "#58C861", "H3K27ac")

    ax_ctcf = fig.add_subplot(gs[5], sharex=ax_h3k4)
    draw_track(ax_ctcf, ctcf_x, ctcf_y, "#7B3FE4", "CTCF (SAOS2, log10)", transform=lambda y: np.log10(y + 1.0))

    ax_runx2 = fig.add_subplot(gs[6], sharex=ax_h3k4)
    draw_track(ax_runx2, runx2_x, runx2_y, "#FF4D4D", "RUNX2")
    ax_runx2.axvline(RUNX2_PEAK_START, color="#555555", linestyle=":", linewidth=1.0)
    ax_runx2.text(RUNX2_PEAK_START, ax_runx2.get_ylim()[1] * 0.92, "RUNX2 peak start", ha="left", va="top", fontsize=8.5, color="#444444")
    ax_runx2.set_xticks([])

    heat_ax = fig.add_subplot(gs[7], sharex=ax_h3k4)
    coll = PolyCollection(polys, array=vals, cmap="Reds", norm=norm, edgecolors="none")
    heat_ax.add_collection(coll)
    heat_ax.set_xlim(bins[0], bins[-1])
    heat_ax.set_ylim(-(bins[-1] - bins[0]) / 2.0, 0)
    heat_ax.axis("off")

    cax = fig.add_subplot(gs[8])
    cb = fig.colorbar(coll, cax=cax, orientation="horizontal")
    cb.set_label("Observed contact frequency (window-relative scaling)", fontsize=10.5)
    cb.ax.tick_params(labelsize=9)

    fig.subplots_adjust(left=0.09, right=0.985, top=0.965, bottom=0.06)
    fig.savefig(OUT_PNG, dpi=220)
    fig.savefig(OUT_PDF)
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
