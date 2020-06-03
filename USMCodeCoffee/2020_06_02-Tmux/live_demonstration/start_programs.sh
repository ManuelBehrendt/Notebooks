#!/bin/bash

tmux \
  new-session -s single-session  "julia run.jl ; read" \; \
  split-window "julia run.jl ; read" \; \
  split-window "julia run.jl ; read" \; \
  split-window "julia run.jl ; read" \; \
  select-layout even-vertical \; \
  detach
