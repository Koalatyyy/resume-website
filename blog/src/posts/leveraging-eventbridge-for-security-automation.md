---
title: "Leveraging Amazon EventBridge to invoke Security Automation"
date: 2026-05-16
excerpt: "How EventBridge rules can capture events from GuardDuty, Macie, and Security Hub and automatically invoke remediation workflows."
eleventyExcludeFromCollections: true
noindex: true
---

AWS security services are good at detection. GuardDuty identifies threats. Macie surfaces sensitive data exposure. Security Hub aggregates findings across both. What none of them do by default is act on what they find.

That gap is where Amazon EventBridge fits. It is a serverless event router that captures events from AWS services and delivers them to targets you define: Lambda functions, Step Functions workflows, Systems Manager Automation runbooks, SNS topics, and more. EventBridge is the connective tissue between detection and response.

---

## What is Amazon EventBridge?

Amazon EventBridge is a serverless event bus service. It receives events from AWS services, your own applications, and third-party software, then routes them to one or more targets based on rules you define.

Events in EventBridge are JSON documents. Every AWS service that integrates with EventBridge emits a structured event when something happens: a GuardDuty finding is generated, a Macie finding is archived, an EC2 instance changes state, an IAM policy is modified. EventBridge receives these events on the default event bus and evaluates them against your rules.

There are three ways to process and deliver events in EventBridge:

- **Event buses**: routers that receive events from many sources and deliver them to many targets. The default event bus in every AWS account automatically receives events from AWS services. You can also create custom event buses for events from your own applications or cross-account event routing.
- **Pipes**: point-to-point integrations for when you have a single source and a single target. Pipes support filtering, enrichment, and transformation of events before delivery.
- **Scheduler**: a standalone scheduler for invoking targets on a cron or rate expression, or as a one-time invocation. Separate from event-driven rules.

For security automation, event buses and rules are the primary mechanism.

---

## Event-Driven Automation in AWS

Traditional security operations are largely reactive: a finding appears in a console, an analyst reviews it, a ticket is created, a remediation step is performed manually. In environments with hundreds of accounts and thousands of resources, that pipeline does not scale.

Event-driven automation replaces manual steps with automated responses triggered directly by the events that security services emit. When GuardDuty generates a HIGH severity finding, EventBridge can invoke a Lambda function within seconds to snapshot the affected instance, revoke the compromised credential, or notify the on-call team. No analyst needs to see the finding first.

The model is straightforward:

1. A security service detects something and emits an event
2. EventBridge receives the event on the default event bus
3. A rule evaluates the event against an event pattern
4. If it matches, EventBridge invokes one or more targets
5. The target performs the automated response

Each step is decoupled. The security service does not know or care what happens after it emits the event. The target does not need to poll for findings. EventBridge handles the routing.

This decoupling also means the same event can trigger multiple independent responses simultaneously. A single GuardDuty finding can, via a single EventBridge rule with multiple targets, notify a Slack channel via SNS, open a Jira ticket via a Lambda function, and kick off a Step Functions workflow to isolate the affected resource, all in parallel.

## Automation does not have to mean remediation

Event-driven automation is often framed around mutative actions: isolating an instance, revoking a credential, modifying a security group. Those are valid responses, but they are not the only ones, and they are not always the right first step.

A finding is a signal. It contains what the detecting service observed, but rarely everything you need to make a confident decision. Before taking an action that affects a running workload, it is worth asking what additional context would make that decision clearer.

EventBridge targets can be used purely for enrichment: gathering information that the original finding does not include and feeding it back into your triage workflow. Examples:

- A GuardDuty finding identifies an EC2 instance by ID. A Lambda function can query the EC2 API to retrieve its tags, the IAM role attached, the VPC it sits in, and whether it has a public IP, then attach all of that to the Security Hub finding via `BatchUpdateFindings`
- A Macie finding identifies an S3 object containing credentials. A Lambda function can check whether the bucket has public access enabled, who last modified the object, and whether the bucket has replication configured to an external account, before any suppression or escalation decision is made
- An IAM Access Analyzer finding flags external access to a resource. A Lambda function can look up the principal being granted access and determine whether it belongs to a known partner account listed in a parameter or config store, informing whether the finding warrants escalation or suppression

In each case the automation runs immediately on finding generation, the enriched data is available to the analyst before they open the finding, and no production resource has been touched. This is a lower-risk entry point for teams building their first automated workflows, and a useful pattern even for teams with mature remediation pipelines.

