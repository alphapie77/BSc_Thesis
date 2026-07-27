# Dataset Card -- STUB (complete during Phase 1)

Follows Gebru et al. (2021) Datasheets for Datasets + Bender & Friedman (2018)
Data Statement.

- **Language (Bender Rule):** Bangla (Bengali), Bangladeshi variety, Bengali script.
- **Source:** Mendeley Data, "Raw Bangla Movie Review Comment Dataset..."
- **Size:** 5,000 rows x 2 columns (Movie Review, Sentiment).
- **HONEST NOTE (to verify in S0):** despite "Raw" in the title, the file appears
  partially pre-cleaned -- zero emoji, zero URLs/mentions. State this explicitly;
  it means the pre-defence report's emoji preprocessing tables do not describe
  this file.
- **Known absence:** no movie-title column -> reviews cannot be mapped to films
  -> a held-out-films split is impossible.
- **To add:** collection method, annotator demographics, licensing, gold-300 release.
