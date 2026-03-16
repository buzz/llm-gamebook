---
description: Implement tasks from an OpenSpec change using a multi-agent supervisor workflow
---

Implement tasks from an OpenSpec change using an advanced supervisor agent that orchestrates specialized sub-agents (@test, @make-python, @make-typescript, @review) for a robust, TDD-driven development cycle.

**Input**: Optionally specify a change name (e.g., `/opsx-implement add-auth`). If omitted, infer from context or prompt the user.

**Steps**

1. **Select the Change**
   Identify the target change. Use `openspec list --json` if ambiguous and ask the user via the **question tool**.

2. **Verify Context and Readiness**
   Read `proposal.md`, `design.md`, `tasks.md`, and delta specs.
   - Extract **Constraints** (SLOs, patterns) and **Acceptance Criteria**.
   - If critical information is missing, escalate to the user immediately.

3. **Initialize Task Tracking**
   Initialize a todo list for the implementation tasks using the **todowrite tool**.

4. **Sub-Task Implementation Loop**
   Group tasks to unit of work. Each unit of work can encompass one or more tasks.
   Work on unit of work in the todo list separately using the following loop.
   Run @test, @make-* and @review one after another as each input depends on previous output.
   Prefer TDD (test-driven development) where tests are written before implementation.
   TDD may be skipped for trivial changes, bug fixes, config changes and refactorings.
   Track an `iteration_count` (max 3) for each sub-task.

   - **Step 4.1: Test Phase (@test)**
     - **Decision:** Is the task testable?
       - **Yes:** Call @test
       - **No:** Skip @test and proceed directly to **Step 4.2** in "Standard Mode."
     - **Call @test and provide Input:**
       - **REQUIRED**
         - **Task:** Clear description of what to implement
         - **Acceptance Criteria:** Specific, testable criteria for success
         - **Test File:** Path for the test file to create
       - **OPTIONAL**
         - **Code Context:** Relevant existing code (actual snippets, not just paths)
         - **Test Design:** Key behaviors to verify, edge cases, what NOT to test (from plan)
         - **Constraints:** Patterns to follow, things to avoid, style requirements
     - **Handle Output:**
       - `VALID RED`: Store the "Notes for @make-*" and test file paths. Proceed to 4.2.
       - `NOT_TESTABLE`: Document the reason (e.g., config-only) and proceed directly to 4.2 in "Standard Mode."
       - `BLOCKED`: Escalate to User (Environment/Context issue).

   - **Step 4.2: Implementation Phase (@make-*)**
     - **Decision:** Use the @make-python for Python, @make-typescript for TypeScript
     - **Call @make-* and provide Input:**
       - **REQUIRED**
         - **Task:** Clear description of what to implement
         - **Acceptance Criteria:** Specific, testable criteria for success
         - **Files to Modify:** Explicit list of files to touch (including new files to create)
         - **Notes for @make-*:** Notes from the Test phase (if available)
       - **OPTIONAL**
         - **Code Context:** Relevant existing code (actual snippets, not just paths)
         - **Pseudo-code/Snippets:** Approach suggestions or code to use as inspiration
         - **Constraints:** Patterns to follow, things to avoid, style requirements
         - **Integration Contract:** Cross-task context (public interface, invariants, interactions with other tasks)
     - **Handle Output:**
       - `TDD Evidence`: Verify the RED → GREEN transition and regression check results.
       - `Escalation (Test Issue)`: If @make-* reports "questionable tests" or logic flaws in the test suite, route the feedback back to **Step 4.1 (@test)** for a fix. Increment `iteration_count`.
       - `Escalation (Blocker)`: If @make-* identifies an architectural flaw, jump to **Escalation Logic**.

   - **Step 4.3: Review Phase (@review)**
     - **Call @review and provide Input:**
       - Problem Statement (Task)
       - Implementation (diff/code from @make-*)
       - System Constraints
     - **Handle Output:**
       - `Verdict: ACCEPTABLE`: Mark task as DONE.
       - `Verdict: NEEDS WORK` or `NEEDS SIMPLIFICATION`: Route findings (Risk/Safety or Complexity issues) back to **Step 4.2 (@make-*)** for refinement. Increment `iteration_count`.
       - `Verdict: BLOCK`: Analyze the "Concrete failure path." If it indicates a design flaw, escalate to user. If it's an implementation bug, route to @make-*.

5. **Completion Overview**
   Once all tasks are done, generate a summary including:
   - Task outcomes and TDD evidence.
   - Simplifications suggested/accepted.
   - Major challenges or design deviations encountered.

---

### Escalation & Retry Logic

- **Iteration Limit:** If any single task triggers more than **three (3)** hand-offs back to a sub-agent (e.g., @make-* failing review 3 times, or @test failing to fix tests for @make-* 3 times), the Supervisor MUST escalate to the user.
- **Architectural Escalation:** If a sub-agent reports a conflict with the `design.md` or a logic flaw that cannot be solved within the task scope, the Supervisor must pause and use the **question tool** to ask the user for a design update or a change in requirements.
- **Protocol:** Every user escalation must include:
  1. The specific sub-agent that hit the wall.
  2. The technical blocker/evidence (e.g., the @review "BLOCK" path).
  3. Actionable options (Update Design, Skip Task, Manual Intervention).

### Output On Completion

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1
- [x] Task 2
...

All tasks complete! You can archive this change with `/opsx-archive`.
```

**Output On Pause (Issue Encountered)**

Use the **question tool**.

```
## Implementation Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 4/7 tasks complete

### Issue Encountered
<description of the issue>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

### Guardrails
- Keep going through tasks until done or blocked
- Always read context files before starting (from the apply instructions output)
- If a task is ambiguous, pause and ask before delegating implementation
- If implementation reveals issues, pause and escalate to user
- Focus on sub-agent orchestration. Leave implementation to sub-agents.
- Update task checkbox immediately after completing each task (`tasks.md`)
- Pause on errors, blockers, or unclear requirements - don't guess

