# Local model setup — deferred

Nothing here downloads a model or connects it to Prysm. Keep using the existing Gemini key for general-knowledge assistance; private evidence summaries already work offline.

You need model **weights**, not a pasted Python codebase. Later, install [Ollama for Windows](https://docs.ollama.com/windows). Put a compatible, instruction-tuned GGUF file at:

```text
chatbot/local_llm/weights/model.gguf
```

The weights directory is ignored by Git. Do not put weights in `rag/knowledge_base/`. No specific model size has been selected: hardware inspection was unavailable, and RAM/VRAM must be checked before downloading. Choose a runtime-supported instruction model and a quantization that fits the machine; retain its model card, license and checksum.

After you have downloaded the file, these commands import and test it locally:

```powershell
cd chatbot/local_llm
ollama create prysm-local -f Modelfile.example
ollama run prysm-local "Return JSON with a summary explaining that an investigation lead is not proof."
```

Importing an existing GGUF with `FROM ./weights/model.gguf` follows the [Ollama import guide](https://docs.ollama.com/import) and [Modelfile reference](https://docs.ollama.com/modelfile). Choose a supported architecture; some models also need their documented chat template. The import may require additional disk space.

Later integration will add a local provider behind `reasoning.explain`, point it at the loopback Ollama service, and validate structured citations against the supplied evidence. Copying weights alone does **not** enable that integration. Local inference and its hardware performance are deliberately untested in Phase 4.
