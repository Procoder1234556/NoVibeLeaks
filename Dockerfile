# MCPmarket / Docker deploy — stdio MCP (NoVibeLeaks / novibeleaks)
FROM python:3.12-slim

WORKDIR /app
COPY secmcp /app/secmcp
WORKDIR /app/secmcp

RUN pip install --no-cache-dir .

CMD ["novibeleaks"]
