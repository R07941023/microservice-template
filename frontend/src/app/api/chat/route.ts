import { NextRequest } from 'next/server';

const ORCHESTRATOR_URL = process.env.LLM_ORCHESTRATOR_URL || 'http://kong:8000/ms-llm-orchestrator/stream-chat';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    type UIMessagePart = { type: string; text?: string };
    type UIMessage = { role: string; parts: UIMessagePart[] };
    const messages: UIMessage[] = body.messages ?? [];
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
    const prompt = lastUserMessage?.parts.find(p => p.type === 'text')?.text;
    const authorizationHeader = req.headers.get('Authorization') || '';
    if (!prompt) {
      return new Response('Prompt is required', { status: 400 });
    }

    // Forward the request to the Python backend
    const response = await fetch(ORCHESTRATOR_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authorizationHeader,
      },
      body: JSON.stringify({ prompt: prompt }),
    });

    // Check if the request to the backend was successful
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error from orchestrator service: ${errorText}`);
      return new Response(errorText, { status: response.status });
    }

    // The body from the fetch response is already a ReadableStream.
    // We can pipe it directly to the client.
    if (response.body) {
      return new Response(response.body, {
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
        },
      });
    } else {
      return new Response('Empty response body from the service', { status: 500 });
    }

  } catch (error) {
    console.error('Error in chat API route:', error);
    return new Response('An internal server error occurred.', { status: 500 });
  }
}
