# "Require this computer" for the four Ledger tasks

Why: the four Ledger tasks were created by Claude through the scheduling API, so they run in the cloud, where Sean's
Chrome is not reachable (their last runs said "Chrome not connected"). They must run on Sean's Mac with the
Claude desktop app open.

Known limit: for a task created by an agent, the "Require this computer" toggle in the task's edit dialog is greyed
out with the tooltip "To require this computer, create a new scheduled task." So each task is recreated by hand.

## Steps (on Sean's Mac, Claude desktop app, signed in as Sean)
1. Settings > Desktop app > General: turn on "Keep computer awake" (a sleeping Mac skips the run; closing the lid
   still sleeps it).
2. Left sidebar: "Scheduled". The list shows the four tasks named "Ledger: ...".
3. For each task below: open it, copy its instructions (the prompt) to the clipboard, then go back to the list and
   click "+ New task".
4. In the new task: Name = the same name; Instructions = paste; Frequency = Daily at the time below (US Eastern);
   permissions = the automatic approval option (a run that waits for approval does nothing overnight); turn ON
   "Require this computer (Claude Desktop (macOS))". Save.
5. Open the old task and pause it (toggle off), so the cloud copy does not also run. Delete it once the new one has
   run once.
6. Check: the new task shows the grey "Requires this computer" badge.

| Task | Daily time (ET) |
|---|---|
| Ledger: trade reports | 8:03 AM |
| Ledger: contract terms and QO decisions | 8:17 AM |
| Ledger: share pages for new moves | 8:41 AM |
| Ledger: drafted posts for big moves | 8:57 AM |

The full instructions for each task are in each old task (step 3); Claude can also paste them on request.
