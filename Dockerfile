# ---- base: Python + Pandoc ----
FROM python:3.13-slim AS base

RUN apt-get update \
    && apt-get install -y --no-install-recommends pandoc \
    && rm -rf /var/lib/apt/lists/*

# ---- blog: build & serve ----
FROM base AS blog

WORKDIR /blog

# ---- claude: base + Claude Code CLI ----
FROM base AS claude

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git \
    && rm -rf /var/lib/apt/lists/*

ARG DEV_UID=1000
ARG DEV_GID=1000
RUN groupadd -g ${DEV_GID} dev \
    && useradd -m -u ${DEV_UID} -g dev dev

# Claude Code native installer
# Note: Trusts Anthropic's HTTPS endpoint (claude.ai). The installer
# itself verifies the downloaded binary via SHA-256 checksum.
# -f flag ensures curl fails on HTTP errors rather than saving error pages.
RUN curl -fsSL -o /tmp/claude-install.sh https://claude.ai/install.sh \
    && bash /tmp/claude-install.sh \
    && rm -f /tmp/claude-install.sh \
    && cp /root/.local/bin/claude /usr/local/bin/claude

RUN mkdir -p /home/dev/.local/bin \
    && cp /root/.local/bin/claude /home/dev/.local/bin/claude \
    && chown -R dev:dev /home/dev/.local
ENV PATH="/root/.local/bin:/home/dev/.local/bin:${PATH}"
