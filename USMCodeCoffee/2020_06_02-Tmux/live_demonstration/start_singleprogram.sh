#!/bin/bash
tmux new-session -d -s my_session01 'julia run.jl'
tmux new-session -d -s my_session02 'julia run.jl'
