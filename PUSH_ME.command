#!/bin/zsh
# Front Office Ledger: one-click push. Uses YOUR Mac's GitHub login; no tokens involved.
cd "$(dirname "$0")"
git branch -M main
git push -u origin main
echo ""
echo "Done. Repo: https://github.com/szerillo/front-office-ledger"
echo "Next: GitHub Settings -> Pages -> deploy from main, folder /prototype"
read -k 1 "?Press any key to close..."
