#!/usr/bin/env python3

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from rich.console import Console

console = Console()

# https://github.com/ggml-org/llama.cpp/tree/master/tools/server
UPSTREAM_URL = "http://127.0.0.1:8012/completion"


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        req = json.loads(self.rfile.read(length) or b"{}")

        console.log(self.path, req)

        if self.path != "/infill":
            self.send_error(404)
            return

        # Upstream example
        # llama-cli -m mellum-4b-dpo-all.Q8_0.gguf --temp 0 -p $'<filename>Utils.kt\npackage utils\n\nfun multiply(x: Int, y: Int): Int {\n    return x * y\n}\n\n<filename>Config.kt\npackage config\n\nobject Config {\n    const val DEBUG = true\n    const val MAX_VALUE = 100\n}\n\n<filename>Example.kt\n<fim_suffix>\nfun main() {\n    val result = calculateSum(5, 10)\n    println(result)\n}\n<fim_prefix>fun calculateSum(a: Int, b: Int): Int {\n<fim_middle>'

        prefix = req.get("input_prefix", "")
        middle = req.get("prompt", "")
        suffix = req.get("input_suffix", "")
        filename = req.get("filename", "")

        parts = []

        for item in req.get("input_extra", []) or []:
            name = item.get("filename", "")
            text = item.get("text", "")
            if name or text:
                parts.append(f"<filename>{name}\n{text}\n\n")

        parts.append(f"<filename>{filename}\n")
        parts.append(f"<fim_suffix>{suffix}")
        parts.append(f"<fim_prefix>{prefix}{middle}")
        parts.append("<fim_middle>")

        body = {
            "prompt": "".join(parts),
            "n_predict": req.get("n_predict", 64),
            "temperature": 0,
            "top_k": req.get("top_k", 40),
            "top_p": req.get("top_p", 0.99),
            "stop": req.get("stop")
            or [
                "<fim_prefix>",
                "<fim_suffix>",
                "<fim_middle>",
                "<filename>",
                "<|endoftext|>",
            ],
            "cache_prompt": True,
            "stream": False,
            "penalize_nl": False,
            "t_max_predict_ms": req.get("t_max_predict_ms", 1000),
            "response_fields": ["content"],
        }

        data = json.dumps(body).encode()

        try:
            resp = requests.post(
                UPSTREAM_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            out = resp.content
            status = resp.status_code
        except Exception as e:
            console.log(e)

            self.send_error(502)
            return

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(out)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8013), Handler).serve_forever()
