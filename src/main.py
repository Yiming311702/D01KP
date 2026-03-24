import os
import time
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
print("程序开始运行！")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


class DataReader:
    @staticmethod
    def read_d01kp_data(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError("文件不存在")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        capacity = int(lines[0])
        group_num = int(lines[1])
        groups = []
        for line in lines[2:2 + group_num]:
            nums = list(map(int, line.split()))
            w1, v1, w2, v2, w3, v3 = nums
            groups.append((w1, v1, w2, v2, w3, v3))
        return capacity, groups


class PlotTool:
    @staticmethod
    def draw_scatter(groups):
        ws, vs = [], []
        for g in groups:
            ws.extend([g[0], g[2], g[4]])
            vs.extend([g[1], g[3], g[5]])
        plt.figure(figsize=(7, 4))
        plt.scatter(ws, vs, c='teal', alpha=0.8)
        plt.xlabel("重量")
        plt.ylabel("价值")
        plt.title("重量-价值散点图")
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.show()


class GroupSorter:
    @staticmethod
    def sort_by_third_ratio(groups):
        def key(g):
            w = g[4]
            v = g[5]
            return v / w if w != 0 else 0

        return sorted(groups, key=key, reverse=True)


class DPD01Knapsack:
    def __init__(self, capacity, groups):
        self.capacity = capacity
        self.groups = groups
        self.best_value = 0
        self.time_cost = 0.0

    def solve(self):
        start = time.time()
        cap = self.capacity
        dp = [0] * (cap + 1)
        for g in self.groups:
            w1, v1, w2, v2, w3, v3 = g
            for j in range(cap, -1, -1):
                cur = dp[j]
                if j >= w1:
                    cur = max(cur, dp[j - w1] + v1)
                if j >= w2:
                    cur = max(cur, dp[j - w2] + v2)
                if j >= w3:
                    cur = max(cur, dp[j - w3] + v3)
                dp[j] = cur
        self.best_value = dp[cap]
        self.time_cost = round(time.time() - start, 4)
        return self.best_value, self.time_cost


class ResultSaver:
    @staticmethod
    def save_txt(path, cap, val, t):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"背包容量：{cap}\n最优价值：{val}\n求解时间：{t}s\n")

    @staticmethod
    def save_excel(path, cap, val, t):
        df = pd.DataFrame({
            "背包容量": [cap],
            "最优价值": [val],
            "求解时间(s)": [t]
        })
        df.to_excel(path, index=False)


class MainUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("D01KP求解系统")
        self.root.geometry("700x480")
        self.capacity = 0
        self.groups = []
        self.solver = None
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=15)

        ttk.Button(frame, text="1.读取数据", command=self.load_data).grid(row=0, column=0, padx=6)
        ttk.Button(frame, text="2.绘制散点图", command=self.draw).grid(row=0, column=1, padx=6)
        ttk.Button(frame, text="3.项集排序", command=self.do_sort).grid(row=0, column=2, padx=6)
        ttk.Button(frame, text="4.求解最优解", command=self.calc).grid(row=1, column=0, pady=10)
        ttk.Button(frame, text="5.保存TXT", command=self.save_txt).grid(row=1, column=1)
        ttk.Button(frame, text="6.保存Excel", command=self.save_excel).grid(row=1, column=2)

        ttk.Label(self.root, text="运行结果").pack()
        self.text = tk.Text(self.root, width=80, height=20)
        self.text.pack(pady=8)

    def load_data(self):
        p = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt")])
        if not p:
            return
        try:
            self.capacity, self.groups = DataReader.read_d01kp_data(p)
            self.solver = DPD01Knapsack(self.capacity, self.groups)
            messagebox.showinfo("提示", "数据读取成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def draw(self):
        if not self.groups:
            messagebox.showwarning("提示", "请先读取数据")
            return
        PlotTool.draw_scatter(self.groups)

    def do_sort(self):
        if not self.groups:
            messagebox.showwarning("提示", "请先读取数据")
            return
        self.groups = GroupSorter.sort_by_third_ratio(self.groups)
        self.text.insert(tk.END, "\n已按第三项价值密度排序完成\n")

    def calc(self):
        if not self.solver:
            messagebox.showwarning("提示", "请先读取数据")
            return
        val, t = self.solver.solve()
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, f"背包容量：{self.capacity}\n")
        self.text.insert(tk.END, f"最优价值：{val}\n")
        self.text.insert(tk.END, f"求解时间：{t}s\n")

    def save_txt(self):
        if not self.solver:
            messagebox.showwarning("提示", "请先求解")
            return
        p = filedialog.asksaveasfilename(defaultextension=".txt")
        if p:
            ResultSaver.save_txt(p, self.capacity, self.solver.best_value, self.solver.time_cost)
            messagebox.showinfo("完成", "保存成功")

    def save_excel(self):
        if not self.solver:
            messagebox.showwarning("提示", "请先求解")
            return
        p = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if p:
            ResultSaver.save_excel(p, self.capacity, self.solver.best_value, self.solver.time_cost)
            messagebox.showinfo("完成", "保存成功")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MainUI()
    app.run()