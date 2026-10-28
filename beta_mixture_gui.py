"""GUI for sampling from a mixture of two Beta distributions.

f(x) = pi1 * Beta(x | a1, b1) + (1 - pi1) * Beta(x | a2, b2)
"""

import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.optimize import minimize
from scipy.stats import beta, binom

INITIAL_PARAMS = (0.5, 1, 6, 6, 1)


def log_joint_likelihood(params, data):
    pi1, a1, b1, a2, b2 = params
    pdf = pi1 * beta.pdf(data, a1, b1) + (1 - pi1) * beta.pdf(data, a2, b2)
    return np.sum(np.log(np.maximum(pdf, 1e-300)))


def neg_log_joint_likelihood(params, data):
    return -log_joint_likelihood(params, data)


def _moment_init(part):
    m, v = part.mean(), max(part.var(), 1e-4)
    k = max(m * (1 - m) / v - 1, 0.5)
    return max(m * k, 0.1), max((1 - m) * k, 0.1)


def fit_mixture_mle(data):
    """Minimize the negative log joint likelihood; returns (pi1, a1, b1, a2, b2).

    Starts from the notebook's initial point plus data-driven starts (moment
    fits of the lower/upper halves around several split points) and keeps the
    best optimum, since the likelihood is multimodal.
    """
    starts = [INITIAL_PARAMS]
    if data.size >= 4:
        for q in (0.25, 0.5, 0.75):
            cut = np.quantile(data, q)
            lo, hi = data[data <= cut], data[data > cut]
            if lo.size >= 2 and hi.size >= 2:
                starts.append((0.5, *_moment_init(lo), *_moment_init(hi)))
    best = None
    for start in starts:
        result = minimize(
            neg_log_joint_likelihood,
            start,
            args=(data,),
            method="L-BFGS-B",
            bounds=[(0, 1)] + [(0.001, None)] * 4,
        )
        if np.all(np.isfinite(result.x)) and (best is None or result.fun < best.fun):
            best = result
    return tuple(best.x) if best is not None else None

DEFAULTS = {
    "pi1": "0.3",
    "a1": "5",
    "b1": "3",
    "a2": "2",
    "b2": "6",
    "n": "1000",
    "bins": "50",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Beta Mixture Sampler")
        self.vars = {k: tk.StringVar(value=v) for k, v in DEFAULTS.items()}

        panel = ttk.Frame(self, padding=10)
        panel.grid(row=0, column=0, sticky="ns")
        labels = [
            ("pi1 (weight of component 1)", "pi1"),
            ("a1", "a1"),
            ("b1", "b1"),
            ("a2", "a2"),
            ("b2", "b2"),
            ("Sample size n", "n"),
            ("Histogram bins", "bins"),
        ]
        for row, (text, key) in enumerate(labels):
            ttk.Label(panel, text=text).grid(row=row, column=0, sticky="w", pady=2)
            entry = ttk.Entry(panel, textvariable=self.vars[key], width=10)
            entry.grid(row=row, column=1, padx=(8, 0), pady=2)
            entry.bind("<Return>", lambda _e: self.run())

        ttk.Button(panel, text="Run experiment", command=self.run).grid(
            row=len(labels), column=0, columnspan=2, pady=(12, 2), sticky="ew"
        )
        ttk.Button(panel, text="Reset", command=self.reset).grid(
            row=len(labels) + 1, column=0, columnspan=2, pady=2, sticky="ew"
        )
        self.info = ttk.Label(panel, text="", justify="left")
        self.info.grid(row=len(labels) + 2, column=0, columnspan=2, pady=10, sticky="w")

        self.fig = Figure(figsize=(6.5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.run()

    def on_close(self):
        plt.close("all")
        self.destroy()

    def reset(self):
        for k, v in DEFAULTS.items():
            self.vars[k].set(v)
        self.run()

    def read_params(self):
        try:
            pi1 = float(self.vars["pi1"].get())
            a1, b1, a2, b2 = (float(self.vars[k].get()) for k in ("a1", "b1", "a2", "b2"))
            n = int(self.vars["n"].get())
            bins = int(self.vars["bins"].get())
        except ValueError:
            raise ValueError("All fields must be numbers (n and bins must be integers).")
        if not 0 <= pi1 <= 1:
            raise ValueError("pi1 must be between 0 and 1.")
        if min(a1, b1, a2, b2) <= 0:
            raise ValueError("a1, b1, a2, b2 must be positive.")
        if n < 1 or bins < 1:
            raise ValueError("n and bins must be at least 1.")
        return pi1, a1, b1, a2, b2, n, bins

    def run(self):
        try:
            pi1, a1, b1, a2, b2, n, bins = self.read_params()
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        pi2 = 1 - pi1
        n1 = int(binom.rvs(n, pi1))
        n2 = n - n1
        sample1 = beta.rvs(a1, b1, size=n1)
        sample2 = beta.rvs(a2, b2, size=n2)
        samples = np.concatenate([sample1, sample2])

        x = np.linspace(0, 1, 402)[1:-1]
        y = pi1 * beta.pdf(x, a1, b1) + pi2 * beta.pdf(x, a2, b2)

        # MLE from the pooled mixture samples (as in gar1028.ipynb)
        est = fit_mixture_mle(samples)
        if est is not None:
            p, e1, f1, e2, f2 = est
            swapped = (1 - p, e2, f2, e1, f1)
            truth = np.array([pi1, a1, b1, a2, b2])
            # the likelihood is symmetric in the labels; align them with the truth
            if np.abs(np.array(swapped) - truth).sum() < np.abs(np.array(est) - truth).sum():
                est = swapped
        self.ax.clear()
        self.ax.hist(
            samples, bins=bins, density=True, alpha=0.5, color="gray", label="Histogram"
        )
        self.ax.plot(x, y, label="True density")
        if est is not None:
            p1h, a1h, b1h, a2h, b2h = est
            y_hat = p1h * beta.pdf(x, a1h, b1h) + (1 - p1h) * beta.pdf(x, a2h, b2h)
            self.ax.plot(x, y_hat, "r--", label="Estimated density (MLE)")
        self.ax.legend()
        self.ax.set_title(
            rf"f(x) = {pi1:g} $\beta(x|{a1:g},{b1:g})$ + {pi2:g} $\beta(x|{a2:g},{b2:g})$"
        )
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw()

        mle_text = ""
        if est is not None:
            mle_text = (
                "\n\nMLE estimates:\n"
                f"pi1 = {est[0]:.3f}\na1 = {est[1]:.3f}, b1 = {est[2]:.3f}\n"
                f"a2 = {est[3]:.3f}, b2 = {est[4]:.3f}"
            )
        self.info.config(
            text=f"n1 = {n1}, n2 = {n2}\nsample mean = {samples.mean():.4f}\n"
            f"theoretical mean = {pi1 * a1 / (a1 + b1) + pi2 * a2 / (a2 + b2):.4f}"
            + mle_text
        )


if __name__ == "__main__":
    App().mainloop()
