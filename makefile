.DEFAULT_GOAL := all

EXAMPLES = examples/$(shell find $(SRC_DIR) -name '*.GOS')

all:
	@echo $(EXAMPLES)
	$(shell for entries in $(EXAMPLES); do\n python3 main.py "$entries" \ndone)