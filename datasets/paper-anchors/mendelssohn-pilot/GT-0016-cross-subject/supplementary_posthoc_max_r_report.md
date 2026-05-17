# Supplementary: post-hoc max-r window inflation

This reports the maximum Pearson r (and Spearman ρ) found by scanning
ALL ~854 possible 80-TR windows in each subject's BOLD, correlated against
MI-RAM amygdala/PMC. This is the upper-bound selection-inflated correlation:
it matches GT-0016's sub-08 TR=556 +0.5906 as the argmax.

**N subjects with valid BOLD:** 17

## Cross-subject distribution of post-hoc max-r

| Predictor | Median | IQR | Max (best subject) | Min (worst) |
|---|---:|:---:|---:|---:|
| max MI amygdala Pearson r | +0.5904 | [+0.5465, +0.6409] | +0.7550 | +0.5025 |
| max MI amygdala Spearman ρ | +0.6227 | [+0.5686, +0.6335] | +0.6930 | +0.4642 |
| max MI PMC Pearson r | +0.5487 | [+0.4385, +0.7457] | +0.7834 | +0.3616 |
| max MI PMC Spearman ρ | +0.5594 | [+0.3996, +0.6646] | +0.7328 | +0.3388 |

## Selection inflation (diagnostic)

Comparison of the post-hoc max-r median here with the sliding-window-anchored
median in `cross_subject_headtohead.csv` tells us how much the paper's
+0.5906 for sub-08 was inflated by window selection. If median max-r ≫
median anchor-r, the paper's N=1 finding is dominated by selection bias.

## Per-subject detail

| Subject | max amyg r | tr_start | max ρ | max PMC r | PMC tr | PMC ρ |
|---|---:|---:|---:|---:|---:|---:|
| sub-01 | +0.6658 | 0 | +0.6335 | +0.3616 | 454 | +0.3747 |
| sub-02 | +0.6228 | 68 | +0.6230 | +0.4169 | 654 | +0.3796 |
| sub-03 | +0.5913 | 0 | +0.5686 | +0.3746 | 671 | +0.3578 |
| sub-05 | +0.5854 | 495 | +0.5885 | +0.6559 | 716 | +0.6556 |
| sub-06 | +0.5434 | 42 | +0.5586 | +0.7707 | 33 | +0.7023 |
| sub-07 | +0.5235 | 490 | +0.6289 | +0.5487 | 768 | +0.4831 |
| sub-08 | +0.5904 | 556 | +0.5420 | +0.4679 | 756 | +0.4392 |
| sub-09 | +0.5826 | 837 | +0.6101 | +0.7585 | 753 | +0.7183 |
| sub-11 | +0.5655 | 360 | +0.6317 | +0.6623 | 156 | +0.6316 |
| sub-12 | +0.7295 | 39 | +0.6668 | +0.7834 | 760 | +0.7145 |
| sub-13 | +0.6385 | 175 | +0.6390 | +0.3923 | 103 | +0.3388 |
| sub-14 | +0.6634 | 457 | +0.6890 | +0.7457 | 457 | +0.6518 |
| sub-15 | +0.5373 | 548 | +0.5699 | +0.5259 | 302 | +0.5594 |
| sub-17 | +0.7550 | 709 | +0.6930 | +0.6186 | 193 | +0.6646 |
| sub-18 | +0.5025 | 475 | +0.4642 | +0.4385 | 786 | +0.3996 |
| sub-19 | +0.5465 | 363 | +0.4964 | +0.4869 | 133 | +0.4331 |
| sub-20 | +0.6409 | 296 | +0.6227 | +0.7670 | 493 | +0.7328 |