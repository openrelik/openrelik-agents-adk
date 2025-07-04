# Experimental suppport for agents

Note: This is not yet production ready.

**Get started**

1. Create a new Google AI Studio API key

2. Update docker-compose.yml

```
openrelik-agents-adk:
    container_name: openrelik-agents-adk
    build:
      context: ./openrelik-agents-adk
      dockerfile: ./Dockerfile
    environment:
      - GOOGLE_GENAI_USE_VERTEXAI=FALSE
      - GOOGLE_API_KEY=<GOOGLE AI STUDIO API KEY>
      - OPENRELIK_MCP_URL=http://openrelik-mcp-server:8081/mcp
    volumes:
      - ./dev-data/artifacts:/path/to/your/artifacts
      - ./openrelik-agents-adk:/usr/local/src/openrelik
    ports:
      - 127.0.0.1:8000:8000
    command: sleep infinity
```

5. Shell into the container:

```
docker compose exec openrelik-agents-adk /bin/bash
```

6. Run the ADK server

```
cd /usr/local/src/openrelik/agents/
adk web --host 0.0.0.0
```

7. Access the development UI at http://localhost:8000
