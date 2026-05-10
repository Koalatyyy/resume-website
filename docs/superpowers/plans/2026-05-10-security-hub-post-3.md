# Security Hub Post 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write a reference-style blog post on AWS Security Hub covering ASFF, severity normalisation, and cross-account aggregation — consistent with the GuardDuty and Macie posts in the series, starting private.

**Architecture:** Single markdown file in `blog/src/posts/`. Eleventy reads it on build, applies `post.njk` layout, and outputs to `blog/_site/security-hub-aggregation-severity/index.html`. The `eleventyExcludeFromCollections: true` and `noindex: true` frontmatter flags keep it hidden from the blog index, Writing section sync, and search engines until removed.

**Tech Stack:** Markdown, Eleventy (Nunjucks), Prism.js (syntax highlighting via `json` fence tag — already wired in)

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `blog/src/posts/security-hub-aggregation-severity.md` | Create | The post content |

---

## Task 1: Write the Post

**Files:**
- Create: `blog/src/posts/security-hub-aggregation-severity.md`

- [ ] **Step 1: Create the file with frontmatter**

Create `blog/src/posts/security-hub-aggregation-severity.md` with this exact frontmatter:

```markdown
---
title: "Understanding Security Hub: ASFF, severity normalisation, and cross-account aggregation"
date: 2026-05-10
excerpt: "How Security Hub normalises findings from GuardDuty, Macie, and 30+ integrations into a single schema — and what the severity scores actually mean."
eleventyExcludeFromCollections: true
noindex: true
---
```

- [ ] **Step 2: Write Section 1 — What is AWS Security Hub?**

Append to the file:

```markdown
## What is AWS Security Hub?

AWS Security Hub is a managed cloud security posture management service that aggregates, normalises, and prioritises security findings from across your AWS environment. Where GuardDuty identifies threats and Macie identifies sensitive data exposure, Security Hub acts as the centralised layer above them — ingesting findings from both services (and 30+ others) and presenting them through a single console and API.

At the core of Security Hub is the **Amazon Security Finding Format (ASFF)**: a standardised JSON schema that every integrated service must map its findings to before Security Hub will accept them. ASFF gives every finding a common set of fields — severity, affected resource, finding type, workflow state — regardless of which service generated it.

Beyond aggregation, Security Hub provides two additional capabilities:

- **Security Hub Controls**: managed compliance checks aligned to standards including CIS AWS Foundations Benchmark, PCI DSS, and AWS Foundational Security Best Practices. Each control is a continuously evaluated rule that generates its own ASFF finding when a resource is non-compliant.
- **Insights**: pre-built and custom groupings of findings, useful for surfacing patterns such as "all HIGH findings by affected account" or "all findings for a specific EC2 instance".

Security Hub must be explicitly enabled per account and per region. Integrations with GuardDuty, Macie, Inspector, Config, and IAM Access Analyzer are enabled separately within Security Hub after the service is turned on.

---
```

- [ ] **Step 3: Write Section 2 — Example Finding Categories**

Append to the file:

```markdown
## Finding Categories

Security Hub classifies every finding using the ASFF `Types` field, which follows a three-level namespace taxonomy: `Namespace/Category/Classifier`. A finding can have multiple `Types` values when it maps to more than one classification.

The five namespaces in use across Security Hub integrations:

| Namespace | What it covers | Example sources |
|---|---|---|
| `Software and Configuration Checks` | Compliance controls, configuration drift, patch status | Security Hub Controls, AWS Config |
| `TTPs` | Threat behaviours aligned to MITRE ATT&CK | GuardDuty, third-party integrations |
| `Sensitive Data Identifications` | Sensitive data discovered in cloud resources | Amazon Macie |
| `Effects` | The impact of a finding — data exposure, resource consumption | GuardDuty, Macie |
| `Unusual Behaviors` | Anomalous activity relative to an established baseline | GuardDuty |

A GuardDuty finding for a console login from an unusual location might carry both `TTPs/Initial Access/Valid Accounts` and `Unusual Behaviors/User/ConsoleLogin` — two `Types` values reflecting different facets of the same event.

Security Hub Controls findings always fall under `Software and Configuration Checks/Industry and Regulatory Standards` or `Software and Configuration Checks/AWS Security Best Practices`, depending on which standard the control belongs to.

---
```

- [ ] **Step 4: Write Section 3 — ASFF Explained**

Append to the file:

