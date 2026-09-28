"""Interactive GUI to plot the PDF of a chosen distribution with adjustable parameters."""
import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import stats


# Each entry: params is a list of (label, default) tuples (1 or 2 params).
# dist(*values) must return a frozen scipy.stats distribution.
DISTRIBUTIONS = {
    "Normal": {
        "params": [("mean (mu)", 0.0), ("std dev (sigma)", 1.0)],
        "dist": lambda mu, sigma: stats.norm(loc=mu, scale=sigma),
    },
    "Uniform": {
        "params": [("lower (a)", 0.0), ("upper (b)", 1.0)],
        "dist": lambda a, b: stats.uniform(loc=a, scale=b - a),
    },
    "Exponential": {
        "params": [("rate (lambda)", 1.0)],
        "dist": lambda lam: stats.expon(scale=1.0 / lam),
    },
    "Gamma": {
        "params": [("shape (k)", 2.0), ("scale (theta)", 1.0)],
        "dist": lambda k, theta: stats.gamma(a=k, scale=theta),
    },
    "Beta": {
        "params": [("alpha", 2.0), ("beta", 2.0)],
        "dist": lambda a, b: stats.beta(a=a, b=b),
    },
    "Chi-square": {
        "params": [("degrees of freedom (df)", 3.0)],
        "dist": lambda df: stats.chi2(df=df),
    },
    "Student t": {
        "params": [("degrees of freedom (df)", 5.0)],
        "dist": lambda df: stats.t(df=df),
    },
    "Lognormal": {
        "params": [("mean of log (mu)", 0.0), ("std dev of log (sigma)", 0.5)],
        "dist": lambda mu, sigma: stats.lognorm(s=sigma, scale=np.exp(mu)),
    },
}


class DistributionPdfApp:
    """GUI for selecting a distribution, entering its parameters, and plotting its pdf."""

    def __init__(self, root):
        self.root = root
        self.root.title("Distribution PDF Viewer")
        self.root.minsize(900, 650)

        self.dist_name = tk.StringVar(value="Normal")
        self.param_vars = []
        self.status = tk.StringVar(value="Choose a distribution and parameters, then click Plot.")

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
        self.param_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=4)

        ttk.Button(controls, text="Plot", command=self.plot).grid(
            row=0, column=2, rowspan=2, padx=(20, 0), ipadx=12, ipady=5
        )

        ttk.Label(self.root, textvariable=self.status).pack(anchor=tk.W, padx=16, pady=(0, 6))

    def _build_plot(self):
        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    def _on_distribution_change(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.param_vars = []

        spec = DISTRIBUTIONS[self.dist_name.get()]
        for row, (label, default) in enumerate(spec["params"]):
            ttk.Label(self.param_frame, text=f"{label}:").grid(
                row=row, column=0, sticky=tk.W, padx=(0, 8), pady=4
            )
            var = tk.StringVar(value=str(default))
            ttk.Entry(self.param_frame, textvariable=var, width=12).grid(
                row=row, column=1, sticky=tk.W, pady=4
            )
            self.param_vars.append(var)

    def plot(self):
        name = self.dist_name.get()
        spec = DISTRIBUTIONS[name]
        try:
            values = [float(var.get()) for var in self.param_vars]
            rv = spec["dist"](*values)
        except ValueError:
            messagebox.showerror("Invalid input", "Parameters must be numeric.")
            return
        except Exception as exc:
            messagebox.showerror("Invalid parameters", str(exc))
            return

        lo, hi = rv.ppf(0.001), rv.ppf(0.999)
        if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
            messagebox.showerror("Invalid parameters", "Parameters produce a degenerate distribution.")
            return

        x = np.linspace(lo, hi, 500)
        pdf = rv.pdf(x)

        self.ax.clear()
        self.ax.plot(x, pdf, color="tab:blue", linewidth=2)
        self.ax.fill_between(x, pdf, alpha=0.2, color="tab:blue")
        param_text = ", ".join(
            f"{label}={value:g}" for (label, _), value in zip(spec["params"], values)
        )
        self.ax.set_title(f"{name} PDF ({param_text})")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()
        self.status.set(f"Plotted {name} with {param_text}.")


def main():
    root = tk.Tk()
    DistributionPdfApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
