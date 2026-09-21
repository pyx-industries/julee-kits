# julee-polling

Polling for [julee](https://github.com/pyx-industries/julee) solutions:
watch an external endpoint and act when it has new data.

```toml
[tool.julee]
kits = ["polling"]
```

The kit provides:

- `PollingConfig`, the schedule and endpoint to watch.
- `PollerService`, `NewDataAnalyzer` and `PollingResultHandler` protocols.
- `HttpPollerService`, polling a REST endpoint.
- `PollDataUseCase`, and a Temporal pipeline that runs it durably.
