# Using Closet

## Setup

Install the app and the integration from this repository using Marketplace
(or HACS on older Home Assistant versions). Start the app,
restart Home Assistant after installing the integration, then confirm the
discovered connection in Settings → Devices & services. App/integration versions
must match. The app's sidebar is restricted to administrators.

The optional native API port is disabled by default. Home Assistant-backed
CLI clients use the integration's authenticated bridge and need no extra port.
Standalone containers use bearer authentication. Keep credentials outside the
checkout and use the CLI's token-file or environment support.

## Options

| Option | Purpose |
| --- | --- |
| timezone | IANA timezone for Today. Use Home Assistant's configured timezone. |
| weather_entity | Weather entity to use for the optional outfit lottery. |
| ai_task_entity | AI Task entity; empty uses Home Assistant's preferred AI Task. |

Empty model/weather configuration does not block inventory or sync. A request
that requires an unavailable forecast fails clearly; Ignore forecast is an
explicit choice, not a silent fallback.

## Catalog ownership

The JSON file owns the item metadata, ownership confirmations and image
references. There is no separate Add/Edit workflow in the app. Change the
source file, validate it, preview the diff and sync the reviewed snapshot.
Never infer current ownership from an order or delivery alone.

IDs are stable purchase identities, not descriptions or SKUs. Unknown details
stay null. Sync updates the projection in one transaction, archives absent IDs,
and reactivates IDs restored to the file. An empty snapshot requires an explicit
allow-empty option. Invalid input, a stale revision or a conflicting retry key
does not replace the catalog.

Product photos remain public HTTPS references, not an offline image archive.
Broken or qualified images retain their labels and placeholders. Source
references do not establish an exact style, color or current ownership.

## Today

Today calls the configured HA AI Task only on request. GETs and page visits do
not call a model. The selected provider receives a bounded text-only catalog
shortlist and the selected occasion/weather context. It does not receive photo
files, receipts, source notes, shop metadata or prices.

Model output is advisory. The app validates item IDs and outfit roles but
cannot prove that an outfit is good. Unconfirmed pieces remain labeled.
Failed refreshes preserve the previous result with its own inputs and freshness.
A timeout does not prove the upstream model stopped; retry the same operation
key to reconcile it before deliberately starting a new attempt.

## Backups

The app uses a cold backup. Native Home Assistant backups include its data:
SQLite catalog projection, sync/generation retry state and pairing credentials.
Keep the authoritative JSON separately in your private storage as well. A JSON
copy alone does not restore pairing or runtime state.

## Troubleshooting

Start with integration diagnostics and the CLI's system/status output. Reports
contain versions, counts and health, not item details or tokens. Keep successful
CLI inventory output private. If the model is unavailable, inventory remains
usable. For security problems, use private vulnerability reporting rather than
posting catalogs or credentials publicly.
