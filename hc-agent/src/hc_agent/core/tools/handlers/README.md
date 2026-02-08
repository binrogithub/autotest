# Handler Specification

Handlers implement cloud service operations for hc-agent.

## Requirements

- Support `preview` and `apply` modes
- Do not perform side effects in preview mode
- Return structured output:
  - summary
  - result
  - evidence

## Responsibilities

Handlers are responsible for:
- Building request specifications
- Invoking HTTP execution
- Parsing minimal result identifiers

Handlers must not:
- Store execution artifacts
- Prompt for user input
- Perform policy or approval checks

All handlers are executed through the unified runner.
