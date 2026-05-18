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


if __name__ == "__main__":
    topic = pick_topic()
    print(f"Selected topic: {topic}")
