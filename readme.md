# nagomi-statements

Stateless gRPC service that parses bank statement PDFs for [nagomi-core](https://github.com/xhos/nagomi-core). It returns the account, statement period and transaction lines, and writes nothing anywhere; core stores the file and imports the lines.

Supported: RBC chequing, savings and Visa. Parsing rules are ported from [andrewscwei/rbc-statement-parser](https://github.com/andrewscwei/rbc-statement-parser) (MIT).

## Config

| env | default |
|---|---|
| `LISTEN_ADDRESS` | `127.0.0.1:55559` |
| `LOG_LEVEL` | `info` |
| `LOG_FORMAT` | text, or `json` |

## Dev

```bash
run      # hot-reloading server
pytest   # tests build synthetic PDFs, no real statements needed
regen    # regenerate src/nagomi from proto/
fmt
```

Adding a bank: a module in `src/nagomi_statements/parsers/` with `detect` and `parse`, registered in `parsers/__init__.py`.
