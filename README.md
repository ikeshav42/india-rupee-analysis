# india-rupee-analysis

Data and code for the article: [Why Is Everything Getting More Expensive in India When the Headlines Say the Economy Is Doing Great?](https://medium.com/@ikeshav42/why-is-everything-getting-more-expensive-in-india-when-the-headlines-say-the-economy-is-doing-great-80c9f1bf532c)

`src/fetch_india.py` pulls data from FRED and the World Bank API into `data/processed/`. `src/viz_india.py` generates the charts.

LPG prices and gold duty history in the CSVs are hand-collected from PPAC and Ministry of Finance budget docs since there's no clean API for those.
