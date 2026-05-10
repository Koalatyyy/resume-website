# Blog Post 3: Security Hub Aggregation & Severity Normalisation — Design Spec
**Date:** 2026-05-10  
**Series:** AWS Security noise reduction (post 3 of 4)

---

## Goal

Write a reference-style blog post covering AWS Security Hub's role as a findings aggregation layer, the ASFF schema, severity normalisation, and cross-account aggregation. Consistent in structure with the GuardDuty and Macie suppression rules posts. Starts private (`eleventyExcludeFromCollections: true`, `noindex: true`).

---

## File

`blog/src/posts/security-hub-aggregation-severity.md`

---

## Frontmatter

```yaml
---
title: "Understanding Security Hub: ASFF, severity normalisation, and cross-account aggregation"
date: 2026-05-10
excerpt: "How Security Hub normalises findings from GuardDuty, Macie, and 30+ integrations into a single schema — and what the severity scores actually mean."
eleventyExcludeFromCollections: true
noindex: true
---
```

---

## Post Structure

### 1. What is AWS Security Hub?

- Managed findings aggregation service — ingests findings from GuardDuty, Macie, Inspector, Config, IAM Access Analyzer, Firewall Manager, and 30+ third-party integrations
- Core function: normalise all findings into a single schema (ASFF) so they can be queried, filtered, and acted on in one place
- Two additional capabilities beyond aggregation: Security Hub Controls (managed compliance checks against CIS, PCI DSS, AWS Foundational Security Best Practices) and Insights (pre-built and custom finding groupings)
- Requires explicit enablement per account per region; integrations must also be enabled individually

### 2. Example Finding Categories

Security Hub organises findings using the ASFF `Types` field, which follows a namespace taxonomy: `Namespace/Category/Classifier`. The five namespaces:

| Namespace | What it covers | Example source |
|---|---|---|
| `Software and Configuration Checks` | Compliance controls, config drift, patch status | Security Hub Controls, Config |
| `TTPs` | MITRE ATT&CK-aligned threat behaviours | GuardDuty, third-party |
| `Sensitive Data Identifications` | Sensitive data discovered in resources | Macie |
| `Effects` | Impact of a finding (data exposure, resource consumption) | GuardDuty, Macie |
| `Unusual Behaviors` | Anomalous activity relative to a baseline | GuardDuty |

Each finding can have multiple `Types` values — a GuardDuty credential finding might carry both `TTPs/Initial Access/Valid Accounts` and `Unusual Behaviors/User/ConsoleLogin`.

### 3. ASFF Explained

Key schema fields and what each one means:

