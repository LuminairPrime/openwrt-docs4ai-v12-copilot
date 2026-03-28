# AI Defect Discovery Pipeline: Architecture & Implementation Guide

This document is the master guide for operating the OpenWrt Defect Discovery Pipeline. Based on architectural feedback, we have decoupled the **Scenario Prompts** from the **Metadata (Test Logic)**. 

### Why this Architecture?
1. **Blind Testing:** By stripping the words "Test" and any Github source URLs from the prompt file, we guarantee the Generating AI cannot use meta-context to cheat. It must rely completely on its raw latency space. (However, the word "OpenWrt" and "snippet" intentionally remain to establish basic boundaries.)
2. **Dual-Workflow Support:** This architecture perfectly supports both manual copy/pasting and automated batch testing.

---

## 1. Directory Structure
The pipeline is physically deployed in this directory (`ai-defect-discovery-pipeline/`). Here is the layout and what each folder does:

```text
ai-defect-discovery-pipeline/
├── 04-pipeline-implementation-guide.md  <-- This instruction manual
├── scenarios/
│   ├── 01-batch-prompts.md              <-- PURE SCENARIOS ONLY. (No test logic, no links).
│   └── 02-metadata-catalog.json         <-- THE GROUND TRUTH. Contains intents, references, and expected paradigms.
├── scripts/
│   └── run_evaluator.py                 <-- Python automation harness to execute the whole pipeline.
└── results/                             <-- Folder where you should save your manual test outputs or where the Python script saves the JSON scoresheets.
```

---

## 2. The Testing Matrix (What we test and why)
The pipeline is populated with exactly 16 scenarios testing specific OpenWrt architectures. Below is the taxonomy of what these tests represent:

| Scenario | Domain Segment | Intent / "The Why" | Target Vulnerability |
| :--- | :--- | :--- | :--- |
| **01, 06** | Shell (`procd`) | Tests system initialization. AI must know `USE_PROCD` instead of writing `bash/systemd`. | `ERR_LINUX_HALLUCINATION` |
| **09, 10** | Shell (`hotplug`) | Tests OpenWrt standard `/etc/hotplug.d` and `/etc/uci-defaults` filesystem logic. | `ERR_LINUX_HALLUCINATION` |
| **02, 16** | Scripting (Implicit) | Tests if AI defaults to new `ucode` bindings (and `uloop` asynchronous handling) rather than clunky shell/Lua wrappers. | `ERR_LEGACY_API` |
| **08, 13** | Scripting (Explicit) | Tests explicitly if the AI actually knows `ucode` syntax. | `ERR_LEGACY_API` |
| **03, 07** | C Backend (`rpcd`) | Tests `libubus` daemon creation and secure `blobmsg` JSON return handling. | `ERR_MISSING_BOILERPLATE` |
| **12, 15** | C Backend (`libubox`) | Tests `uloop` event loop initialization and robust `blobmsg_parse` capabilities. | `ERR_NON_C_COMPLIANT` |
| **04, 05, 14** | JS Frontend (`LuCI`) | Tests `L.ui`, component hierarchies, and `rpc.declare` live data fetching. Prevents the AI from using Lua CBI. | `ERR_LEGACY_API` |
| **11** | Build System | Tests OpenWrt package top-level `Makefile` standards. | `ERR_MISSING_BOILERPLATE` |

---

## 3. Workflow A: Manual & Batch AI Testing (Copy/Paste)

If you are manually testing an AI in a chat interface (like running a prompt on me directly, or in the ChatGPT web UI):

1. **Batch Generation:** Open `scenarios/01-batch-prompts.md`. Read the whole file and paste it perfectly into the AI. The instructions at the top will force the AI to execute every scenario sequentially and output them clearly.
2. **Singular Generation:** Open `scenarios/01-batch-prompts.md`, copy just the text under `## Scenario 01`, and paste it into the AI chat. 
3. **Saving Results:** Create a new markdown file in the `results/` folder (ex: `results/claude-3-manual/raw-outputs.md`) and paste the AI's generated code there so it is permanently logged.

---

## 4. Workflow B: The Python Evaluation Automation

If you want to run the pipeline automatically, we have provided a Python script that handles the entire Generate -> Evaluate -> Score loop.

### How it works:
The script `scripts/run_evaluator.py` dynamically parses the `01-batch-prompts.md` file to extract the raw prompts. It then cross-references those prompts with the `02-metadata-catalog.json` file to retrieve the "Expected Paradigms" (e.g., `USE_PROCD`). 

It feeds the naive prompt to the **Generating Model**. It then takes the output code, combines it with the Expected Paradigms, and feeds it to the **Evaluating Model**. 

### Execution:
Run the script passing the model flags:
```bash
python run_evaluator.py --target-model gpt-4o-mini --auditor-model gpt-4o
```
The final result will automatically be deposited into the `results/` folder as a timestamped `.json` file containing the strict taxonomy categories that the AI failed on (e.g., `ERR_LINUX_HALLUCINATION`).

---

## 5. Translating Defects to Documentation

Once you review the JSON scoresheet (or manually audit your chat logs using the Taxonomy definitions inside `run_evaluator.py`), you must count the frequencies of the failures.

*   If the Evaluating AI tags `ERR_LINUX_HALLUCINATION` multiple times, you must write an `openwrt-docs4ai` tutorial specifically teaching the AI how to replace `systemd` with `procd`.
*   If `ERR_LEGACY_API` is rampant when testing LuCI generation, your next cookbook chapter must explicitly cover modern Vue.js/JavaScript LuCI views versus legacy Lua CBI models. 

This completes the pipeline. You now have a scientifically rigorous, completely decoupled data loop to drive your documentation product.
