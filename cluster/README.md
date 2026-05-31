# Cluster submission scripts

Submission scripts for running the zipper-algebra pipeline on UCSB's knot cluster (SLURM).

## Workflow

1. **Anchor run** — one expensive `SGrobnerTrace` at a chosen (Q, T, PSTR) point. Produces a saved traced basis file.
2. **Replay sweep** — one cheap job that runs `trace_replay.gap`, which iterates internally over its `samples` list (linear-solve replays using the anchor's trace structure). The `samples` list inside `trace_replay.gap` is the one place to edit when adding evaluation points.

## Files

| File | Purpose |
|---|---|
| `zipper_n4_traced.sbatch` | Anchor SGrobnerTrace on `batch` (46 GB). First attempt. |
| `zipper_n4_traced_largemem.sbatch` | Same, on `largemem` (800 GB). Fallback if `batch` OOMs. |
| `zipper_replay.sbatch` | Runs `trace_replay.gap` against an anchor file. |

## Anchor run

```bash
# Traced bigelow n=4 anchor at q=5, t=7, p=2^31-1 — the heavy job
sbatch --export=ALL,TRACED=true cluster/zipper_n4_traced.sbatch

# Override params
sbatch --export=ALL,TRACED=true,N=4,Q=7,T=11 cluster/zipper_n4_traced.sbatch
```

Default env values (when unset): `N=3, Q=5, T=7, PSTR=2^31-1, UNTWIST=bigelow, TRACED=false`. Explicitly setting `TRACED=true` is required for an anchor run.

## Replay sweep

Edit `samples` inside `../trace_replay.gap` to add/remove evaluation points, commit, then:

```bash
sbatch --export=ALL,ANCHOR_FILE=logs_and_traces/grobner_zipper_bigelow-trace-4-\(2^31-1\)-5-7.gap \
       cluster/zipper_replay.sbatch
```

If `ANCHOR_FILE` is omitted, `trace_replay.gap` falls back to its hard-coded default path.

## Monitoring

```bash
squeue -u $USER
sstat -j JOBID --format=JobID,MaxRSS,AveRSS --noheader
sacct -j JOBID --format=JobID,State,Elapsed,MaxRSS,ReqMem,ExitCode
tail -f logs_and_traces/logfile_zipper_bigelow-traced-4-\(2^31-1\)-5-7.txt
scancel JOBID
```

## Before submitting

1. Edit `--mail-user=YOUR_EMAIL@ucsb.edu` in each `.sbatch` (or delete the `mail-*` lines).
2. Confirm `gap` is on `PATH` (`~/.bashrc` should have `export PATH="$HOME/gap-4.15.1:$PATH"`).
3. Parameters consumed from environment:
   - `zipper.gap`: `N`, `Q`, `T`, `PSTR`, `UNTWIST`, `S`, `TRACED`
   - `trace_replay.gap`: `ANCHOR_FILE`
