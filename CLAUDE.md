# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a simple Pomodoro Timer desktop application built with Python and tkinter. The timer follows the standard Pomodoro Technique:
- 25-minute work sessions
- 5-minute short breaks
- 15-minute long break after 4 sessions

## Running the Application

```bash
python Project/pomodoro.py
```

## Keyboard Shortcuts

- **Space**: Start/Pause timer
- **R**: Reset timer
- **Q**: Quit application

## Architecture

Single-file application (`Project/pomodoro.py`) with a `PomodoroTimer` class that manages all timer state and UI. The class uses:
- `tkinter` for the GUI
- `root.after()` for non-blocking timer countdown
- Color-coded states: red for work, green for short break, blue for long break