
MKFILE := $(abspath $(lastword $(MAKEFILE_LIST)))
ROOT 		:= $(abspath $(dir $(MKFILE))/../)


m5lib:
	$(MAKE) -C $(ROOT)/m5lib m5lib

N=2048


CC=g++

all: branch

branch.cpp: branch_gen.py
	python branch_gen.py $N $@

branch: branch.cpp
	$(CC) -o  $@ -g  -static $< -I $(ROOT)/m5lib -L $(ROOT)/m5lib -lm5ops

clean:
	rm -f branch.cpp
	rm -f branch


branch-array: branch_array.cpp
	$(CC) -o  $@ -g  -static $< -I $(ROOT)/m5lib -L $(ROOT)/m5lib -lm5ops


binary-search: binary_search.cpp
	$(CC) -o  $@ -g  -static $< -I $(ROOT)/m5lib -L $(ROOT)/m5lib -lm5ops