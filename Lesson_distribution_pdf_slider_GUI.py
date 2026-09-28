"""Interactive GUI to plot a distribution's PDF, with parameters set by sliders.

The graph updates live as each slider is dragged.
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


class DistributionPdfSliderApp:
    """GUI for selecting a distribution and dragging sliders to update its pdf plot live."""

    def __init__(self, root):
        self.root = root
        self.root.title("Distribution PDF Viewer (Sliders)")
        self.root.minsize(900, 650)

        self.dist_name = tk.StringVar(value="Normal")
        self.sliders = []
        self.value_labels = []
        self.status = tk.StringVar(value="Choose a distribution and drag sliders to update the plot.")

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

        self.param_frame = ttk.Frame(controls)
        self.param_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=4)
        self.param_frame.columnconfigure(1, weight=1)

        ttk.Label(self.root, textvariable=self.status).pack(anchor=tk.W, padx=16, pady=(0, 6))

    def _build_plot(self):
        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

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
        values = [scale.get() for scale in self.sliders]

        try:
            rv = spec["dist"](*values)
            lo, hi = rv.ppf(0.001), rv.ppf(0.999)
            if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
                raise ValueError("degenerate distribution for the current parameters")
            if discrete:
                x = np.arange(int(np.floor(lo)), int(np.ceil(hi)) + 1)
                y = rv.pmf(x)
            else:
                x = np.linspace(lo, hi, 500)
                y = rv.pdf(x)
        except Exception as exc:
            self.status.set(f"Cannot plot: {exc}")
            return

        self.ax.clear()
        if discrete:
            self.ax.stem(x, y, basefmt=" ")
        else:
            self.ax.plot(x, y, color="tab:blue", linewidth=2)
            self.ax.fill_between(x, y, alpha=0.2, color="tab:blue")
        param_text = ", ".join(
            f"{label}={value:g}" for (label, *_), value in zip(spec["params"], values)
        )
        kind = "PMF" if discrete else "PDF"
        self.ax.set_title(f"{name} {kind} ({param_text})")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)" if not discrete else "P(X = x)")
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()
        self.status.set(f"Showing {name} with {param_text}.")


def main():
    root = tk.Tk()
    DistributionPdfSliderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
