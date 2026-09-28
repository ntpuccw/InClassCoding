"""Interactive GUI to plot a distribution's PDF or CDF, with parameters set by sliders.

The graph updates live as each slider is dragged or the PDF/CDF radio button is toggled.
"""
import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import stats


# Each entry: params is a list of (label, min, max, default, resolution) tuples (1 or 2 params).
# dist(*values) must return a frozen scipy.stats distribution.
DISTRIBUTIONS = {
    "Normal": {
        "params": [
            ("mean (mu)", -5.0, 5.0, 0.0, 0.1),
            ("std dev (sigma)", 0.1, 5.0, 1.0, 0.1),
        ],
        "dist": lambda mu, sigma: stats.norm(loc=mu, scale=sigma),
    },
    "Uniform": {
        "params": [
            ("lower (a)", -5.0, 5.0, 0.0, 0.1),
            ("width (b-a)", 0.1, 10.0, 1.0, 0.1),
        ],
        "dist": lambda a, width: stats.uniform(loc=a, scale=width),
    },
    "Exponential": {
        "params": [("rate (lambda)", 0.1, 5.0, 1.0, 0.1)],
        "dist": lambda lam: stats.expon(scale=1.0 / lam),
    },
    "Gamma": {
        "params": [
            ("shape (k)", 0.1, 10.0, 2.0, 0.1),
            ("scale (theta)", 0.1, 5.0, 1.0, 0.1),
        ],
        "dist": lambda k, theta: stats.gamma(a=k, scale=theta),
    },
    "Beta": {
        "params": [
            ("alpha", 0.1, 10.0, 2.0, 0.1),
            ("beta", 0.1, 10.0, 2.0, 0.1),
        ],
        "dist": lambda a, b: stats.beta(a=a, b=b),
    },
    "Chi-square": {
        "params": [("degrees of freedom (df)", 1.0, 30.0, 3.0, 1.0)],
        "dist": lambda df: stats.chi2(df=df),
    },
    "Student t": {
        "params": [("degrees of freedom (df)", 1.0, 30.0, 5.0, 1.0)],
        "dist": lambda df: stats.t(df=df),
    },
    "F distribution": {
        "params": [
            ("df1 (numerator)", 1.0, 30.0, 5.0, 1.0),
            ("df2 (denominator)", 1.0, 30.0, 10.0, 1.0),
        ],
        "dist": lambda df1, df2: stats.f(dfn=df1, dfd=df2),
    },
    "Lognormal": {
        "params": [
            ("mean of log (mu)", -2.0, 2.0, 0.0, 0.1),
            ("std dev of log (sigma)", 0.1, 2.0, 0.5, 0.1),
        ],
        "dist": lambda mu, sigma: stats.lognorm(s=sigma, scale=np.exp(mu)),
    },
    "Binomial": {
        "params": [
            ("trials (n)", 1.0, 100.0, 20.0, 1.0),
            ("success prob (p)", 0.01, 1.0, 0.5, 0.01),
        ],
        "dist": lambda n, p: stats.binom(n=n, p=p),
        "discrete": True,
    },
    "Poisson": {
        "params": [("rate (lambda)", 0.1, 30.0, 5.0, 0.1)],
        "dist": lambda lam: stats.poisson(mu=lam),
        "discrete": True,
    },
}


