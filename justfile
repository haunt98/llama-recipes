
all: format lint

lint:
    ruff check --select I --fix

format:
    shfmt -w -s -i 4 **/*.sh
    ruff format
    npx prettier --log-level error --print-width 120 --tab-width 4 --prose-wrap always --write **/*.md
