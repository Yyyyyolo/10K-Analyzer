import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import Canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import analyzer
import downloader
import json
import re
import time
import ast

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

    def draw_sales_pie_chart(self, sales_data_str):
        # Extract the dictionary part using regular expression
        print(sales_data_str)
        dict_match = re.search(r"\{.*\}", sales_data_str, re.DOTALL)
        print(dict_match)
        if dict_match:
            sales_data_str = dict_match.group(0)
            try:
                # Convert the string representation of the dictionary into an actual dictionary
                sales_data = ast.literal_eval(sales_data_str)
            except (SyntaxError, ValueError):
                print("Error parsing dictionary")
                return
        else:
            print("No valid dictionary found")
            return

        labels = []
        sizes = []
        total_sales = sales_data.get("Total", 0)
        other_sales = total_sales

        for label, sales in sales_data.items():
            if label != "Total":
                labels.append(label)
                sizes.append(sales)
                other_sales -= sales

        if other_sales > 0:
            labels.append("Other")
            sizes.append(other_sales)

        # Create the pie chart
        fig = plt.Figure(figsize=(9, 6))
        ax = fig.add_subplot(111)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title("Income Distribution")

        chart = FigureCanvasTkAgg(fig, self.canvas1)
        chart.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        chart.draw()

    def analyze(self):
        ticker = self.ticker_entry.get()
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, f"Analyzing {ticker}...\n")
 
        a = analyzer.analyzer("d9afe4b3-bb3f-46b0-b37b-373cae94aba8", "Meta-Llama-3-8B-Instruct", ticker)
        # Example Text Output
        self.text_output.insert(tk.END, f"Result for {ticker}: {a.analyze_1()}\n")
        #time.sleep(60)
        pie_str = a.analyze_income()
        self.draw_sales_pie_chart(pie_str)
        #time.sleep(60)
        """# Example Plot 1
        fig1 = plt.Figure(figsize=(4, 3))
        ax1 = fig1.add_subplot(111)
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)
        ax1.plot(x, y)
        ax1.set_title('Sine Wave')

        chart1 = FigureCanvasTkAgg(fig1, self.canvas1)
        chart1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        chart1.draw()"""

        
def main():
    root = tk.Tk()
    gui = TickerAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()