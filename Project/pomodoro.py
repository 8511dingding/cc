"""
Pomodoro Timer - A simple desktop Pomodoro timer application
"""
import tkinter as tk
from tkinter import ttk
import time
import os


class PomodoroTimer:
    WORK_TIME = 25 * 60  # 25 minutes in seconds
    SHORT_BREAK = 5 * 60  # 5 minutes
    LONG_BREAK = 15 * 60  # 15 minutes
    SESSIONS_BEFORE_LONG_BREAK = 4

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # Center window
        self.root.eval('tk::PlaceWindow . center')

        self.work_time = self.WORK_TIME
        self.break_time = self.SHORT_BREAK
        self.long_break_time = self.LONG_BREAK
        self.sessions = 0
        self.is_running = False
        self.is_work = True
        self.remaining = self.work_time
        self.timer_id = None

        self.setup_ui()

        # Bind keyboard shortcuts
        self.root.bind('<space>', lambda e: self.toggle_timer())
        self.root.bind('<r>', lambda e: self.reset_timer())
        self.root.bind('<q>', lambda e: self.root.quit())

    def setup_ui(self):
        # Configure colors
        self.bg_color = "#2D2D2D"
        self.accent_color = "#E74C3C"
        self.break_color = "#27AE60"
        self.long_break_color = "#3498DB"
        self.text_color = "#FFFFFF"

        self.root.configure(bg=self.bg_color)

        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_frame,
            text="🍅 Pomodoro Timer",
            font=("Arial", 24, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 10))

        # Session info
        self.session_label = tk.Label(
            main_frame,
            text=f"Session {self.sessions + 1} of {self.SESSIONS_BEFORE_LONG_BREAK}",
            font=("Arial", 12),
            fg="#888888",
            bg=self.bg_color
        )
        self.session_label.pack()

        # Timer type label
        self.type_label = tk.Label(
            main_frame,
            text="WORK",
            font=("Arial", 16, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        self.type_label.pack(pady=(30, 10))

        # Timer display
        self.time_label = tk.Label(
            main_frame,
            text=self.format_time(self.remaining),
            font=("Arial", 72, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.time_label.pack()

        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Press Start to begin",
            font=("Arial", 10),
            fg="#666666",
            bg=self.bg_color
        )
        self.status_label.pack(pady=(10, 20))

        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(pady=20)

        # Start/Pause button
        self.start_btn = tk.Button(
            btn_frame,
            text="Start",
            font=("Arial", 14, "bold"),
            width=8,
            command=self.toggle_timer,
            bg=self.accent_color,
            fg=self.text_color,
            activebackground="#C0392B",
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # Reset button
        reset_btn = tk.Button(
            btn_frame,
            text="Reset",
            font=("Arial", 14),
            width=8,
            command=self.reset_timer,
            bg="#555555",
            fg=self.text_color,
            activebackground="#666666",
            relief=tk.FLAT,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        # Skip button
        skip_btn = tk.Button(
            btn_frame,
            text="Skip",
            font=("Arial", 14),
            width=8,
            command=self.skip_session,
            bg="#555555",
            fg=self.text_color,
            activebackground="#666666",
            relief=tk.FLAT,
            cursor="hand2"
        )
        skip_btn.pack(side=tk.LEFT, padx=5)

        # Controls hint
        hint_label = tk.Label(
            main_frame,
            text="Space: Start/Pause | R: Reset | Q: Quit",
            font=("Arial", 9),
            fg="#555555",
            bg=self.bg_color
        )
        hint_label.pack(side=tk.BOTTOM, pady=(20, 0))

        # Style buttons
        for btn in [self.start_btn, reset_btn, skip_btn]:
            btn.configure(relief=tk.FLAT)

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def toggle_timer(self):
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.is_running = True
        self.start_btn.configure(text="Pause", bg="#F39C12", activebackground="#E67E22")
        self.status_label.configure(text="Running...")
        self.countdown()

    def pause_timer(self):
        self.is_running = False
        self.start_btn.configure(text="Resume", bg=self.accent_color, activebackground="#C0392B")
        self.status_label.configure(text="Paused")
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def reset_timer(self):
        self.is_running = False
        self.start_btn.configure(text="Start", bg=self.accent_color, activebackground="#C0392B")
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        if self.is_work:
            self.remaining = self.work_time
        elif self.sessions == self.SESSIONS_BEFORE_LONG_BREAK:
            self.remaining = self.long_break_time
        else:
            self.remaining = self.break_time

        self.time_label.configure(text=self.format_time(self.remaining))
        self.status_label.configure(text="Press Start to begin")

    def skip_session(self):
        self.is_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.switch_session()

    def countdown(self):
        if not self.is_running:
            return

        if self.remaining > 0:
            self.time_label.configure(text=self.format_time(self.remaining))
            self.timer_id = self.root.after(1000, self.countdown)
        else:
            self.on_session_complete()

    def on_session_complete(self):
        if self.is_work:
            self.sessions += 1
            self.session_label.configure(text=f"Session {self.sessions} of {self.SESSIONS_BEFORE_LONG_BREAK}")

        self.switch_session()

        # Auto-start next session
        if self.is_work:
            self.status_label.configure(text="Break time! Starting...")
        else:
            self.status_label.configure(text="Work time! Starting...")
        self.start_timer()

    def switch_session(self):
        self.is_work = not self.is_work

        if self.is_work:
            self.type_label.configure(text="WORK", fg=self.accent_color)
            self.remaining = self.work_time
        elif self.sessions >= self.SESSIONS_BEFORE_LONG_BREAK:
            self.type_label.configure(text="LONG BREAK", fg=self.long_break_color)
            self.remaining = self.long_break_time
            self.sessions = 0
            self.session_label.configure(text=f"Session {self.sessions + 1} of {self.SESSIONS_BEFORE_LONG_BREAK}")
        else:
            self.type_label.configure(text="SHORT BREAK", fg=self.break_color)
            self.remaining = self.break_time

        self.start_btn.configure(text="Start", bg=self.accent_color, activebackground="#C0392B")
        self.time_label.configure(text=self.format_time(self.remaining))
        self.status_label.configure(text="Press Start to begin")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()