# omp-patches

A patch series on top of [omp](https://github.com/can1357/oh-my-pi) releases, and the auth broker and gateway
image built from it.

Every omp release is checked out at its tag, the patches in [`patches/`](patches) are applied in order with
`git am`, every package they touch is checked and tested, and the image is published. A new omp release is
picked up within the hour; when a patch no longer applies, an issue is opened instead.

## Patches

Each patch's header says what it changes and why, and ends with an `Upstream-Status:` trailer:

| Status | Meaning |
|---|---|
| `Pending` | Not sent upstream yet. |
| `Submitted [where]` | Sent upstream and waiting. |
| `Backport [version]` | Taken from a later omp release: drop it once that release is out. |
| `Inappropriate [why]` | Specific to this image, not meant for upstream. |
| `Denied [why]` | Upstream declined it; kept for the reason given. |

<!-- patches:start -->

| # | Patch | Upstream |
|---|---|---|
| 0001 | [feat(ai): auth gateway reports upstream usage and cost](patches/0001-feat-ai-auth-gateway-reports-upstream-usage-and-cost.patch) | Pending |
| 0002 | [fix(ai): drop replayed foreign reasoning for Codex targets](patches/0002-fix-ai-drop-replayed-foreign-reasoning-for-Codex-tar.patch) | Pending |
| 0003 | [fix(ai): replay Codex's own encrypted reasoning through the gateway](patches/0003-fix-ai-replay-Codex-s-own-encrypted-reasoning-throug.patch) | Pending |
| 0004 | [fix(ai): send Codex reasoning only with its following item; retry refused reasoning](patches/0004-fix-ai-send-Codex-reasoning-only-with-its-following-.patch) | Pending |
| 0005 | [fix(ai): keep message digests, not messages, in anthropic thread anchors](patches/0005-fix-ai-keep-message-digests-not-messages-in-anthropi.patch) | Pending |
| 0006 | [feat(ai): drain accounts whose saved reset is about to lapse](patches/0006-feat-ai-drain-accounts-whose-saved-reset-is-about-to.patch) | Pending |
| 0007 | [feat(coding-agent): auth gateway spends saved resets before they expire](patches/0007-feat-coding-agent-auth-gateway-spends-saved-resets-b.patch) | Pending |

### 0001 · feat(ai): auth gateway reports upstream usage and cost

The auth gateway forwards a reported zero cache-write count instead of
dropping it, passes through the upstream's own USD charge (OpenRouter
usage.cost plus BYOK upstream inference cost), and falls back to a catalog
price estimate only when no charge was reported. Usage gains
cacheWriteReported, reportedCost and byokFee to carry this.

### 0002 · fix(ai): drop replayed foreign reasoning for Codex targets

Auth-gateway clients send back the reasoning summaries the gateway streamed
them: chat clients (pi, OpenCode v2) as reasoning_content, Responses clients
(Codex) as reasoning items. The gateway stamps those turns with a foreign
provider, so for an openai-codex target transformMessages demoted the text
to assistant output_text wrapped in <think> tags, and every replayed turn
showed the model its own summaries as printed output.

For openai-codex-responses targets the block is now dropped. Codex replays
only its own encrypted reasoning items, which the same-model path keeps, so
this matches what a native Codex client sends. Every other target still
demotes.

### 0003 · fix(ai): replay Codex's own encrypted reasoning through the gateway

The auth gateway labels each turn a client replays with its route's wire
format (openai-responses, anthropic-messages) and the <provider>/<id> the
client requested, so for an openai-codex target no replayed turn matched
the same-model check and every reasoning item was dropped, its
encrypted_content included. The Responses route also streamed reasoning
output_item.done items without encrypted_content, which is what Codex
keeps as history, and stamped tool-call turns "stop", which strips their
signatures as abandoned tool use.

transformMessages now replays a Responses reasoning item that carries
encrypted_content to a Codex target when the turn is labelled with that
target's <provider>/<id>. Any other reasoning is still dropped for Codex
targets, and turns from other providers keep their current handling. The
Responses route streams the full reasoning item on output_item.done, as
response.completed already did, and stamps tool-call turns toolUse, as
the Messages route does. A gateway client's replayed Responses reasoning
item for any other target, such as a Codex client on an Anthropic model,
is dropped instead of demoted to visible assistant text.

The tests now round-trip through the real parseRequest paths and the
Responses stream instead of a hand-stamped openai-codex turn.

### 0004 · fix(ai): send Codex reasoning only with its following item; retry refused reasoning

Codex fails a request whose replayed reasoning item lacks the output item
it led to ("…without its required following item"), and the backend can
refuse encrypted_content minted for another account, which a session hits
after a usage-limit or auth failover. Since Codex strips every input item
id with store=false, the following-item rule can only hold positionally.

- The Codex encoder drops each reasoning item that no output item of its
  own turn follows: a Claude Code turn left with only thinking, a Codex
  turn whose call never reached the client, or a cut turn.
- The Responses route puts assistant message items into the open assistant
  turn, with their id and phase, so one response's reasoning, messages and
  calls stay one turn.
- When Codex rejects replayed reasoning (invalid_encrypted_content or the
  missing-following-item error), at transport open or in the stream, the
  request is replayed once without any reasoning. The refused items are
  remembered in the session's provider state, so later requests leave them
  out while reasoning minted afterwards still replays.

Tests cover each reviewed case through the real parseRequest paths and the
final Codex request body, and both retry paths against a mocked backend.

### 0005 · fix(ai): keep message digests, not messages, in anthropic thread anchors

A thread anchor outlives its request: it holds the conversation the server
stored, so the next request can be checked to extend it. It held that
conversation as the messages themselves, screenshots included. In-process
omp keeps one session, but the auth gateway keeps provider state for up to
256 conversations, each with its own anchor, so every conversation it
served stayed pinned until another replaced or evicted it.

On a busy gateway, 11 anchors held 185 MB of a 362 MB live heap,
the bulk of it base64 screenshots in tool results. With the per-request
garbage on top, the gateway crossed its 1 GiB limit and was killed by the
kernel 24 times in four days, cutting every stream in flight.

An anchor now keeps one 128-bit digest per message, computed without cache
breakpoints and with object keys sorted, so it continues and refuses
exactly the conversations it did before at a few dozen bytes a message.

### 0006 · feat(ai): drain accounts whose saved reset is about to lapse

The account picker ranks siblings by required drain: the share of a window
left unused divided by the hours until it resets, so quota about to go to
waste is used first. A saved reset (Claude, Codex) that expires before the
window it clears resets on its own is lost unless spent in this window, and
it gives back what the window has used when it is spent: worth the most
with the window full.

So when an account holds a usable saved reset that lapses before a window
resets, the reset's expiry, not the window's reset, is that window's
deadline. The account's drain rises and the gateway sends it work first,
filling the window by the time the reset is spent (see the salvage sweep).
A reset that names the limits it clears counts only for those; one that
names none counts for every window; one the provider says cannot be spent
never counts.

### 0007 · feat(coding-agent): auth gateway spends saved resets before they expire

Sessions salvage a saved Claude or Codex reset that is about to expire
unused, but only while a session runs and only for its own process. A
gateway serving other clients has no session, so its accounts' resets
expire unspent.

`omp auth-gateway serve` now runs the same salvage on a five-minute timer
(session/reset-salvage.ts), with the planners and consent settings a
session uses: `codexResets.autoRedeem5h`/`autoRedeemWeekly`,
`claudeResets.autoRedeem5h`/`autoRedeemWeekly`/`autoRedeemFable`, and
`salvageHorizonHours`. It only salvages (the planners' `sweep` trigger);
spending a reset to lift a block stays with the session whose request hit
it. Only `yes` spends: with nothing set to `yes` no timer starts. Each
spend takes the same cross-process fence as `omp usage reset`, rechecks a
Codex balance under it, is attempted once per credit, and a failure that
may pass is deferred for 30 minutes.

<!-- patches:end -->

## Image

`ghcr.io/savid/omp:<omp version>-r<n>`, where `r<n>` counts builds of the series against that omp release.
`:<omp version>` follows the newest build for that release and `:latest` the newest overall.

The image is the omp release as published to npm, with only the files the series adds or changes laid over it.
The build refuses to replace a file whose published copy is not the release tag's.

One role per container, with its state in `/state`:

```sh
docker run … ghcr.io/savid/omp:latest broker              # credential vault on :8765
docker run … ghcr.io/savid/omp:latest gateway             # auth gateway on :4000
docker run -i … ghcr.io/savid/omp:latest set-key openrouter < key
```

- `broker` needs `OMP_AUTH_BROKER_TOKEN`. `CLAUDE_SETUP_TOKEN`, `OPENROUTER_API_KEY`, `TYPESAFE_API_KEY` and
  `OPENCODE_GO_API_KEY`, when set, are saved to the vault at start; logins added by hand stay.
- `gateway` needs `OMP_AUTH_BROKER_URL` and reads the broker's token from `/state/broker-token`.

### Saved-reset salvage

The gateway spends a Claude or Codex saved reset before it expires unused, and steers work to that account first
so the reset gives back as much as it can. It only spends with consent, set in the gateway's
`/state/.omp/agent/config.yml`; with nothing set to `yes` it spends nothing:

```yaml
claudeResets:
  autoRedeemWeekly: "yes"
  autoRedeemFable: "yes"
  salvageHorizonHours: 12 # spend within this many hours of expiry, when the window is well used
codexResets:
  autoRedeemWeekly: "yes"
  autoRedeem5h: "yes"
```

Each release also carries the patched `@oh-my-pi/pi-ai` as a tarball, for projects that install it by URL.

## Working on the series

```sh
scripts/apply.sh     # omp at the version in UPSTREAM, in ./upstream, with each patch as a commit
                     # change ./upstream and commit: one commit per patch, its message the patch's header
scripts/test.sh      # checks and tests for every package the series touches
scripts/save.sh      # the commits back out to patches/, and the list above
scripts/build.sh     # the image, locally
```

When an omp release breaks a patch:

```sh
scripts/apply.sh 19.1.0              # stops at the patch that no longer applies
git -C upstream am --continue        # once resolved; repeat for each
echo 19.1.0 > UPSTREAM
(cd gateway && bun add --exact @oh-my-pi/pi-coding-agent@19.1.0)
scripts/test.sh && scripts/save.sh   # then commit and push: the release run publishes it
```

## Releases

[`release.yml`](.github/workflows/release.yml) runs hourly and on every push to `master`. When npm has a newer omp,
it moves `UPSTREAM` and the pin in `gateway/package.json` to it; when the series changed since the last release,
it builds the next `r<n>`. Either way it applies, checks and tests the series, publishes the image and a GitHub
release `v<omp version>-r<n>` listing the patches, and commits the move. [`ci.yml`](.github/workflows/ci.yml)
does the same without publishing for every pull request.
