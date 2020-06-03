#!/bin/bash

tmux \
  new-session -s single-session  "julia runshort.jl" \; \
  split-window "julia runshort.jl" \; \
  split-window "julia runshort.jl" \; \
  split-window "julia runshort.jl" \; \
  select-layout even-vertical \; \
  detach
