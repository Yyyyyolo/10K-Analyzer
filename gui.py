import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import Canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import analyzer

class TickerAnalyzerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Ticker Analyzer")

        # GUI Elements
        self.label = ttk.Label(master, text="Enter Ticker:")
        self.label.pack()

        self.ticker_entry = ttk.Entry(master)
        self.ticker_entry.pack()

        self.analyze_button = ttk.Button(master, text="Analyze", command=self.analyze)
        self.analyze_button.pack()

        self.text_output = scrolledtext.ScrolledText(master, height=10)
        self.text_output.pack()

        self.canvas_frame1 = ttk.Frame(master)
        self.canvas_frame1.pack()
        self.canvas1 = Canvas(self.canvas_frame1, width=400, height=300)
        self.canvas1.pack(side=tk.LEFT)

        self.canvas_frame2 = ttk.Frame(master)
        self.canvas_frame2.pack()
        self.canvas2 = Canvas(self.canvas_frame2, width=400, height=300)
        self.canvas2.pack(side=tk.LEFT)

    def analyze(self):
        ticker = self.ticker_entry.get()
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, f"Analyzing {ticker}...\n")
 
        a = analyzer.analyzer("d9afe4b3-bb3f-46b0-b37b-373cae94aba8", "Meta-Llama-3-8B-Instruct", ticker)
        # Example Text Output
        self.text_output.insert(tk.END, f"Result for {ticker}: {a.analyze_1()}\n")

        # Example Plot 1
        fig1 = plt.Figure(figsize=(4, 3))
        ax1 = fig1.add_subplot(111)
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)
        ax1.plot(x, y)
        ax1.set_title('Sine Wave')

        chart1 = FigureCanvasTkAgg(fig1, self.canvas1)
        chart1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        chart1.draw()

        # Example Plot 2
        fig2 = plt.Figure(figsize=(4, 3))
        ax2 = fig2.add_subplot(111)
        ax2.plot(x, np.cos(x), color='red')
        ax2.set_title('Cosine Wave')

        chart2 = FigureCanvasTkAgg(fig2, self.canvas2)
        chart2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        chart2.draw()

def main():
    root = tk.Tk()
    gui = TickerAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()