---
id: gw_story_01K9E5ZSF05NZ1QAYFYQ8H3PZN
type: story
title: View invoice history
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ5WT0FJVWWECVSKF6DWRS
release: v1.1
order: 21300
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to browse past invoices backed by persistent Invoice/InvoiceLine rows
  so_that: I can download and reconcile
owners: []
tags: []
---
# View invoice history

## Narrative

As a finance operations lead, I want to browse past invoices backed by persistent Invoice/InvoiceLine rows so that I can download and reconcile.

## Acceptance Criteria

### AC-001 — List invoices

**Given:**

- The workspace has monthly invoices as Invoice rows

**When:**

- I GET /api/billing/invoices

**Then:**

- I see each Invoice with period_start, period_end, total, currency, status and download_url; clicking opens the InvoiceLine breakdown

### AC-002 — Invoice detail

**Given:**

- I open a specific Invoice

**When:**

- The detail renders

**Then:**

- Each InvoiceLine is shown (kind, description, amount, cost_center); an active InvoiceContest or CreditRequest against a line shows as a badge

## API

### `GET /api/billing/invoices`
**Response:**

```yaml
response:
  invoices:
  - Invoice
```
**Errors:**

```yaml
errors:
- 401
- 403
```
_inferred: true (carried over from source YAML)_

### `GET /api/billing/invoices/:id`
**Response:**

```yaml
response:
  invoice: Invoice
  lines:
  - InvoiceLine
```
**Errors:**

```yaml
errors:
- 401
- 403
- 404
```
_inferred: true (carried over from source YAML)_

## UI

_None._
## Data Models

- Invoice
- InvoiceLine
- InvoiceContest
- CreditRequest

## Non-Functional Requirements

_None._

## Notes

_None._

## Open Questions

_None._
