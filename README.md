# Experimental suppport for agents

Note: This is not yet production ready.

**Get started**

1. Create a new user, e.g. `agent-smith`
2. Create an API key for `agent-smith`
3. Make sure to give `agent-smith` access to folders you want to expose

4. Update docker-compose.yml

```
openrelik-agents-adk:
    container_name: openrelik-agents-adk
    build:
      context: ./openrelik-agents-adk
      dockerfile: ./Dockerfile
    environment:
      - GOOGLE_GENAI_USE_VERTEXAI=FALSE
      - GOOGLE_API_KEY=<GOOGLE AI STUDIO API KEY>
      - OPENRELIK_API_URL=http://host.docker.internal:8710
      - OPENRELIK_API_KEY=<OPENRELIK API KEY>
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
