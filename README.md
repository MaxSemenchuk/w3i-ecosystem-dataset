# W3I Ecosystem Dataset

A relational map of Ukraine's Web3, academic and public-sector network: organizations, people (name and affiliation only), projects, topic tags, and a catalogue of materials published by the Web3 Institute (W3I). Open data (CC BY 4.0) with a data dictionary, reproducible analysis scripts and an accompanying data paper.

- **Paper:** [paper/dataset-paper.md](paper/dataset-paper.md) (PDF in the release)
- **Data:** [data/json](data/json) and [data/csv](data/csv)
- **Dictionary:** [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md)
- **Analysis:** [analysis/](analysis/README.md)

## What is inside

| File | Records | Content |
|---|---|---|
| `organizations` | 831 | name, sector, country, website, aliases, description, tag ids |
| `people` | 644 | name and links to organizations, projects and tags. Nothing else |
| `projects` | 50 | name, type, website, description, linked organizations, related projects, tag ids |
| `tags` | 45 | topic labels and categories |
| `materials` | 50 | reports, talks and articles published on w3i.network: title, date, topics, excerpt, links |

Relations are `*_ids` arrays pointing to the `id` of another file (`organization_ids` → `organizations`). In CSV they are `;`-separated.

```python
import pandas as pd
orgs = pd.read_json("data/json/organizations.json").set_index("id")
people = pd.read_json("data/json/people.json")
```

## Scope and limits

This is the network **visible to W3I**, built from forums, programmes and partner lists since 2023. It is not a census of the ecosystem. Sectors are assigned by W3I, there is no time dimension, and attributes such as country or description are incomplete. See section 4 of the paper.

## Privacy

- The data is a subset of what is already shown on the public W3I Explore map ([w3i.network](https://w3i.network)).
- **People:** only the name and professional affiliations are released. No biographies, locations, profile links, contact details or other attributes. A person appears only if at least one organization is recorded for them.
- People who registered for W3I services are not included. No emails, phone numbers, messenger handles or wallet addresses are published anywhere in this dataset.
- **Remove or correct a record:** write to support@w3i.network or open an issue using the removal template. Records are removed in the next release; older versions remain in the archive, so request removal early.

## Cite

See [CITATION.cff](CITATION.cff). Data: [CC BY 4.0](LICENSE). Code in `analysis/`: MIT ([LICENSE-CODE](LICENSE-CODE)).
