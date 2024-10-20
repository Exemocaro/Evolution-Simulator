import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import filedialog

def parse_log_file(file_path):
    generations = []
    lifespans = []
    food_eaten = []
    distances = []
    remaining_food = []

    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'Generation (\d+): Avg Lifespan: ([\d.]+), Avg Food Eaten: ([\d.]+), Avg Distance: ([\d.]+), Remaining Food: (\d+)', line)
            if match:
                gen, lifespan, food, distance, remain = map(float, match.groups())
                generations.append(gen)
                lifespans.append(lifespan)
                food_eaten.append(food)
                distances.append(distance)
                remaining_food.append(remain)

    return generations, lifespans, food_eaten, distances, remaining_food

def plot_data(generations, lifespans, food_eaten, distances, remaining_food):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    
    line1, = ax1.plot(generations, lifespans, 'b-')
    ax1.set_ylabel('Average Lifespan')
    ax1.set_title('Evolution Simulation Statistics')

    line2, = ax2.plot(generations, food_eaten, 'g-')
    ax2.set_ylabel('Average Food Eaten')

    line3, = ax3.plot(generations, distances, 'r-')
    ax3.set_ylabel('Average Distance')

    line4, = ax4.plot(generations, remaining_food, 'm-')
    ax4.set_xlabel('Generation')
    ax4.set_ylabel('Remaining Food')

    plt.tight_layout()

    return fig, (line1, line2, line3, line4)

def update_annot(line, ann, event):
    x, y = line.get_data()
    xdata = event.xdata
    index = min(range(len(x)), key=lambda i: abs(x[i]-xdata))
    ann.xy = (x[index], y[index])
    text = f"Generation: {x[index]:.0f}\nValue: {y[index]:.2f}"
    ann.set_text(text)
    ann.get_bbox_patch().set_alpha(0.4)

def hover(event, fig, lines, annotations):
    vis = annotations[0].get_visible()
    if event.inaxes in fig.axes:
        for line, ann in zip(lines, annotations):
            cont, _ = line.contains(event)
            if cont:
                update_annot(line, ann, event)
                ann.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    ann.set_visible(False)
                    fig.canvas.draw_idle()

def select_and_plot_log():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    file_path = filedialog.askopenfilename(initialdir=log_dir, title="Select log file",
                                           filetypes=(("Log files", "*.log"), ("All files", "*.*")))

    if file_path:
        generations, lifespans, food_eaten, distances, remaining_food = parse_log_file(file_path)
        
        if not generations:
            print("No data found in the selected log file.")
            root.quit()
            return

        fig, lines = plot_data(generations, lifespans, food_eaten, distances, remaining_food)

        # Create annotations for each line
        annotations = []
        for ax, line in zip(fig.axes, lines):
            ann = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                              bbox=dict(boxstyle="round", fc="w"),
                              arrowprops=dict(arrowstyle="->"))
            ann.set_visible(False)
            annotations.append(ann)

        # Create a new window to display the plot
        plot_window = tk.Toplevel(root)
        plot_window.title("Evolution Simulation Statistics")

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.mpl_connect("motion_notify_event", lambda event: hover(event, fig, lines, annotations))

        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, plot_window)
        toolbar.update()

        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Set up proper closure of the application
        def on_closing():
            plot_window.destroy()
            root.quit()

        plot_window.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    else:
        print("No file selected.")
        root.quit()

if __name__ == "__main__":
    select_and_plot_log()