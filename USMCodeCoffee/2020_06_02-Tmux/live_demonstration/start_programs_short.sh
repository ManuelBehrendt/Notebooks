#!/bin/bash

tmux \
  new-session -s single-session  "julia runshort.jl ; read" \; \
  split-window "julia runshort.jl ; read" \; \
  split-window "julia runshort.jl ; read" \; \
  split-window "julia runshort.jl ; read" \; \
  select-layout even-vertical \; \
  detach
