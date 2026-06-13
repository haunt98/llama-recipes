# llama-recipes

Support [ggml-org/llama.vim](https://github.com/ggml-org/llama.vim)

```sh
uv venv --clear
uv sync

source .venv/bin/activate

llama-server --cache-list

llama-server --fim-qwen-1.5b-default
llama-server --fim-qwen-3b-default
```

## [JetBrains/Mellum-4b-dpo-all-gguf](https://huggingface.co/JetBrains/Mellum-4b-dpo-all-gguf)

```sh
bash ./mellum/llama-server.sh

python3 ./mellum/main.py
```
