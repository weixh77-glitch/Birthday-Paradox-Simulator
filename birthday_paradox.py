"""生日悖论桌面演示，使用 Python 标准库。"""

import random
import tkinter as tk
from collections import Counter
from datetime import date, timedelta
from tkinter import messagebox, simpledialog, ttk

DAYS = 365
TRIALS = 10_000
MAX_PEOPLE = 10_000


def probability_curves(people, trials=TRIALS):
    """返回从 0 人到指定人数的理论概率和模拟概率。"""
    limit = min(people, DAYS + 1)
    theoretical = [0.0] * (limit + 1)
    no_match = 1.0
    for size in range(1, limit + 1):
        no_match *= (DAYS - size + 1) / DAYS
        theoretical[size] = 1 - no_match

    first_matches = [0] * (limit + 1)
    for _ in range(trials):
        seen = set()
        for size in range(1, limit + 1):
            birthday = random.randrange(DAYS)
            if birthday in seen:
                first_matches[size] += 1
                break
            seen.add(birthday)

    simulated = [0.0] * (limit + 1)
    matches = 0
    for size in range(1, limit + 1):
        matches += first_matches[size]
        simulated[size] = matches / trials
    return theoretical, simulated


def draw_chart(canvas, people, theoretical, simulated):
    canvas.delete("all")
    width, height = canvas.winfo_width(), canvas.winfo_height()
    if width < 150 or height < 120:
        return
    left, right, top, bottom = 62, width - 28, 24, height - 48
    max_x = max(60, min(people, DAYS + 1))

    def position(size, probability):
        return (
            left + size / max_x * (right - left),
            bottom - probability * (bottom - top),
        )

    for percent in range(0, 101, 25):
        _, y = position(0, percent / 100)
        canvas.create_line(left, y, right, y, fill="#dce3eb")
        canvas.create_text(left - 9, y, text=f"{percent}%", anchor="e")
    canvas.create_line(left, top, left, bottom, right, bottom, fill="#334155")
    for size in sorted({round(max_x * i / 6) for i in range(7)}):
        x, _ = position(size, 0)
        canvas.create_line(x, bottom, x, bottom + 4)
        canvas.create_text(x, bottom + 14, text=str(size))
    canvas.create_text((left + right) / 2, height - 12, text="人数")

    for values, color, dash in (
        (theoretical, "#185adb", ()),
        (simulated, "#c54d0c", (5, 4)),
    ):
        points = [coord for size, value in enumerate(values)
                  for coord in position(size, value)]
        canvas.create_line(*points, fill=color, width=2, dash=dash)

    chosen = min(people, max_x)
    x, y = position(chosen, theoretical[chosen])
    canvas.create_line(x, bottom, x, y, fill="#64748b", dash=(2, 3))
    canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#185adb", outline="white")


def main():
    root = tk.Tk()
    root.title("生日悖论")
    root.geometry("830x630")
    root.minsize(570, 490)
    root.withdraw()

    first_size = simpledialog.askinteger(
        "生日悖论", f"请输入人数（1–{MAX_PEOPLE:,}）",
        initialvalue=23, minvalue=1, maxvalue=MAX_PEOPLE, parent=root,
    )
    if first_size is None:
        root.destroy()
        return

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)
    controls = ttk.Frame(frame)
    controls.pack(fill="x")
    ttk.Label(controls, text="人数").pack(side="left")
    entry = ttk.Entry(controls, width=10)
    entry.insert(0, str(first_size))
    entry.pack(side="left", padx=8)

    summary = ttk.Label(frame, justify="left")
    legend = ttk.Frame(frame)
    canvas = tk.Canvas(frame, background="white", highlightthickness=0)
    table_frame = ttk.Frame(frame)
    table = ttk.Treeview(
        table_frame, columns=("number", "birthday", "match"),
        show="headings", height=6,
    )
    for column, title in (("number", "编号"), ("birthday", "生日"), ("match", "是否重复")):
        table.heading(column, text=title)
        table.column(column, anchor="center", width=100)
    scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    table.pack(side="left", fill="both", expand=True)

    chart = None

    def redraw(_event=None):
        if chart is not None:
            draw_chart(canvas, *chart)

    def generate(_event=None):
        nonlocal chart
        try:
            people = int(entry.get())
            if not 1 <= people <= MAX_PEOPLE:
                raise ValueError
        except ValueError:
            messagebox.showerror("人数无效", f"请输入 1–{MAX_PEOPLE:,} 之间的整数。", parent=root)
            return

        birthdays = random.choices(range(DAYS), k=people)
        counts = Counter(birthdays)
        repeated_dates = sum(count > 1 for count in counts.values())
        chart_limit = max(60, min(people, DAYS + 1))
        theoretical, simulated = probability_curves(chart_limit)
        index = min(people, DAYS + 1)
        note = "。图表画到 366 人，此后概率恒为 100%" if people > DAYS + 1 else ""
        summary.configure(text=(
            f"{people:,} 人 · 理论概率 {theoretical[index]:.2%} · "
            f"模拟概率 {simulated[index]:.2%}（{TRIALS:,} 次）\n"
            f"本次样本有 {repeated_dates} 个日期重复{note}"
        ))

        table.delete(*table.get_children())
        first_day = date(2001, 1, 1)
        for number, birthday in enumerate(birthdays, start=1):
            day = first_day + timedelta(days=birthday)
            table.insert("", "end", values=(
                number, f"{day.month} 月 {day.day} 日",
                "是" if counts[birthday] > 1 else "—",
            ))
        table.yview_moveto(0)
        chart = (people, theoretical, simulated)
        redraw()

    ttk.Button(controls, text="生成生日", command=generate).pack(side="left")
    entry.bind("<Return>", generate)
    summary.pack(anchor="w", pady=(12, 8))
    ttk.Label(legend, text="━ 理论概率", foreground="#185adb").pack(side="left")
    ttk.Label(legend, text="┄ 模拟概率", foreground="#c54d0c").pack(side="left", padx=12)
    legend.pack(anchor="w")
    canvas.pack(fill="both", expand=True, pady=(4, 10))
    table_frame.pack(fill="x")
    canvas.bind("<Configure>", redraw)
    root.deiconify()
    generate()
    entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()


