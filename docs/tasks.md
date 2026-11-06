# Capability Registry

The five capabilities are declared in `deckforge/tasks/registry.py`:

| id | capability | metrics |
|---|---|---|
| `layout` | Layout placement (coding stage) | `layout_acc` |
| `design` | Design specification (design stage) | `design_acc` |
| `completion` | Closed-loop completion | `deck_success` |
| `reward` | Verifiable reward | `score` |
| `repair` | Checked repair harness | `repair_gain` |

Query them programmatically:

```python
from deckforge.tasks import list_tasks, get_task

for t in list_tasks():
    print(t["id"], t["name"], t["metrics"])
```
