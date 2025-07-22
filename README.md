# Experimental suppport for agents

Note: This is not yet production ready.

**Get started**

1. Create a new Google AI Studio API key

2. Create a new user, e.g. `agent-smith` (using admin.py)

3. Create an API key for `agent-smith` (via logging in as the user and create one in the UI)

4. Make sure to give `agent-smith` access to folders you want to expose

5. Update docker-compose.yml

```
openrelik-agents-adk:
    container_name: openrelik-agents-adk
    build:
      context: ./openrelik-agents-adk
      dockerfile: ./Dockerfile
    environment:
      - GOOGLE_GENAI_USE_VERTEXAI=FALSE
      - GOOGLE_API_KEY=<GOOGLE AI STUDIO API KEY>
      # Option 1: We run the MCP server with stdio in the agent
      #           - This works out-of-the-box
      - OPENRELIK_API_URL=http://openrelik-server:8710
      - OPENRELIK_API_KEY=<OPENRELIK API KEY>
      # Option 2: We run the MCP server standalone with 'transport=http'
      #           - Add the compose config for OpenRelik MCP server from
      #             https://github.com/openrelik/openrelik-mcp-server
      #           - Then remove the hash from the line below to enable it.
      #- OPENRELIK_MCP_URL=http://openrelik-mcp-server:8081/mcp
    volumes:
      - ./data:/usr/share/openrelik/data
    ports:
      - 127.0.0.1:8000:8000
    command: sleep infinity
```

6. Shell into the container:

```
docker compose exec openrelik-agents-adk /bin/bash
```

7. Run the ADK server

```
cd agents
adk web --host 0.0.0.0
```

8. Access the development UI at http://localhost:8000
