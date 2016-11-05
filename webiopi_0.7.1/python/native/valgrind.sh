#!/bin/sh -x

sudo valgrind --tool=memcheck -v --demangle=yes \
    --leak-check=full \
    --leak-resolution=high \
    --show-reachable=yes \
    --show-possibly-lost=yes \
    $1