The step-by-step example later in this post shows this pattern in practice: enrichment and notification first, containment as a downstream step.

---

## How EventBridge Captures Security Events

### Event Patterns

A rule matches events using an event pattern: a JSON filter that specifies which fields must be present and what values they must hold. EventBridge evaluates every incoming event against every active rule. If the event matches the pattern, the rule fires.

Event patterns use a subset of the event's JSON structure. You only need to include the fields you want to match on; fields you omit are ignored.

A rule that captures all GuardDuty findings:

```json
{
  "source": ["aws.guardduty"],
  "detail-type": ["GuardDuty Finding"]
}
```

A rule that captures only HIGH and CRITICAL GuardDuty findings, scoped to a specific finding type:

```json
{
  "source": ["aws.guardduty"],
  "detail-type": ["GuardDuty Finding"],
  "detail": {
    "type": ["UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS"],
    "severity": [{ "numeric": [">=", 7] }]
  }
}
```

A rule that captures Security Hub findings with a FAILED compliance status:

```json
{
  "source": ["aws.securityhub"],
  "detail-type": ["Security Hub Findings - Imported"],
  "detail": {
    "findings": {
      "Compliance": {
        "Status": ["FAILED"]
      },
      "Workflow": {
        "Status": ["NEW"]
      }
    }
  }
}
```

### Event Sources

The AWS services most relevant to security automation and their EventBridge event types:

| Service | Event type | When it fires |
|---|---|---|
| GuardDuty | `GuardDuty Finding` | A new finding is generated or an existing finding is updated |
| Security Hub | `Security Hub Findings - Imported` | A finding is ingested or updated in Security Hub |
| Macie | `Macie Finding` | A new Macie finding is generated |
| CloudTrail | Via `aws.cloudtrail` | API calls matching a configured data event trail |
| IAM Access Analyzer | `Access Analyzer Finding` | A new external access finding is generated |
| Config | `Config Rules Compliance Change` | A resource transitions to NON_COMPLIANT |

### Targets

Once a rule matches, EventBridge delivers the event to one or more targets. Common targets for security automation:

- **Lambda**: arbitrary code. Revoke credentials, modify security group rules, call third-party APIs, enrich findings with additional context before forwarding
- **Step Functions**: multi-step workflows with branching logic, retries, and human approval steps. Suited for remediations that require sequenced actions or sign-off
- **Systems Manager Automation**: pre-built and custom runbooks for remediating AWS resource configurations. Useful for Config compliance findings where the remediation is a well-defined AWS API call
- **SNS**: fan-out to email, SMS, or HTTP endpoints. Useful for notifications to on-call paging tools or Slack webhooks
- **SQS**: queue events for downstream processing at controlled throughput. Useful when the consumer cannot handle burst volume from a large finding wave

A single rule can have up to five targets. All targets receive the same event and are invoked in parallel.

---

## Example: Automated Response to Credential Exfiltration

The GuardDuty finding type `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS` indicates that EC2 instance credentials are being used from outside AWS infrastructure. This is high-fidelity: instance credentials should never originate outside AWS, so the false positive rate is low.

An automated response for this finding:

1. EventBridge rule matches on `source: aws.guardduty` and `detail.type: UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS`
2. Rule invokes a Step Functions workflow
3. Workflow step 1: Lambda extracts the affected role ARN from `detail.resource.accessKeyDetails.principalId`
4. Workflow step 2: Lambda calls `iam:PutRolePolicy` to attach an explicit deny-all inline policy to the role, blocking further use of any active sessions
5. Workflow step 3: SNS notifies the security team with the finding detail and the role that was locked
6. Workflow step 4: Lambda updates the finding's `Workflow.Status` in Security Hub to `NOTIFIED` via `BatchUpdateFindings`

The entire sequence completes in under 30 seconds from finding generation. No analyst interaction required for the initial containment.

---

## Further Reading

- [What is Amazon EventBridge?](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html)
- [Amazon EventBridge rules](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rules.html)
- [EventBridge event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html)
- [EventBridge targets](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-targets.html)
- [GuardDuty EventBridge events](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings_cloudwatch.html)
- [Security Hub EventBridge events](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-cwe-integration-types.html)
- [Automated response and remediation in Security Hub](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-cloudwatch-events.html)
