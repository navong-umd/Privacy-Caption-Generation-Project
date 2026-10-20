# Third-party material

The code in this repository is MIT-licensed (see `LICENSE`). The items below come from other sources and keep their original terms.

## SuSi Android source and sink lists

`data/knowledge_base/CatSources_v0_9.txt`, `data/knowledge_base/CatSinks_v0_9.txt`, and the parsed `formatted_sources.csv` / `formatted_sinks.csv` derived from them come from SuSi:

> S. Rasthofer, S. Arzt, and E. Bodden. "A Machine-learning Approach for Classifying and Categorizing Android Sources and Sinks." NDSS 2014. https://github.com/secure-software-engineering/SuSi

The upstream repository does not publish a license file.
<!-- TODO(Ali): confirm with the SuSi authors or the PI that redistributing these lists is acceptable. -->

## Android API documentation

`data/knowledge_base/personal_info_results.csv` was produced by the legacy document-analysis scripts (`legacy/document_analysis/`) from public Android API reference descriptions.

## APKs and decompiled code

No APKs or decompiled application code are distributed here. Real-app runs fetch APKs locally from AndroZoo (https://androzoo.uni.lu, subject to its access terms) or F-Droid with the fetchers in `adapters/`. Outputs derived from proprietary apps stay in the gitignored `data/` folder.