class DistributionPdfCdfSliderApp:
    """GUI for selecting a distribution, dragging sliders, and toggling between PDF and CDF."""

    def __init__(self, root):
        self.root = root
        self.root.title("Distribution PDF/CDF Viewer (Sliders)")
        self.root.minsize(900, 650)

        self.dist_name = tk.StringVar(value="Normal")
        self.plot_type = tk.StringVar(value="PDF")
        self.sliders = []
        self.value_labels = []
        self.status = tk.StringVar(value="Choose a distribution, drag sliders, or switch PDF/CDF.")
        self.crosshair_x = 0.0
        self._dragging = False

        self._build_controls()
        self._build_plot()
        self._on_distribution_change()

    def _build_controls(self):
        controls = ttk.LabelFrame(self.root, text="Distribution parameters", padding=12)
        controls.pack(fill=tk.X, padx=12, pady=(12, 6))
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="Distribution:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=4)
        dist_box = ttk.Combobox(
            controls,
            textvariable=self.dist_name,
            values=list(DISTRIBUTIONS),
            state="readonly",
            width=25,
        )
        dist_box.grid(row=0, column=1, sticky=tk.W, pady=4)
        dist_box.bind("<<ComboboxSelected>>", lambda event: self._on_distribution_change())

        type_frame = ttk.Frame(controls)
        type_frame.grid(row=0, column=2, rowspan=2, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(
            type_frame, text="PDF", variable=self.plot_type, value="PDF", command=self.plot
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            type_frame, text="CDF", variable=self.plot_type, value="CDF", command=self.plot
        ).pack(anchor=tk.W)

        self.param_frame = ttk.Frame(controls)
        self.param_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=4)
        self.param_frame.columnconfigure(1, weight=1)

        ttk.Label(self.root, textvariable=self.status).pack(anchor=tk.W, padx=16, pady=(0, 6))

    def _build_plot(self):
        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.canvas.mpl_connect("button_press_event", self._on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self._on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)

    def _on_mouse_press(self, event):
        if event.inaxes != self.ax or event.xdata is None:
            return
        self._dragging = True
        self.crosshair_x = event.xdata
        self.plot()

    def _on_mouse_release(self, event):
        self._dragging = False

    def _on_mouse_move(self, event):
        if not self._dragging or event.inaxes != self.ax or event.xdata is None:
            return
        self.crosshair_x = event.xdata
        self.plot()

    def _on_distribution_change(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.sliders = []
        self.value_labels = []

        spec = DISTRIBUTIONS[self.dist_name.get()]
        for row, (label, lo, hi, default, resolution) in enumerate(spec["params"]):
            ttk.Label(self.param_frame, text=f"{label}:").grid(
                row=row, column=0, sticky=tk.W, padx=(0, 8), pady=4
            )
            value_label = ttk.Label(self.param_frame, text=f"{default:g}", width=8)
            scale = tk.Scale(
                self.param_frame,
                from_=lo,
                to=hi,
                resolution=resolution,
                orient=tk.HORIZONTAL,
                showvalue=False,
                command=lambda value, lbl=value_label: self._on_slider_move(value, lbl),
            )
            scale.set(default)
            scale.grid(row=row, column=1, sticky=tk.EW, pady=4)
            value_label.grid(row=row, column=2, sticky=tk.W, padx=(8, 0), pady=4)
            self.sliders.append(scale)
            self.value_labels.append(value_label)

        self.plot()

    def _on_slider_move(self, value, label):
        label.config(text=f"{float(value):g}")
        self.plot()

    def plot(self):
        name = self.dist_name.get()
        spec = DISTRIBUTIONS[name]
        discrete = spec.get("discrete", False)
        show_cdf = self.plot_type.get() == "CDF"
        values = [scale.get() for scale in self.sliders]

        try:
            rv = spec["dist"](*values)
            lo, hi = rv.ppf(0.001), rv.ppf(0.999)
            if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
                raise ValueError("degenerate distribution for the current parameters")
            if discrete:
                x = np.arange(int(np.floor(lo)), int(np.ceil(hi)) + 1)
                y = rv.cdf(x) if show_cdf else rv.pmf(x)
            else:
                x = np.linspace(lo, hi, 500)
                y = rv.cdf(x) if show_cdf else rv.pdf(x)
        except Exception as exc:
            self.status.set(f"Cannot plot: {exc}")
            return

        self.ax.clear()
        if discrete:
            if show_cdf:
                self.ax.step(x, y, where="post", color="tab:orange", linewidth=2)
            else:
                self.ax.stem(x, y, basefmt=" ")
        else:
            color = "tab:orange" if show_cdf else "tab:blue"
            self.ax.plot(x, y, color=color, linewidth=2)
            if not show_cdf:
                self.ax.fill_between(x, y, alpha=0.2, color=color)

        cx = min(max(self.crosshair_x, lo), hi)
        if discrete:
            cx = round(cx)
        crosshair_text = ""
        if lo <= cx <= hi:
            cy = rv.cdf(cx) if show_cdf else (rv.pmf(cx) if discrete else rv.pdf(cx))
            self.ax.axvline(x=cx, color="gray", linestyle="--", linewidth=1)
            self.ax.axhline(y=cy, color="gray", linestyle="--", linewidth=1)
            self.ax.plot(cx, cy, "ro", markersize=5, zorder=5)
            y_symbol = "F" if show_cdf else ("P" if discrete else "f")
            crosshair_text = f"x={cx:.4g}, {y_symbol}(x)={cy:.4g}"
            self.ax.annotate(
                crosshair_text,
                xy=(cx, cy),
                xytext=(10, 10),
                textcoords="offset points",
                fontsize=9,
                bbox=dict(boxstyle="round", fc="lightyellow", ec="gray", alpha=0.9),
            )

        param_text = ", ".join(
            f"{label}={value:g}" for (label, *_), value in zip(spec["params"], values)
        )
        kind = "CDF" if show_cdf else ("PMF" if discrete else "PDF")
        self.ax.set_title(f"{name} {kind} ({param_text})")
        self.ax.set_xlabel("x")
        if show_cdf:
            self.ax.set_ylabel("F(x)")
        else:
            self.ax.set_ylabel("P(X = x)" if discrete else "f(x)")
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()
        status_text = f"Showing {name} {kind} with {param_text}."
        if crosshair_text:
            status_text += f"  |  {crosshair_text}"
        self.status.set(status_text)


def main():
    root = tk.Tk()
    DistributionPdfCdfSliderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
