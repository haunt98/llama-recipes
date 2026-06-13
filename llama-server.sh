#!/usr/bin/env bash

# llama-server --cache-list
# llama-server --fim-qwen-1.5b-default
# llama-server --fim-qwen-3b-default
llama-server \
    -hf JetBrains/Mellum-4b-dpo-all-gguf:Q8_0 \
    --port 8012 \
    --ctx-size 8192
