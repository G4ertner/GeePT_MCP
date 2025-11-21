from __future__ import annotations

import argparse
import tkinter as tk
from tkinter import messagebox

import requests

DEFAULT_SERVER_URL = "http://127.0.0.1:8000"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a user injection message to GeePT MCP")
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run identifier to target (e.g., streamable HTTP session id)",
    )
    parser.add_argument(
        "--server-url",
        default=DEFAULT_SERVER_URL,
        help="Base server URL hosting the injection endpoint",
    )
    return parser.parse_args()


def _build_target_url(server_url: str, run_id: str) -> str:
    trimmed = server_url.rstrip("/")
    return f"{trimmed}/runs/{run_id}/inject"


def main() -> None:
    args = _parse_args()
    target_url = _build_target_url(args.server_url, args.run_id)

    root = tk.Tk()
    root.title("Send injection message")

    tk.Label(root, text="Injection message:").pack(anchor="w", padx=10, pady=(10, 0))

    text_box = tk.Text(root, height=6, width=60)
    text_box.pack(padx=10, pady=5)

    status_var = tk.StringVar(value=f"Target: {target_url}")
    status_label = tk.Label(root, textvariable=status_var, fg="gray")
    status_label.pack(anchor="w", padx=10)

    def send_message() -> None:
        message = text_box.get("1.0", "end-1c").strip()
        if not message:
            messagebox.showwarning("Empty message", "Enter a message before sending.")
            return

        try:
            response = requests.post(target_url, json={"message": message}, timeout=10)
        except Exception as exc:  # noqa: BLE001 - surface network errors cleanly
            messagebox.showerror("Network error", f"Failed to send message: {exc}")
            return

        if response.ok:
            messagebox.showinfo("Sent", "Message queued for next tool response.")
            text_box.delete("1.0", "end")
        else:
            messagebox.showerror(
                "Server error", f"Server responded with {response.status_code}: {response.text}"
            )

    send_button = tk.Button(root, text="Send", command=send_message)
    send_button.pack(pady=(5, 10))

    root.mainloop()


if __name__ == "__main__":
    main()
