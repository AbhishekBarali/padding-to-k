# POST HOC: minItems >= 2 on lists in real-world JSON Schemas (JSONSchemaBench)

POST HOC: not in the registered plan. Source: `analysis/posthoc/schema_prevalence.py`.

Data: `epfl-dlab/JSONSchemaBench` at revision `5bd0f4640badc6f3f02df796421d21cb0ca0b141` (licence MIT), ten subsets, train + val + test.

Reproduce (from the repository root; downloads about 21 MB into the gitignored `analysis/posthoc/cache/`):

```
uv run --no-project --python 3.12 --with pyarrow==26.0.0 python analysis/posthoc/schema_prevalence.py
```

## Summary

Of 9,542 schemas, 49.9% contain at least one array. 8.4% have an open array with minItems >= 1 (7.7% one whose items are strings or objects). 0.5% have an open (not fixed-length, not tuple) array with minItems >= 2, and 0.3% one with minItems >= 3. 0.3% of all schemas have such an array whose items are strings or objects (a list of things), 50.0% of the schemas with one; 0.2% have one with number or integer items (vectors, ranges, coordinates). (48 schemas; 24 with string or object items.) Fixed-length arrays (minItems == maxItems >= 2) occur in 0.8% of schemas and tuple arrays with minItems >= 2 in 0.0%; neither is counted above. 0 schemas failed to parse.

## Per subset (% of schemas)

| Subset | Schemas | Parse fail | Any array | min>=2 open | min>=3 open | min>=2 str/obj | min>=2 num | of which str/obj | fixed min>=2 | tuple min>=2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Github_trivial | 444 | 0 | 17.6 | 0.9 | 0.9 | 0.0 | 0.7 | 0.0 | 0.5 | 0.0 |
| Github_easy | 1,938 | 0 | 33.4 | 0.7 | 0.2 | 0.4 | 0.3 | 61.5 | 0.8 | 0.0 |
| Github_medium | 1,969 | 0 | 57.4 | 0.7 | 0.4 | 0.3 | 0.4 | 46.2 | 1.5 | 0.1 |
| Github_hard | 1,236 | 0 | 78.8 | 0.7 | 0.3 | 0.5 | 0.2 | 66.7 | 1.5 | 0.0 |
| Github_ultra | 164 | 0 | 95.7 | 3.0 | 3.0 | 1.8 | 1.2 | 60.0 | 6.1 | 0.0 |
| Glaiveai2K | 1,707 | 0 | 29.1 | 0.0 | 0.0 | 0.0 | 0.0 | - | 0.0 | 0.0 |
| JsonSchemaStore | 492 | 0 | 88.8 | 0.8 | 0.4 | 0.2 | 0.4 | 25.0 | 1.0 | 0.0 |
| Kubernetes | 1,064 | 0 | 60.8 | 0.0 | 0.0 | 0.0 | 0.0 | - | 0.0 | 0.0 |
| Snowplow | 403 | 0 | 33.7 | 0.0 | 0.0 | 0.0 | 0.0 | - | 0.0 | 0.0 |
| WashingtonPost | 125 | 0 | 48.8 | 0.0 | 0.0 | 0.0 | 0.0 | - | 0.0 | 0.0 |
| All | 9,542 | 0 | 49.9 | 0.5 | 0.3 | 0.3 | 0.2 | 50.0 | 0.8 | 0.0 |

## Arrays (all subsets)

40,039 array schemas: 39,726 open, 312 fixed-length, 1 tuple. Open arrays with minItems >= 2: 371 (31 string/object items, 329 number/integer, 11 other); with minItems >= 3: 190.

minItems on open arrays: 0: 826, 1: 1,994, 2: 181, 3: 16, 4: 172, 10: 1, 600: 1

## Examples of qualifying arrays

| Subset | Path | minItems | maxItems | Item type | Description |
|---|---|---:|---:|---|---|
| Github_easy | `/allOf/0/oneOf/1/properties/from` | 2 |  | object | Who is the email from? Can be multiple people. |
| Github_medium | `/properties/players` | 2 |  | string | List of all players in the game |
| Github_hard | `/definitions/shortcutsArray/items` | 2 | 4 | string |  |
| Github_ultra | `/definitions/BoundaryType/properties/Points` | 3 |  | object |  |
| JsonSchemaStore | `/definitions/parallel_steps` | 2 |  | object | Set of steps to run concurrently |
| Github_trivial | `/` | 4 |  | number | A GeoJSON object MAY have a member named 'bbox' to include information on the coordinate r |
| Github_easy | `/properties/grades` | 2 | 5 | number |  |
| Github_medium | `/definitions/position` | 2 |  | number | A position is the fundamental geometry construct. The `coordinates` member of a geometry o |
| Github_hard | `/definitions/pixel_walk_record/properties/n/oneOf/1` | 2 |  | number |  |
| Github_ultra | `/definitions/curve/properties/ControlPoints` | 4 |  | number_array | Specifies the value of ControlPoints used in this Curve module. |
| JsonSchemaStore | `/oneOf/0/properties/coordinates` | 2 |  | number |  |
| Github_easy | `/properties/pokemon` | 600 |  | object |  |
| Github_medium | `/properties/interests` | 3 | 100 | string |  |
| Github_hard | `/properties/Cliques/items` | 2 | 4 | string | Specifies a set of 2-4 terrain types for which a corner Wang tileset will be generated. |
| Github_ultra | `/definitions/LineType/properties/Points` | 2 |  | object |  |

## Caveats

- Duplicates: 338 schema texts occur more than once (733 rows; 4 of the texts across subsets). Deduplicated by exact text, 9,147 schemas, of which 0.5% have an open array with minItems >= 2 (0.3% string/object).
- Walker coverage: 126 schemas have an integer minItems >= 2 on some object anywhere in their JSON; the walker reaches one in all but 5 (those sit under non-schema keywords, or the minItems is on a node that is not an array schema).
- Arrays under $defs/definitions are counted whether or not the schema references them.
- Item types follow local $refs only; an external $ref counts as unspecified ("other").
- The dataset dropped a few very long Github schemas on 2025-03-31 (see its card); this is the pinned revision after that change.
