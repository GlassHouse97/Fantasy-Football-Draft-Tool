# ADP Market Quality Report — 2026-08-24

Status: **FantasyPros aggregate loaded, normalized, rebuilt, and audited successfully**

## Current FantasyPros aggregate capture

The manually downloaded FantasyPros **Overall ADP** CSV was captured at
**2026-08-24 18:25:05 UTC**. Its exact original bytes are preserved with SHA-256:

```text
9402d970666b6677aba3368fd69d6d8adecba360c8f55bce7dc44e2e7464a52d
```

The supported file contract is:

```text
Rank, Player (Bye), POS, Yahoo, Sleeper, RTSports, AVG
```

FantasyPros also supplied `Real-Time`; it remains in the immutable original bytes but is not one of
the requested platform/composite observations and is ignored by normalization.

Selecting the valid file at the bottom of **Player Evaluation → Player Export List** immediately
validates, archives, imports, and refreshes the table. There is no separate preview or confirmation
action. Re-selecting the identical file reused the existing immutable archive rather than creating
duplicate raw evidence.

The user authenticates and downloads the CSV in their own browser. The application does not store
FantasyPros credentials or cookies and does not automate login or export acquisition.

## Four immutable overall snapshots

| Source snapshot | CSV column | Source rows | Mapped | Unresolved | Player Export coverage |
|---|---|---:|---:|---:|---:|
| Yahoo | `Yahoo` | 222 | 185 | 37 | 165 |
| Sleeper | `Sleeper` | 302 | 244 | 58 | 228 |
| RTSports | `RTSports` | 328 | 280 | 48 | 258 |
| FantasyPros | `AVG` | 370 | 299 | 71 | 276 |

The FantasyPros value is the exported `AVG` composite; the application does not recompute it from
Yahoo, Sleeper, and RTSports. Board coverage is the accepted current-player coverage reported by
Player Export and is intentionally reported separately from source-row identity counts.

Identity remains conservative. Exact or uniquely supported evidence can map a player; ambiguous
rows retain their source identity and remain unresolved. A display name alone never becomes an
unqualified canonical join, and missing values remain blank rather than becoming zero.

## Current Player Export result

The verified board contains:

- 1,368 current projected or accepted market-only players;
- 276 players with at least one displayed market value;
- 927 displayed platform observations; and
- 165 complete Yahoo/Sleeper/RTSports/FantasyPros comparisons.

**Experimental Model Rank** uses the same health-neutral projection and replacement-value ranking
as Draft Assistant under the default 12-team full-PPR **Standard** roster: 1 QB, 2 RB, 2 WR, 1 TE,
1 FLEX, and 7 bench spots, with no K/DST. It is secondary to the FantasyPros-derived **Consensus
Rank**. Market-only players without a supported projection may have a blank model rank; the
application does not manufacture one.

## Deterministic Phase 5 rebuild and audit

After the aggregate import, the deterministic Phase 5 rebuild produced:

| Evidence | Rows |
|---|---:|
| Production ADP snapshots | 6 |
| ADP observations | 2,795 |
| Movement features | 2,795 |
| Movement forecasts | 8,385 |
| Availability parameters | 2,795 |

The post-rebuild data audit passed across **15 manifests** and **19 verified immutable files**.

## Earlier direct-source evidence

The aggregate snapshots supplement rather than erase the earlier immutable evidence:

| Evidence | Captured at (UTC) | Rows | SHA-256 |
|---|---:|---:|---|
| nflverse fantasy-platform ID crosswalk | 2026-08-24 15:55:32 | 12,480 | `a0c83c64f6f1ab1f8d4b15d1e2794e32e7c3fba94fb34079ef68fe2f6d8ce7bf` |
| Direct Sleeper 2026 full-PPR response | 2026-08-24 15:55:43 | 3,112 raw / 1,327 usable | `ab20e688b5397adf738b64c3a52c780076d71ea3167caf0d0ebe812832f8b1df` |

The direct Sleeper capture mapped 869 rows exactly and 70 through one conservative unique current
name/position/team match; 388 remained unresolved. Its successful idempotence replay inserted zero
rows and matched all 1,327 existing observations. These are historical direct-capture facts and are
not substituted for the newer aggregate snapshot counts above.

## Local verification

```powershell
fantasy-draft data audit
fantasy-draft status
```

For a later dated market refresh, manually download a new complete FantasyPros Overall ADP CSV and
select it at the bottom of Player Export List. Because selection imports immediately, do not select
a shortened test file as the active source-of-truth export.
