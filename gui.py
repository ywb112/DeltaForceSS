# -*- coding: utf-8 -*-
"""DeltaForceSS Windows control panel.

The GUI wraps the existing main.py worker. Automated selling is deliberately
not implemented yet: the game has no verified sell-screen recognition here.
"""
from __future__ import annotations

import os
import sys
import time
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LOG_DIR = APP_DIR / "log"
WORKER_LOG = LOG_DIR / "control-panel-worker.log"

BG = "#0b1020"
PANEL = "#151d30"
PANEL_2 = "#1b2740"
TEXT = "#e8eefc"
MUTED = "#9aa9c5"
ACCENT = "#67e8c5"
BLUE = "#79a7ff"
WARN = "#f5c56b"
RED = "#ff7b86"


def worker_mode() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    log = open(WORKER_LOG, "a", encoding="utf-8", buffering=1)
    sys.stdout = log
    sys.stderr = log
    print("\n" + "=" * 60)
    print("DeltaForceSS worker started:", time.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        import main as legacy_main
        legacy_main.main()
    except BaseException as exc:
        print(f"Worker stopped: {type(exc).__name__}: {exc}")
    finally:
        print("Worker ended:", time.strftime("%Y-%m-%d %H:%M:%S"))
        log.close()


class ControlPanel:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("DeltaForceSS · Control Center")
        self.root.geometry("1040x720")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)
        self.worker: subprocess.Popen | None = None
        self.log_position = 0
        self._setup_style()
        self._build()
        self._refresh()

    def _setup_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL_2, foreground=TEXT, padding=(16, 9))
        style.map("TNotebook.Tab", background=[("selected", "#263858")])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT)
        style.configure("TProgressbar", troughcolor=PANEL_2, background=ACCENT)

    def _label(self, parent, text, size=10, color=TEXT, bold=False):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"))

    def _card(self, parent, title, value, subtitle, color=ACCENT):
        card = tk.Frame(parent, bg=PANEL, padx=18, pady=15, highlightthickness=1,
                        highlightbackground="#25324b")
        self._label(card, title, 10, MUTED, True).pack(anchor="w")
        tk.Label(card, text=value, bg=PANEL, fg=color,
                 font=("Segoe UI Semibold", 21)).pack(anchor="w", pady=(8, 3))
        self._label(card, subtitle, 9, MUTED).pack(anchor="w")
        return card

    def _build(self) -> None:
        header = tk.Frame(self.root, bg=BG, padx=26, pady=22)
        header.pack(fill="x")
        tk.Label(header, text="DeltaForceSS", bg=BG, fg=TEXT,
                 font=("Segoe UI Semibold", 25)).pack(side="left")
        tk.Label(header, text="CONTROL CENTER  /  WINDOWS", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=18, pady=(10, 0))
        self.status = tk.Label(header, text="● IDLE", bg=BG, fg=MUTED,
                               font=("Segoe UI", 10, "bold"))
        self.status.pack(side="right", pady=(10, 0))

        cards = tk.Frame(self.root, bg=BG, padx=26)
        cards.pack(fill="x")
        for title, value, sub, color in [
            ("ENGINE", "Ready", "Original automation core", ACCENT),
            ("WORKER", "Stopped", "Process state", BLUE),
            ("AUTO SELL", "Not connected", "Preview-first implementation pending", WARN),
            ("LOGGING", "Live", "Worker output captured locally", ACCENT),
        ]:
            self._card(cards, title, value, sub, color).pack(side="left", fill="both", expand=True,
                                                               padx=(0, 10))

        body = tk.Frame(self.root, bg=BG, padx=26, pady=18)
        body.pack(fill="both", expand=True)
        self.tabs = ttk.Notebook(body)
        self.tabs.pack(fill="both", expand=True)
        overview = tk.Frame(self.tabs, bg=PANEL, padx=20, pady=18)
        selling = tk.Frame(self.tabs, bg=PANEL, padx=20, pady=18)
        self.tabs.add(overview, text="运行与日志")
        self.tabs.add(selling, text="自动出售")

        tk.Label(overview, text="Automation session", bg=PANEL, fg=TEXT,
                 font=("Segoe UI Semibold", 15)).pack(anchor="w")
        tk.Label(overview, text="请先在游戏中打开特勤处制造页面，再启动自动化。",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 14))
        buttons = tk.Frame(overview, bg=PANEL)
        buttons.pack(fill="x", pady=(0, 14))
        self.start_btn = tk.Button(buttons, text="▶  启动自动化", command=self.start,
                                   bg=ACCENT, fg="#08131c", activebackground="#8af5da",
                                   relief="flat", padx=18, pady=10, font=("Segoe UI", 10, "bold"))
        self.start_btn.pack(side="left")
        self.stop_btn = tk.Button(buttons, text="■  停止", command=self.stop, state="disabled",
                                  bg="#3a2637", fg="#ffd8df", activebackground="#563344",
                                  relief="flat", padx=18, pady=10, font=("Segoe UI", 10, "bold"))
        self.stop_btn.pack(side="left", padx=10)
        tk.Button(buttons, text="打开用户配置", command=self.open_config,
                  bg=PANEL_2, fg=TEXT, relief="flat", padx=16, pady=10).pack(side="left")

        self.log_view = tk.Text(overview, bg="#080d18", fg="#c5d5f2", insertbackground=TEXT,
                                relief="flat", font=("Cascadia Mono", 9), wrap="word",
                                padx=12, pady=10, height=16)
        self.log_view.pack(fill="both", expand=True)
        self.log_view.insert("end", "控制面板已就绪。\n启动后，核心程序日志会显示在这里。\n")
        self.log_view.configure(state="disabled")

        tk.Label(selling, text="自动出售 · 安全接入阶段", bg=PANEL, fg=TEXT,
                 font=("Segoe UI Semibold", 16)).pack(anchor="w")
        tk.Label(selling,
                 text="硬性规则：只卖本程序能够确认由本程序成功生产并领取的物品。\\n\\n"
                      "不能仅凭物品名称相同、出现在仓库或价格合适就出售。必须建立生产记录，并把记录与仓库识别结果严格匹配；"
                      "任何身份不明、记录缺失、数量对不上或 OCR 置信度不足的物品，一律跳过。\\n\\n"
                      "当前版本尚未实现经过验证的出售识别与动作，因此自动出售保持关闭，不会执行出售点击。后续先显示待售清单供你确认，再考虑严格白名单自动出售。",
                 bg=PANEL, fg=MUTED, justify="left", wraplength=840,
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(14, 18))
        tk.Label(selling, text="出售执行：未启用（避免误售）", bg=PANEL, fg=WARN,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        footer = tk.Frame(self.root, bg=BG, padx=26, pady=12)
        footer.pack(fill="x")
        tk.Label(footer, text="提示：自动化会控制鼠标与键盘；运行期间请勿操作游戏窗口。",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(footer, text="Fork build · experimental", bg=BG, fg="#667795",
                 font=("Segoe UI", 9)).pack(side="right")

    def start(self) -> None:
        if self.worker and self.worker.poll() is None:
            return
        if not (APP_DIR / "config.yaml").exists() or not (APP_DIR / "user_config.yaml").exists():
            messagebox.showerror("配置文件缺失", "请确认 config.yaml 和 user_config.yaml 与程序放在同一目录。")
            return
        LOG_DIR.mkdir(exist_ok=True)
        WORKER_LOG.write_text("", encoding="utf-8")
        command = [sys.executable, "--worker"] if getattr(sys, "frozen", False) else [sys.executable, str(Path(__file__).resolve()), "--worker"]
        try:
            self.worker = subprocess.Popen(command, cwd=str(APP_DIR), stdin=subprocess.DEVNULL,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception as exc:
            messagebox.showerror("启动失败", str(exc))
            return
        self.status.config(text="● RUNNING", fg=ACCENT)
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._append_log("启动请求已发送。请观察游戏与日志。")

    def stop(self) -> None:
        if self.worker and self.worker.poll() is None:
            self.worker.terminate()
            self._append_log("已发送停止信号。")
        self._set_stopped()

    def _set_stopped(self) -> None:
        self.status.config(text="● IDLE", fg=MUTED)
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def open_config(self) -> None:
        path = APP_DIR / "user_config.yaml"
        if not path.exists():
            messagebox.showerror("配置文件缺失", f"找不到：{path}")
            return
        try:
            os.startfile(str(path))
        except Exception as exc:
            messagebox.showerror("无法打开配置", str(exc))

    def _append_log(self, text: str) -> None:
        self.log_view.configure(state="normal")
        self.log_view.insert("end", text.rstrip() + "\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def _refresh(self) -> None:
        if WORKER_LOG.exists():
            try:
                content = WORKER_LOG.read_text(encoding="utf-8", errors="replace")
                if len(content) > self.log_position:
                    self._append_log(content[self.log_position:])
                    self.log_position = len(content)
            except OSError:
                pass
        if self.worker and self.worker.poll() is not None:
            self._set_stopped()
            self.worker = None
        self.root.after(800, self._refresh)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker_mode()
        return
    root = tk.Tk()
    ControlPanel(root)
    root.mainloop()


if __name__ == "__main__":
    main()
