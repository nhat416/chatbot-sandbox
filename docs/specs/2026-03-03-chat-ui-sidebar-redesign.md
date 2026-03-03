# Chat UI Sidebar Redesign

## Summary
Redesign the single-page chat interface to closely match the provided design references by introducing a left navigation/sidebar, thread history list, a cleaner center conversation layout, and a bottom composer while keeping the existing backend API and streaming behavior unchanged.

## Problem
The current UI is functional but does not match the desired product direction shown in `designs/chatbot_design_1.png` and `designs/chatbot_design_2.png`. It lacks a persistent sidebar with chat threads and has a simpler visual structure.

## Goals
- Make `static/index.html` visually and structurally similar to the design images.
- Add a left sidebar with nav actions and visible chat history threads.
- Support multiple chat threads in the frontend state with active-thread switching.
- Provide an in-UI way to clear local thread history.
- Preserve streaming chat behavior via `POST /chat` SSE responses.
- Ensure layout remains usable on desktop and mobile.

## Non-Goals
- No backend persistence or new backend endpoints.
- No authentication or multi-user thread sync.
- No markdown rendering upgrade or rich attachments.

## Current Behavior
- Single chat timeline in one pane.
- No thread list or thread switching.
- Minimal header + bottom input row.

## Proposed Behavior
- Add a sidebar with:
  - brand/header row
  - actions (`New chat`, `Clear chats`, `Search chats`, etc. as UI items)
  - "Your chats" list showing thread titles
  - profile footer area
- Main area includes:
  - top bar with title and action buttons
  - conversation viewport centered with ChatGPT-like spacing
  - empty-state prompt before first message
  - rounded composer dock near the bottom
- Frontend manages multiple threads in memory and local storage.
- Switching threads immediately updates message view.
- Clearing chats removes stored local thread state and resets the visible thread list.

## API / Data Contract Changes
- No API changes.
- Existing `POST /chat` request/stream format remains the same.

## Edge Cases
- Sending a message with no selected thread should auto-create a thread.
- Empty/whitespace-only input should do nothing.
- Failed network call should show a clear assistant-side error message.
- Thread title defaults should remain readable for very short or very long prompts.
- Clearing history should not affect backend state (none exists) or API behavior.

## Acceptance Criteria
- [ ] Sidebar with thread history is visible on desktop and similar to design.
- [ ] Users can create a new thread and switch between threads.
- [ ] Users can clear local thread history from the sidebar.
- [ ] Sending messages streams assistant output as before and stores messages in the active thread.
- [ ] Empty-state prompt appears when thread has no messages.
- [ ] Mobile layout remains usable (sidebar toggle/stacked behavior).

## Implementation Plan
1. Replace `static/index.html` layout/CSS to implement sidebar + topbar + centered chat canvas + composer.
2. Refactor frontend state management to support multiple threads and active-thread rendering.
3. Keep existing SSE parsing and token queue behavior in the new UI flow.
4. Add local-storage persistence for thread list and active thread.
5. Manually verify desktop and mobile behavior.

## Validation Plan
- Automated checks:
  - `uv run ruff check .` (no Python changes expected)
- Manual checks:
  - Run app and verify `/` loads redesigned UI
  - Create new chat threads and switch between them
  - Send messages and verify streaming still ends with `[DONE]`
  - Verify layout at desktop and narrow/mobile widths

## Risks and Mitigations
- Risk: UI changes accidentally break stream rendering.
  - Mitigation: preserve SSE parser/token queue logic and test with live prompt.
- Risk: mobile layout regression due to added sidebar.
  - Mitigation: add responsive CSS with off-canvas sidebar behavior.

## Rollback Plan
Revert `static/index.html` to the previous version if regressions are found.
