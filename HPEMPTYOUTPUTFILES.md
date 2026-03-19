# HPEMPTYOUTPUTFILES: Post-Mortem on Empty Agent Output Files

## What Happened

During the bibliography expansion phase, two agents were launched in the background:

1. **MIT site reverse-engineering agent** (ID: `a761319f218a3eba7`) -- tasked with fetching and analyzing the MIT Electronic Hypnerotomachia site
2. **Web scholarship search agent** (ID: `acb35c0d2ba97a5be`) -- tasked with searching the web for missing HP scholarship

Both agents were launched with `run_in_background: true`. After waiting for them to complete, their output files were found to be **0 bytes**:

```
-rw-r--r-- 1 PC 197121  0 Mar 18 19:41 acb35c0d2ba97a5be.output
-rw-r--r-- 1 PC 197121  0 Mar 18 19:44 a761319f218a3eba7.output (task file name: bn5xup07h.output)
```

## Why It Happened

### Mechanism

Background agents in Claude Code run as subprocesses. Their results are returned through a notification system to the parent conversation. The `.output` files in the temp directory serve as a communication channel. When an agent completes, its result is delivered via the `task-notification` system in the conversation.

In this case, the likely sequence was:

1. Agents were launched at ~19:39-19:41
2. The parent conversation continued working on other tasks (ingesting Perplexity data, writing HPDECKARD2.md)
3. When the parent checked on the agents via `TaskOutput`, both returned `not_ready`
4. The parent waited, then the task IDs were no longer found (`No task found with ID`)
5. The output files remained at 0 bytes

### Root Cause Analysis

Several factors may have contributed:

1. **Session context limits**: The conversation was already deep (this is a long session with many tool calls). Background agents share the session's resource envelope. If the session approached limits, agent subprocesses may have been terminated.

2. **Timeout**: Both agents involved multiple web fetches (MIT site has ~15 pages to analyze; scholarship search requires multiple web queries). Web fetches can be slow, and agent subprocesses may have hit time limits.

3. **Output not persisted to file**: The agent notification system delivers results as in-conversation messages (`<task-notification>` tags), not as file writes. The `.output` files may be placeholders created at launch but never written to if the agent's result was delivered through a different channel.

4. **Agent completion during a tool call**: If the agent completed while the parent was mid-tool-call, the notification may have been queued but not persisted to the output file.

### Evidence

Earlier in the same session, the article-summarization agents (batch 1, 2, 3, 4) were also launched as background agents. Their output files were ALSO 0 bytes:

```
-rw-r--r-- 1 PC 197121  0 Mar 18 18:43 abcfa8e220976991e.output
-rw-r--r-- 1 PC 197121  0 Mar 18 17:59 acd1132e6d44abca6.output
```

But those agents **did** return results -- their output appeared as `<task-notification>` messages in the conversation. The difference is that for the earlier agents, the parent conversation received the notifications and processed them. For the later agents (MIT + scholarship), the parent may not have been in a state to receive the notifications, or the agents may not have completed before the session state shifted.

## Impact

### Work Lost
- MIT site analysis: ~5 minutes of web fetching and analysis. **Redone manually** using direct `WebFetch` calls in the parent conversation.
- Scholarship search: ~5 minutes of web searching. **Redone manually** using `WebSearch` calls.

### Work NOT Lost
- All results that were produced by earlier agents (batches 1-4) were successfully received and integrated into the database.
- The manual redo produced equivalent or better results (the direct web searches found additional scholarship the agent might have missed).

## Lessons

1. **Output files are not the primary delivery mechanism.** Agent results arrive as `<task-notification>` messages in the conversation, not as file contents. The `.output` files are diagnostic artifacts, not reliable storage.

2. **Background agents are fire-and-forget.** If you need guaranteed results, use foreground agents (`run_in_background: false`, the default). Foreground agents block the parent until they complete, ensuring the result is received.

3. **Long-running web tasks are risky for background agents.** Multiple web fetches compound timeout risk. Prefer giving agents bounded, fast tasks (read local files) over open-ended web exploration.

4. **Always have a fallback.** The manual redo worked fine. The agent pattern is an optimization, not a requirement. When it fails, falling back to direct tool calls loses time but not data.

## Recommendation

For this project going forward:
- Use **foreground agents** for all critical-path work (summarization, extraction, analysis)
- Use **background agents** only for genuinely non-blocking tasks where failure is acceptable
- **Never assume** background agent output files contain results -- always check via TaskOutput or conversation notifications
- For web research tasks, prefer **direct WebSearch/WebFetch** in the parent conversation where results can be immediately verified and acted on