```markdown
## The Amazon Security Finding Format (ASFF)

ASFF is the JSON schema that all Security Hub findings conform to. Every integrated service — GuardDuty, Macie, Inspector, third-party products — must translate its native finding format into ASFF before Security Hub will ingest it. This normalisation is what makes cross-service querying and filtering possible.

The key fields:

| Field | Purpose |
|---|---|
| `SchemaVersion` | Always `2018-10-08` — the ASFF version |
| `Id` | Unique finding ARN within Security Hub |
| `ProductArn` | ARN of the service or integration that generated the finding — `product/aws/guardduty`, `product/aws/macie`, etc. |
| `GeneratorId` | Product-specific identifier: the GuardDuty detector ARN, the Config rule name, the Security Hub control ID |
| `AwsAccountId` | The account the finding relates to — in a multi-account setup, this is the member account, not the aggregator |
| `Types` | Array of `Namespace/Category/Classifier` strings classifying the finding |
| `CreatedAt` / `UpdatedAt` | ISO 8601 timestamps; `UpdatedAt` reflects when the originating service last updated the finding |
| `Severity.Label` | Normalised severity label: `INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` |
| `Severity.Normalized` | Integer 0–100; the score Security Hub uses internally to derive `Severity.Label` |
| `FindingProviderFields.Severity` | The original severity from the source product, preserved alongside the normalised ASFF score |
| `Resources` | Array of affected AWS resources, each with `Type`, `Id`, `ARN`, `Region`, and optional `Details` |
| `Compliance` | Present on Security Hub control findings (contains `Status`: `PASSED`, `FAILED`, `WARNING`, `NOT_AVAILABLE`); absent on threat findings from GuardDuty and Macie |
| `WorkflowState` / `Workflow.Status` | Triage state: `NEW`, `NOTIFIED`, `RESOLVED`, or `SUPPRESSED` — updated manually or via automation |
| `RecordState` | `ACTIVE` or `ARCHIVED`; set by the originating service when a finding is no longer relevant |

The distinction between `RecordState` and `Workflow.Status` is worth noting. `RecordState` is controlled by the originating service — GuardDuty sets a finding to `ARCHIVED` when it stops observing the behaviour. `Workflow.Status` is controlled by your team — it reflects where the finding sits in your triage process and is set manually or via Security Hub automation rules.

---
```

- [ ] **Step 5: Write Section 4 — Severity Normalisation**

Append to the file:

```markdown
## Severity Normalisation

Every finding ingested by Security Hub is assigned a `Severity.Normalized` score between 0 and 100. This score determines the `Severity.Label` displayed in the console and returned by the API:

| Normalized range | Severity.Label |
|---|---|
| 0 | `INFORMATIONAL` |
| 1–39 | `LOW` |
| 40–69 | `MEDIUM` |
| 70–89 | `HIGH` |
| 90–100 | `CRITICAL` |

Each integrated service maps its own native severity scale to this 0–100 range. For the three AWS services most commonly used together:

| Service | Native severity | ASFF Normalized | Label |
|---|---|---|---|
| GuardDuty | Low (1.0–3.9) | 1–39 | `LOW` |
| GuardDuty | Medium (4.0–6.9) | 40–69 | `MEDIUM` |
| GuardDuty | High (7.0–8.9) | 70–89 | `HIGH` |
| GuardDuty | Critical (9.0+) | 90–100 | `CRITICAL` |
| Macie | LOW | 1–39 | `LOW` |
| Macie | MEDIUM | 40–69 | `MEDIUM` |
| Macie | HIGH | 70–89 | `HIGH` |
| Inspector | INFORMATIONAL | 0 | `INFORMATIONAL` |
| Inspector | LOW | 1–39 | `LOW` |
| Inspector | MEDIUM | 40–69 | `MEDIUM` |
| Inspector | HIGH | 70–89 | `HIGH` |
| Inspector | CRITICAL | 90–100 | `CRITICAL` |

The normalised score provides a common severity axis across services — but it does not provide context. A GuardDuty `HIGH` finding for `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS` (Normalized: 80) and a Macie `HIGH` finding for `Policy:IAMUser/S3BlockPublicAccessDisabled` (Normalized: 70) both appear as `HIGH` in Security Hub. The first represents active credential theft; the second is a bucket misconfiguration. The label is the same; the risk profile is not.

This is why `ProductArn` and `Types` matter when building filters, suppression rules, or automation. Filtering on `Severity.Label = HIGH` alone will surface both. Filtering on `ProductArn = product/aws/guardduty` AND `Severity.Label = HIGH` narrows to active threat findings from GuardDuty only.

The original source severity is always available in `FindingProviderFields.Severity.Original`, which preserves the native score (e.g. `"5.0"` for a GuardDuty Medium) alongside the normalised value.

---
```

- [ ] **Step 6: Write Section 5 — Cross-Account Aggregation**

