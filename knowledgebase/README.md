# Knowledge Base

Structured astrology reference content for the AstroGuruAI Knowledge Brain, report generator, and rule engines.

Generated JSON is produced by:

```bash
python -m knowledge_brain.builders.build_all
```

## Structure

```
knowledgebase/
├── manifest.json
├── vedic/
│   ├── planets.json          # 9 grahas
│   ├── houses.json           # 12 bhavas
│   ├── signs.json            # 12 rashis
│   ├── nakshatras.json       # 27 nakshatras
│   ├── padas.json            # 108 padas
│   └── combinations.json     # planet-house/sign combinations
├── domains/
│   ├── marriage_rules.json   # 300+ marriage rules
│   ├── career_rules.json     # 300+ career rules
│   ├── health_rules.json
│   └── finance_rules.json
├── lal_kitab/
│   ├── rin.json
│   ├── dosh.json
│   ├── remedies.json
│   └── planet_house.json
└── kp/
    ├── event_rules.json
    ├── significator_rules.json
    ├── star_lord_rules.json
    └── sub_lord_rules.json
```

## Usage

Load and search via the `knowledge_brain` package:

```python
from knowledge_brain import KnowledgeQuery, KnowledgeRegistry, KnowledgeSearchEngine
from knowledge_brain.loader import KnowledgeLoader

registry = KnowledgeRegistry(KnowledgeLoader("knowledgebase"))
engine = KnowledgeSearchEngine(registry)
result = engine.search_json(KnowledgeQuery(problem_text="delay in marriage", domain="marriage"))
```

No business logic lives in this directory — only static JSON knowledge files.