| Field | Purpose |
|---|---|
| `SchemaVersion` | Always `2018-10-08` — the ASFF version |
| `Id` | Unique finding ARN within Security Hub |
| `ProductArn` | ARN of the service or integration that generated the finding |
| `GeneratorId` | Product-specific identifier (e.g. GuardDuty detector ID, Config rule name) |
| `AwsAccountId` | Account the finding relates to (not necessarily where Security Hub is running) |
| `Types` | Namespace/Category/Classifier taxonomy array |
| `CreatedAt` / `UpdatedAt` | ISO 8601 timestamps; `UpdatedAt` reflects when the originating service last updated the finding |
| `Severity.Label` | Normalised label: `INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `Severity.Normalized` | Integer 0–100; the score used internally to derive `Severity.Label` |
| `FindingProviderFields.Severity` | The original severity from the source product, preserved alongside the ASFF score |
| `Resources` | Array of affected AWS resources (type, ID, ARN, region, tags) |
| `Compliance` | Present on Security Hub control findings; absent on threat findings from GuardDuty/Macie |
| `WorkflowState` / `Workflow.Status` | Triage state: `NEW`, `NOTIFIED`, `RESOLVED`, `SUPPRESSED` |
| `RecordState` | `ACTIVE` or `ARCHIVED`; updated by the originating service |

### 4. Severity Normalisation

How the 0–100 `Normalized` score maps to labels:

| Normalized range | Severity.Label |
|---|---|
| 0 | `INFORMATIONAL` |
| 1–39 | `LOW` |
| 40–69 | `MEDIUM` |
| 70–89 | `HIGH` |
| 90–100 | `CRITICAL` |

How each major integration maps its native severity to ASFF Normalized:

| Service | Native severity | ASFF Normalized | Label |
|---|---|---|---|
| GuardDuty | Low (1.0–3.9) | 1–39 | LOW |
| GuardDuty | Medium (4.0–6.9) | 40–69 | MEDIUM |
| GuardDuty | High (7.0–8.9) | 70–89 | HIGH |
| GuardDuty | Critical (9.0+) | 90–100 | CRITICAL |
| Macie | LOW | 1–39 | LOW |
| Macie | MEDIUM | 40–69 | MEDIUM |
| Macie | HIGH | 70–89 | HIGH |
| Inspector | INFORMATIONAL | 0 | INFORMATIONAL |
| Inspector | LOW | 1–39 | LOW |
| Inspector | MEDIUM | 40–69 | MEDIUM |
| Inspector | HIGH | 70–89 | HIGH |
| Inspector | CRITICAL | 90–100 | CRITICAL |

Where the normalisation can mislead: a GuardDuty `HIGH` (e.g. `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS` at 8.0 → Normalized 80) and a Macie `HIGH` (e.g. `Policy:IAMUser/S3BlockPublicAccessDisabled` → Normalized 70) both appear as `HIGH` in Security Hub, but represent very different risk profiles — one is active credential theft, one is a misconfiguration. `Severity.Normalized` gives you a common scale; it does not give you context. The `ProductArn` and `Types` fields are what let you distinguish them.

### 5. Cross-Account Aggregation

- **Delegated administrator**: one account (typically the Security tooling or audit account) is designated as the Security Hub delegated administrator via AWS Organizations. Member accounts are enrolled automatically or manually.
- **Finding flow**: member accounts send findings to their local Security Hub; the delegated administrator account aggregates findings from all members. The `AwsAccountId` field on each finding identifies the originating account.
- **Aggregation Region**: one region is designated as the aggregation region. Findings from all linked regions flow into it. Cross-region aggregation must be explicitly configured.
- **Filtering by account**: the `AwsAccountId` filter attribute lets you scope queries and suppression rules to specific member accounts — useful when a known-noisy account (e.g. a dev sandbox) generates volume you want to separate from production signals.

### 6. JSON Example

An ASFF-normalised GuardDuty `UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B` finding as it appears in Security Hub. Key fields annotated in the surrounding post text:

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

Fields to annotate in prose:
- `ProductArn` — `product/aws/guardduty` identifies this as a GuardDuty finding; a Macie finding would read `product/aws/macie`
- `GeneratorId` — the GuardDuty detector ARN; useful when filtering by detector in multi-account environments
- `Types` — dual classification: MITRE ATT&CK `Valid Accounts` + `Unusual Behaviors/ConsoleLogin`
- `Severity.Normalized` 50 → `MEDIUM` — GuardDuty's native 5.0 maps directly; `FindingProviderFields.Severity.Original` preserves the native score
- `Compliance: null` — absent on threat findings; present only on Security Hub control findings
- `Workflow.Status: NEW` — triage state; changes to `RESOLVED` or `SUPPRESSED` via Security Hub suppression rules or manual update
- `RecordState: ACTIVE` — set to `ARCHIVED` by GuardDuty when the finding is no longer active

### 7. Summary

Recap of: what Security Hub is, ASFF as the normalisation layer, the five finding namespaces, severity score mapping, cross-account aggregation model, and how to read a normalised finding.

### 8. Further Reading

- AWS docs links for: Security Hub overview, ASFF syntax reference, Security Hub integrations, aggregation regions, delegated administrator setup

---

## Consistency Notes

- Same H2 section structure as GD and Macie posts
- Same prose style: direct, no fluff, technical but accessible
- Same further reading section at the end
- JSON block uses `json` language tag for Prism highlighting (already wired in)
- No `draft: true` — use `eleventyExcludeFromCollections: true` to hide (matches hello-world pattern)
