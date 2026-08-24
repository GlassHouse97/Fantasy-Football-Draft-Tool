# Player Evaluation Milestones

## Product goal

Player Evaluation is a player-first reference workspace. It keeps four different kinds of
evidence separate:

1. platform draft cost (ADP);
2. model projection and ranking;
3. creator opinion; and
4. current news, which is not yet integrated.

The workspace must never turn missing evidence into a neutral or zero value.

## Milestone 1 — Player Export List

The first page is implemented as a complete export over the active 2026 projection board plus
current-season canonical players present only in an accepted market snapshot. It contains explicit
ESPN, Yahoo, Sleeper, and Underdog columns, a composite mean over only non-missing values, and a
source-count column. It also reports the scoring/contest context for every platform because
Underdog best-ball ADP is not directly equivalent to redraft ADP.

The August 24, 2026 milestone archived Sleeper's full-PPR response and nflverse's platform-ID
crosswalk, then loaded both through immutable, idempotent contracts. Player Export now shows 939
canonically linked Sleeper observations across a 1,612-player projection-or-market universe. ESPN,
Yahoo, and Underdog remain blank until an authorized export is supplied. Display-name matching
alone is never accepted: exact platform IDs, one unique current name + position + team match, or a
reviewed override are required.

The current source and mapping evidence is recorded in
[the dated ADP quality report](ADP_MARKET_QUALITY_REPORT_2026-08-24.md). The next acquisition
increment is one authorized multi-site export. ADPWire currently advertises a paid CSV/XLSX with
all four requested platform columns; the actual file must be obtained and inspected before a
provider-specific importer is claimed.

## Milestone 2 — Player Market Consensus

The second page is implemented as an evidence-gated player-first shell. Its first registered
source is [Fantasy Football Advice](https://www.youtube.com/@FantasyFootballAdviceFFA/videos),
scoped to videos published on or after January 1, 2026. No creator stance is displayed until the
underlying corpus is built and validated.

The ingestion and analysis contract is:

1. archive a complete in-scope channel video inventory;
2. acquire available transcripts with video and caption provenance;
3. report videos without usable transcripts as coverage gaps;
4. resolve mentions to canonical players using IDs, full names, and reviewed aliases;
5. retain the video, timestamp range, and matched surface form for every mention;
6. aggregate all in-scope evidence into one player/creator stance;
7. publish stance, confidence, summary, video count, mention count, latest evidence date, and
   evidence links; and
8. human-review a sample before declaring the corpus useful.

The initial alias registry includes `JSN` for Jaxon Smith-Njigba. It is configuration, not proof
that every occurrence of the letters refers to that player; context validation remains required.

The official YouTube captions API requires authorization, and downloading a caption track requires
permission to edit the video. That makes it unsuitable for downloading a third-party channel's
public transcripts through the official API. Milestone 2 must therefore settle a permitted and
reliable transcript-acquisition method, preserve provenance, and fail visibly when captions are
unavailable before any summarization work begins.
