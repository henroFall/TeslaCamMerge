#!/bin/bash

LOG1=./log/RemoveOld.log
LOG2=./log/LoadSSD.log
LOG3=./log/MergeTeslaCam.log

SESSION_NAME="logwatch"

tmux has-session -t "$SESSION_NAME" 2>/dev/null && tmux kill-session -t "$SESSION_NAME"

# Start with first tail and keep tmux alive even if it fails
tmux new-session -d -s "$SESSION_NAME" -n main "tail -f $LOG1 || sleep 600"
sleep 0.2

tmux split-window -v -t "$SESSION_NAME":0 "tail -f $LOG2 || sleep 600"
tmux split-window -v -t "$SESSION_NAME":0 "tail -f $LOG3 || sleep 600"
tmux split-window -v -t "$SESSION_NAME":0 \
  "echo 'Type q or exit to quit all logs:'; read input; [[ \$input == q || \$input == exit ]] && tmux kill-session -t $SESSION_NAME"

# Now resize the upper panes evenly to fill remaining space
# First select the first pane, then apply "even-vertical"
tmux select-pane -t "$SESSION_NAME":0.0
tmux select-layout -t "$SESSION_NAME":0 even-vertical

# Resize the prompt pane (bottom) to 3 lines
tmux resize-pane -t "$SESSION_NAME":0.3 -y 3
tmux select-pane -t "$SESSION_NAME":0.3

# Attach to the session
tmux attach-session -t "$SESSION_NAME"
