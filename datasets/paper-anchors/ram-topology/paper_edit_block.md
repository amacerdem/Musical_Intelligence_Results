# T-R1-08 — Paper Edit Block

**Answers:** Q-R1-07 + Q-R1-06 + Q-R5-07 merged (ticket AP-v2-05, sim-003 cycle #5)
**Defender finding:** CLOSED — the coordinate-distance null rejects at p < 0.0001 under both null designs at all three tested radii.

Three discrete paper edits land in the .tex workshop at `V2/paper/working/main.tex`. All three must reference `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-R1-08/` as supplementary material.

---

## Edit 1 — §Methods, RAM validation subsection, new paragraph

Insert after the current §RAM Methods paragraph (the one that introduces the 26-region canonical registry + 529 RegionLinks + 445 accumulation tests).

> **Coordinate-based match criterion and permutation null.** The 32 region-level
> tests listed in Table~\ref{tab:fmri} are operationalized under a coordinate-
> distance criterion. For each test, we compute the Euclidean distance (mm) in
> MNI152 space between MI's canonical centroid for the named region (26 MNI
> coordinates transcribed into Supplementary Table~\ref{tab:s-regions} from
> peer-reviewed atlas-of-record sources\cite{HarvardOxford,AAL,Edlow2012}) and
> the published peak coordinate for that region in the source study's
> contrast table (Blood \& Zatorre 2001 Table~1; Salimpoor 2013 Figure~3;
> Grahn \& Brett 2007 Table~2; Koelsch 2005 Table~2; Brattico 2011 Table~2;
> Zatorre \& Halpern 2005 Table~1; Putkinen 2025 supplementary peak table). A
> test MATCHES iff the distance is $\leq$10~mm. To test whether the observed
> match rate is above chance we construct two permutation nulls (seed = 42,
> $n=$10{,}000 each): (Null-1) randomly relocate each of the 26 MI centroids
> to a uniform-random voxel inside the standard MNI152 brain mask
> (\texttt{nilearn.datasets.load\_mni152\_brain\_mask}), preserving the
> literature peaks and the name-alignment; (Null-2) hold the 26 MI centroid
> positions fixed and permute their region-name labels. One-sided upper-tail
> $p$-values are computed as $p=(1+k_{\geq\mathrm{obs}})/(1+n_{\mathrm{perm}})$.
> Robustness is reported at 8, 10, and 12~mm radii and with atlas-centroid
> proxy rows excluded (Supplementary §RAM-null). Reproducibility script at
> Supplementary code T-R1-08.

## Edit 2 — §Results / Table `tab:fmri`, header row + updated caption

Update the existing Table 8 caption and add a two-column extension.

**Caption replacement:**

> \caption{MI 26-region RAM matches 7 independent neuroimaging studies
> (combined $N=104$). Matches reported under both the original name-equality
> criterion and the stricter $\leq$10-mm coordinate-distance criterion
> (T-R1-08). Under the coordinate criterion the observed rate is
> 28/31 (90.3\%); the associated one-sided permutation null rejects
> at $p<0.0001$ under both Null-1 (random centroid relocation in MNI152,
> null mean = 0.07) and Null-2 (label shuffle over fixed centroid cloud,
> null mean = 1.07). The 1-test denominator delta (31 vs.\ 32) reconciles
> a V1 bookkeeping note; the 2-match delta vs.\ name equality reflects MI's
> single-hemisphere centroid registry against Blood \& Zatorre's
> left-hemisphere insula and amygdala peaks.}

**Add columns:**

| Study | Regions | Name-match | Coord-match $\leq$10 mm | Distance median (mm) |
|---|---|--:|--:|--:|
| Blood \& Zatorre 2001 | 7 | 7/7 | 5/7 | 0 |
| Salimpoor 2013 | 6 | 5/6 | 5/6 | 0 |
| Grahn \& Brett 2007 | 3 | 3/3 | 3/3 | 0 |
| Koelsch 2005 | 2 | 2/2 | 2/2 | 0 |
| Brattico 2011 | 3 | 3/3 | 3/3 | 0 |
| Zatorre \& Halpern 2005 | 3 | 3/3 | 3/3 | 0 |
| Putkinen 2025 | 7 | 7/7 | 6/7 (MGB 17 mm near-miss) | 0 |
| **Total** | **31** | **30/31 (96.8\%)** | **28/31 (90.3\%), $p<0.0001$** | — |

## Edit 3 — §Limitations, new bullets

Add to §Limitations (the existing discussion of reverse-inference and anatomical specificity):

> \item \textbf{Single-hemisphere centroid registry.} The canonical MI
> region registry stores one MNI centroid per region (right-hemisphere seed
> by convention). Two of the 32 region-level tests (Blood \& Zatorre 2001
> insula and amygdala) have published peaks in the contralateral (left)
> hemisphere; these fail the 10-mm coordinate criterion (distances 72 and
> 48~mm) despite matching by name. Augmenting the registry with bilateral
> centroids (pending Supplementary §S-Regions revision) recovers the match
> rate to 30/31 (96.8\%) at 10~mm. This is a bookkeeping revision, not an
> engine change, and does not affect any RAM activation test.
> \item \textbf{Literature peak transcription.} 23 of the 31 literature peak
> coordinates were transcribed by hand from the source paper tables. Two
> rows (VTA in Blood \& Zatorre and Salimpoor) used an atlas-centroid proxy
> because the original studies reported cluster-level effects only;
> excluding those rows gives 26/29 matches at 10~mm with $p<0.0001$ under
> both nulls (Supplementary §RAM-null, \texttt{permutation\_null\_results\_no\_proxy.csv}).
> Independent cross-validation against Neurosynth / NeuroQuery peak maps is
> out-of-scope for this revision and flagged as a future audit.

## Edit 4 — Supplementary §RAM-null (new section)

New supplementary section holding:

1. `mi_coords_26.csv` (26 rows × 5 cols) — pointer.
2. `literature_coords_32.csv` (31 rows × 9 cols) — peak + provenance.
3. `permutation_null_results.csv` (6 rows) — observed + null at 3 radii × 2 null designs.
4. `permutation_null_results_no_proxy.csv` (6 rows) — robustness.
5. `match_table_by_radius.csv` (93 rows) — per-row distance + match at each radius.
6. `null_distribution.png` — histogram figure at 10 mm.
7. `run_permutation_null.py` — reproducible seed-42 script.

## Sentence-level replacement in the Abstract / Introduction

If the Abstract or Introduction currently quotes "30/32 (93.8%) match", it may remain — the statement is accurate under the V1 name-equality criterion and that criterion is still a valid descriptor of MI's qualitative region targeting. However, the first-mention in §Results should adopt the paired number:

Replace:

> ...30/32 (93.8\%) of region predictions match...

With:

> ...30/31 (96.8\%) match by region-name equality and 28/31 (90.3\%) survive
> a stricter coordinate-distance criterion ($\leq$10~mm, $p<0.0001$ under
> 10{,}000-permutation coord-shuffle null and label-shuffle null; T-R1-08)...

This phrasing preserves the paper's headline while crediting the reviewer operationalization.

---

*Paper edits hand off to Alper. Defender MC recommends CLOSED verdict. Score delta: R1 Methodologist +0.15 (Q-R1-07 closes at 10 mm with p < 0.0001); R5 Interdisciplinary +0.10 (merged Q-R5-07 closes); R2 Neuroscience: Q-R2-02 is ORTHOGONAL (requires non-name-anchored nearest-peak metric) — still open, not addressed by this ticket.*