Append to the file:

```markdown
## Cross-Account Aggregation

In a multi-account AWS organisation, Security Hub findings are generated locally in each member account. Cross-account aggregation centralises them into a single view without requiring you to log into each account individually.

### Delegated Administrator

One account — typically the security tooling or audit account — is designated as the Security Hub delegated administrator via AWS Organizations. Member accounts are enrolled automatically (if auto-enable is configured in Organizations) or manually. Once enrolled, each member account's Security Hub findings are visible to the administrator account.

The `AwsAccountId` field on each finding identifies the originating member account. In the administrator account's console and API, findings from all members are queryable alongside findings from the administrator account itself.

### Aggregation Region

Security Hub findings are regional. Cross-region aggregation must be explicitly configured: one region is designated as the aggregation region, and linked regions forward their findings into it. This gives you a single-region view across both accounts and regions.

The aggregation region must be the same region where your delegated administrator is configured. Regions are linked individually — you select which regions contribute findings to the aggregation region.

### Filtering by Account

When querying aggregated findings, the `AwsAccountId` filter attribute scopes results to specific member accounts. This is useful when a known-noisy account — a development sandbox or a penetration testing account — generates volume that would otherwise dilute the signal from production accounts. You can build Security Hub automation rules that apply `Workflow.Status = SUPPRESSED` to findings from specific accounts matching specific criteria, without affecting the same finding types in other accounts.

---
```

- [ ] **Step 7: Write Section 6 — JSON Example**

Append to the file:

````markdown
## Example ASFF Finding

The following is a GuardDuty `UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B` finding as it appears in Security Hub after normalisation — the format returned by the Security Hub `GetFindings` API.

```json
{
  "SchemaVersion": "2018-10-08",
  "Id": "arn:aws:securityhub:eu-west-1:123456789012:subscription/guardduty/v1/eu-west-1/123456789012/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "ProductArn": "arn:aws:securityhub:eu-west-1::product/aws/guardduty",
  "GeneratorId": "arn:aws:guardduty:eu-west-1:123456789012:detector/abc123def456abc123def456abc123de",
  "AwsAccountId": "123456789012",
  "Types": [
    "TTPs/Initial Access/Valid Accounts",
    "Unusual Behaviors/User/ConsoleLogin"
  ],
  "CreatedAt": "2026-05-10T08:42:17Z",
  "UpdatedAt": "2026-05-10T08:42:17Z",
  "Severity": {
    "Label": "MEDIUM",
    "Normalized": 50,
    "Original": "MEDIUM"
  },
  "FindingProviderFields": {
    "Severity": {
      "Label": "MEDIUM",
      "Original": "5.0"
    },
    "Types": [
      "TTPs/Initial Access/Valid Accounts",
      "Unusual Behaviors/User/ConsoleLogin"
    ]
  },
  "Title": "API GenerateDataKey was invoked from an unusual location.",
  "Description": "APIs commonly used to obtain data keys, which can be used to access encrypted data, were invoked from an unusual location. The API call was made from the country Spain, which differs from the expected country United Kingdom for IAM user john.doe.",
  "Resources": [
    {
      "Type": "AwsIamAccessKey",
      "Id": "arn:aws:iam::123456789012:user/john.doe",
      "Partition": "aws",
      "Region": "eu-west-1",
      "Details": {
        "AwsIamAccessKey": {
          "PrincipalId": "AIDABC123DEF456GHI789",
          "PrincipalType": "IAMUser",
          "PrincipalName": "john.doe"
        }
      }
    }
  ],
  "WorkflowState": "NEW",
  "Workflow": {
    "Status": "NEW"
  },
  "RecordState": "ACTIVE",
  "Compliance": null
}
```

Key fields to note:

- **`ProductArn`**: `product/aws/guardduty` identifies the originating service. A Macie finding reads `product/aws/macie`; a Security Hub control finding reads `product/aws/securityhub`. This is the primary field for filtering by integration.
- **`GeneratorId`**: the GuardDuty detector ARN. In multi-account environments with multiple detectors, this identifies which detector fired — useful when a specific detector is known to generate noise for a particular finding type.
- **`Types`**: dual classification — `TTPs/Initial Access/Valid Accounts` maps to MITRE ATT&CK; `Unusual Behaviors/User/ConsoleLogin` reflects GuardDuty's anomaly detection model. Both are searchable filter attributes in Security Hub.
- **`Severity.Normalized`**: 50, which places this in the `MEDIUM` band (40–69). GuardDuty's native severity of 5.0 maps directly to 50. `FindingProviderFields.Severity.Original` preserves the native `"5.0"` alongside the normalised value.
- **`Compliance`**: `null` — absent on threat findings. Present only on Security Hub control findings, where it carries `Status: PASSED | FAILED | WARNING | NOT_AVAILABLE`.
- **`Workflow.Status`**: `NEW` — the finding has not been triaged. Changes to `RESOLVED` or `SUPPRESSED` via Security Hub automation rules or manual update. Unlike `RecordState`, this field is owned by your team, not the originating service.
- **`RecordState`**: `ACTIVE` — the finding is current. GuardDuty sets this to `ARCHIVED` when it stops observing the behaviour, independent of your triage state.

