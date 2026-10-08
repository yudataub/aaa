#!/bin/bash
cd /home/user/aaa
python3 -m http.server 8765 >/tmp/http.log 2>&1 &
SP=$!
sleep 1
W=/tmp/claude-0/-home-user-aaa/bf25bffc-af4e-5f9d-9c53-c58411494098/scratchpad/work
cd $W
export NODE_PATH=$(npm root -g)
node idx.js
node all.js
kill $SP 2>/dev/null
