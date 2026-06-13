#!/usr/bin/env bash

llama-server \
    -hf JetBrains/Mellum-4b-dpo-all-gguf:Q8_0 \
    --port 8012 \
    --ctx-size 0 \
    --cache-reuse 256