---
````

- [ ] **Step 8: Write Section 7 — Summary**

Append to the file:

```markdown
## Summary

In this post we covered the core building blocks of AWS Security Hub and how findings from GuardDuty, Macie, and other services are normalised into a common format.

We started with what Security Hub is: a managed aggregation layer that ingests findings from 30+ integrations and normalises them into ASFF, with Security Hub Controls and Insights built on top.

We looked at the five finding type namespaces — `Software and Configuration Checks`, `TTPs`, `Sensitive Data Identifications`, `Effects`, and `Unusual Behaviors` — and how a single finding can carry multiple `Types` values mapping it to different classification dimensions.

We walked through the key ASFF fields: `ProductArn` as the primary integration identifier, `GeneratorId` as the product-specific source, `Types` as the classification taxonomy, and the `Severity.Normalized` / `Severity.Label` pair as the common severity axis. We also covered the distinction between `RecordState` (owned by the originating service) and `Workflow.Status` (owned by your triage process).

We covered severity normalisation in detail — how each service maps its native scale to the 0–100 ASFF range, and why `Severity.Label` alone is not enough to distinguish risk profiles across services. `ProductArn` and `Types` provide the context that severity alone cannot.

Finally we covered cross-account aggregation: the delegated administrator model, aggregation regions, and how to use `AwsAccountId` as a filter attribute to scope findings to specific member accounts.

---

## Further Reading

- [What is AWS Security Hub?](https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html)
- [Amazon Security Finding Format (ASFF) syntax](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-findings-format.html)
- [ASFF field reference](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-findings-format-attributes.html)
- [Severity normalisation in Security Hub](https://docs.aws.amazon.com/securityhub/latest/userguide/finding-update-batchimportfindings.html#batchimportfindings-severity)
- [Available AWS service integrations](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-internal-providers.html)
- [Designating a Security Hub administrator account](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-accounts-orgs-recommend.html)
- [Configuring finding aggregation across Regions](https://docs.aws.amazon.com/securityhub/latest/userguide/finding-aggregation.html)
```

- [ ] **Step 9: Build and verify**

```bash
cd blog && npm install && npx @11ty/eleventy
```

Expected output includes:
```
Writing ./_site/security-hub-aggregation-severity/index.html from ./src/posts/security-hub-aggregation-severity.md
```

Open `blog/_site/security-hub-aggregation-severity/index.html` in a browser. Confirm:
- Post renders with correct title and date
- All tables display correctly
- JSON block has Prism syntax highlighting (coloured tokens)
- Post does NOT appear in `blog/_site/index.html` post list (excluded from collections)
- `<meta name="robots" content="noindex">` is present in the `<head>` (from `noindex: true`)

- [ ] **Step 10: Verify sync script excludes the post**

```bash
node scripts/sync-writing.js
```

Expected output:
```
sync-writing: wrote 2 post card(s) to index.html
```

Still 2, not 3 — the new post is excluded because `eleventyExcludeFromCollections: true` is in its frontmatter.

- [ ] **Step 11: Commit**

```bash
git add blog/src/posts/security-hub-aggregation-severity.md
git commit -m "feat: add Security Hub aggregation and severity post (private)"
```

---

## Self-Review

**Spec coverage:**
- [x] Frontmatter with private flags — Step 1
- [x] What is Security Hub — Step 2
- [x] Finding categories / Types namespace — Step 3
- [x] ASFF fields table — Step 4
- [x] Severity normalisation tables — Step 5
- [x] Cross-account aggregation — Step 6
- [x] JSON example with annotations — Step 7
- [x] Summary — Step 8
- [x] Further reading — Step 8
- [x] Build verification — Step 9
- [x] Sync script exclusion check — Step 10

**Placeholder scan:** No TBDs, no vague steps. All content is complete.

**Type consistency:** N/A — this is content, not code. No type mismatches possible.

**Note on publishing:** To publish, remove `eleventyExcludeFromCollections: true` and `noindex: true` from the frontmatter. The sync script will pick up the post on the next deploy and add it to the Writing section automatically.
