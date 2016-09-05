CXX=g++
CFLAGS=-O -std=c++11 -Wall
LIBS=

ifneq ($(OS),Windows_NT)
	LIBS+=-lpthread

	ifeq ($(shell uname),Darwin)
		LIBS+=-framework IOKit -framework CoreFoundation
	endif
endif

all: minidx3

minidx3: main.cpp serial.cpp
	$(CXX) $(CFLAGS) $^ -o $@ $(LIBS)

clean:
	- rm -rf minidx3 minidx3.exe
