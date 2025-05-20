# Interacting with the AI

This document explains how the AI streaming system works in Quore and how to implement a chat UI to interact with it.

## Streaming API

The chat API uses a server-sent events (SSE) style streaming response for interaction. The backend streams real-time AI responses and events using a Vercel-compatible format.

### Endpoint

```
POST /projects/{project_id}/chat
```

### Request Format

```json
{
  "messages": [
    { 
      "role": "user", 
      "content": "Previous user message" 
    },
    { 
      "role": "assistant", 
      "content": "Previous assistant response" 
    },
    { 
      "role": "user", 
      "content": "Current user message" 
    }
  ],
  "config": {
    "next_question_suggestions": true
  }
}
```

Notes:
- The last message must be from the user
- The `config` object is optional

### Stream Response Format

The server returns a text/event-stream response with different prefixes for different event types:

1. **Text Events** (prefix `0:`)
   - Contains actual text content from the AI
   - Sent as individual tokens that should be concatenated on the front-end

2. **Data Events** (prefix `8:`)
   - Contains structured data like source references or suggested follow-up questions
   - Sent as JSON objects

3. **Error Events** (prefix `3:`)
   - Contains error information if something goes wrong

These prefixes (0, 8, 3) follow the [Vercel AI SDK](https://ai-sdk.dev/) streaming protocol, which is designed to be compatible with OpenAI's streaming format. They aren't random numbers but correspond to specific event types in the protocol:
- `0:` - Text/content events (delta tokens)
- `8:` - Data/tool events (structured JSON)
- `3:` - Error events

This standardized format ensures interoperability between different AI services and frontend frameworks.

### Data Event Types

The `8:` data events include a `type` field that indicates what kind of data is being sent. The following event types are currently supported:

| Type | Description | Data Structure |
|------|-------------|----------------|
| `sources` | Reference documents used to generate the response | `{"nodes": [{"text": "...", "metadata": {...}}]}` |
| `suggested_questions` | Follow-up questions suggested by the AI | Array of question strings |
| `agent` | Agent-specific events and information | `{"agent": "...", "type": "text/progress", "text": "...", "data": {...}}` |
| `artifact` | File or data artifacts generated during the response | Artifact metadata and content |

Each type has its own data structure and should be handled accordingly in the front-end implementation.

### Event Types

The streaming response may include the following event types:

#### 1. Text Chunks

Regular text responses that should be displayed in the chat interface.

```
0:"Hello "
0:"world"
```

On the front-end, these should be concatenated to form "Hello world".

#### 2. Source Nodes

References to source documents that were used to generate the response.

```
8:[{"type":"sources","data":{"nodes":[{"text":"Source content here","metadata":{"file_name":"document.pdf","page":5}}]}}]
```

#### 3. Suggested Questions

Follow-up questions suggested by the AI (only sent if enabled in config).

```
8:[{"type":"suggested_questions","data":["What is X?","Tell me more about Y","How does Z work?"]}]
```

#### 4. Error Messages

```
3:"An error occurred processing your request"
```

## Frontend Implementation Guide

1. **Create a persistent connection** to receive the streaming response
2. **Parse each chunk** according to its prefix:
   - `0:` - Text content to display incrementally
   - `8:` - JSON data to process (sources, suggestions)
   - `3:` - Error messages to display

3. **Handle text streaming** by appending each token to your display
4. **Handle data events** by parsing the JSON and rendering appropriate UI components (source citations, suggestion buttons)
5. **Handle errors** by showing appropriate error messages

### Example Implementation

```javascript
async function streamFromAPI(projectId, messages, config) {
  const response = await fetch(`/projects/${projectId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, config }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    
    // Process complete lines
    let lineEnd;
    while ((lineEnd = buffer.indexOf('\n')) !== -1) {
      const line = buffer.slice(0, lineEnd);
      buffer = buffer.slice(lineEnd + 1);
      
      if (line.startsWith('0:')) {
        // Text event
        const textChunk = JSON.parse(line.slice(2));
        appendToChat(textChunk);
      } else if (line.startsWith('8:')) {
        // Data event
        const dataStr = line.slice(2);
        const dataArray = JSON.parse(dataStr);
        if (dataArray.length > 0) {
          const data = dataArray[0];
          
          if (data.type === 'sources') {
            displaySources(data.data.nodes);
          } else if (data.type === 'suggested_questions') {
            displaySuggestedQuestions(data.data);
          }
        }
      } else if (line.startsWith('3:')) {
        // Error event
        const error = JSON.parse(line.slice(2));
        displayError(error);
      }
    }
  }
}
```

## Important Implementation Details

1. The stream is designed to deliver tokens in real-time, allowing for a typing-like effect.
2. Source nodes and suggested questions are delivered separately from the text content.
3. Source nodes include the original text and metadata that should be used to create citations.
4. The UI should accumulate text chunks while having separate areas for displaying sources and suggestions.
