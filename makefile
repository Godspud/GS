CC = gcc
HOST_CFLAGS = -Wall -Wextra -O2

BUILD_DIR = build
MY_COMPILER = $(BUILD_DIR)/gsc

.DEFAULT_GOAL := all

all: $(MY_COMPILER)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# build the GS compiler from GS.c
$(MY_COMPILER): GS.c | $(BUILD_DIR)
	$(CC) $(HOST_CFLAGS) GS.c -o $@
	@echo "=== GSC built ==="

# usage: make run FILE=test.gs
run: $(MY_COMPILER)
	@if [ -z "$(FILE)" ]; then \
		echo "ERROR: make run FILE=test.gs"; \
		exit 1; \
	fi
	@if [ ! -f "$(FILE)" ]; then \
		echo "ERROR: File '$(FILE)' not found."; \
		exit 1; \
	fi
	@echo "=== Compiling $(FILE) ==="
	$(MY_COMPILER) $(FILE) -o $(BUILD_DIR)/out.c
	@echo "=== Running output ==="
	$(CC) $(BUILD_DIR)/out.c -o $(BUILD_DIR)/out
	$(BUILD_DIR)/out

clean:
	rm -rf $(BUILD_DIR)