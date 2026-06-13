#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.request

UPSTREAM = "http://127.0.0.1:8012/completion"


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/infill":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        req = json.loads(self.rfile.read(length) or b"{}")

        prefix = req.get("input_prefix", "")
        middle = req.get("prompt", "")
        suffix = req.get("input_suffix", "")
        filename = req.get("filename", "current_file")

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
            "stop": req.get("stop") or [
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
            upstream_req = urllib.request.Request(
                UPSTREAM,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(upstream_req, timeout=10) as resp:
                out = resp.read()
                status = resp.status
        except Exception as e:
            status = 502
            out = json.dumps({
                "error": {
                    "message": str(e),
                    "type": "adapter_error",
                }
            }).encode()

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *_):
        return


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8013), Handler).serve_forever()
