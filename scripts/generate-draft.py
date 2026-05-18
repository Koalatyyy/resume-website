import os
import re
import sys
from datetime import date
from pathlib import Path

import anthropic
import requests

POSTS_DIR = Path("blog/src/posts")
DRAFTS_DIR = Path("drafts")

CANDIDATES = [
    "AWS Inspector",
    "AWS Config",
    "IAM Access Analyzer",
    "AWS CloudTrail",
    "AWS Detective",
    "AWS Network Firewall",
    "AWS WAF",
    "Amazon VPC Flow Logs",
    "AWS Firewall Manager",
    "Amazon Cognito security",
    "AWS Organizations SCPs",
    "S3 Object Lock",
    "AWS KMS key policies",
    "AWS Secrets Manager rotation",
    "AWS Audit Manager",
]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text


def existing_slugs() -> set[str]:
    slugs = set()
    for path in POSTS_DIR.glob("*.md"):
        slugs.add(path.stem)
    if DRAFTS_DIR.exists():
        for path in DRAFTS_DIR.glob("*.md"):
            stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
            slugs.add(stem)
    return slugs


def pick_topic() -> str:
    covered = existing_slugs()
    for candidate in CANDIDATES:
        if slugify(candidate) not in covered:
            return candidate
    print("All candidate topics are covered. Add more topics to CANDIDATES.")
    sys.exit(0)


TOPIC_DOC_URLS: dict[str, list[str]] = {
    "AWS Inspector": [
        "https://docs.aws.amazon.com/inspector/latest/user/findings-understanding.html",
        "https://docs.aws.amazon.com/inspector/latest/user/coverage.html",
    ],
    "AWS Config": [
        "https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config.html",
        "https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html",
    ],
    "IAM Access Analyzer": [
        "https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html",
        "https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-policy-validation.html",
    ],
    "AWS CloudTrail": [
        "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html",
        "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html",
    ],
    "AWS Detective": [
        "https://docs.aws.amazon.com/detective/latest/userguide/what-is-detective.html",
        "https://docs.aws.amazon.com/detective/latest/userguide/detective-investigations.html",
    ],
    "AWS Network Firewall": [
        "https://docs.aws.amazon.com/network-firewall/latest/developerguide/stateful-rule-groups-ips.html",
        "https://docs.aws.amazon.com/network-firewall/latest/developerguide/firewall-policies.html",
    ],
    "AWS WAF": [
        "https://docs.aws.amazon.com/waf/latest/developerguide/web-acl.html",
        "https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html",
    ],
    "Amazon VPC Flow Logs": [
        "https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html",
        "https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html",
    ],
    "AWS Firewall Manager": [
        "https://docs.aws.amazon.com/waf/latest/developerguide/fms-policy-primary.html",
        "https://docs.aws.amazon.com/waf/latest/developerguide/fms-getting-started-prerequisites.html",
    ],
    "Amazon Cognito security": [
        "https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-mfa.html",
        "https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-settings-advanced-security.html",
    ],
    "AWS Organizations SCPs": [
        "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html",
        "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_evaluation.html",
    ],
    "S3 Object Lock": [
        "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html",
        "https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html",
    ],
    "AWS KMS key policies": [
        "https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html",
        "https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html",
    ],
    "AWS Secrets Manager rotation": [
        "https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html",
        "https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_how.html",
    ],
    "AWS Audit Manager": [
        "https://docs.aws.amazon.com/audit-manager/latest/userguide/what-is.html",
        "https://docs.aws.amazon.com/audit-manager/latest/userguide/frameworks.html",
    ],
}

DOC_TOKEN_BUDGET = 6000


def fetch_aws_docs(topic: str) -> str:
    urls = TOPIC_DOC_URLS.get(topic, [])
    collected: list[str] = []
    total_chars = 0
    budget_chars = DOC_TOKEN_BUDGET * 4

    for url in urls:
        if total_chars >= budget_chars:
            break
        try:
            page_resp = requests.get(url, timeout=15)
            page_resp.raise_for_status()
            title = re.search(r"<title[^>]*>([^<]+)</title>", page_resp.text, re.IGNORECASE)
            title_text = title.group(1).strip() if title else url
            text = re.sub(r"<[^>]+>", " ", page_resp.text)
            text = re.sub(r"\s+", " ", text).strip()
            excerpt = text[:budget_chars - total_chars]
            collected.append(f"## {title_text}\nSource: {url}\n\n{excerpt}")
            total_chars += len(excerpt)
        except Exception as e:
            print(f"Warning: doc fetch failed for '{url}': {e}", file=sys.stderr)

    if not collected:
        print(f"Error: could not fetch any AWS documentation for topic '{topic}'.", file=sys.stderr)
        sys.exit(1)

    return "\n\n---\n\n".join(collected)


if __name__ == "__main__":
    topic = pick_topic()
    print(f"Selected topic: {topic}")
    print("Fetching AWS documentation...")
    doc_context = fetch_aws_docs(topic)
    print(f"Fetched {len(doc_context)} chars of documentation.")
