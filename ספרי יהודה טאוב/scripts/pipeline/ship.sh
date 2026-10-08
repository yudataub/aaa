#!/bin/bash
# usage: ship.sh "commit message"
cd /home/user/aaa
git add -A
git commit -q -m "$1

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MWY9gAXPxkt5oTb1qR7QCi" || exit 1
git fetch -q origin main
if ! git merge-base --is-ancestor origin/main HEAD; then
  if ! git merge origin/main -m "Merge main" >/tmp/merge.log 2>&1; then
    U=$(git diff --name-only --diff-filter=U)
    echo "CONFLICTS: $U"
    if [ "$U" = "ספרי יהודה טאוב/שיעורי יוטיוב/lessons.json" ]; then
      git checkout --theirs "ספרי יהודה טאוב/שיעורי יוטיוב/lessons.json"
      W=/tmp/claude-0/-home-user-aaa/bf25bffc-af4e-5f9d-9c53-c58411494098/scratchpad/work
      python3 $W/reapply_lessons.py || exit 2
      git add "ספרי יהודה טאוב/שיעורי יוטיוב/lessons.json"
      git commit -q -m "Merge main; re-apply lesson entries

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MWY9gAXPxkt5oTb1qR7QCi"
    else exit 3; fi
  fi
fi
git push -u origin claude/bold-hopper-jrpef6 2>&1 | tail -1
