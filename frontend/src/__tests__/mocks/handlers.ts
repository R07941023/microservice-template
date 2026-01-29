import { http, HttpResponse, delay } from 'msw';

// Sample drop data for testing
export const mockDropData = [
  {
    id: '1',
    dropperid: 1001,
    itemid: 2001,
    minimum_quantity: 1,
    maximum_quantity: 5,
    questid: 0,
    chance: 0.5,
    dropper_name: 'Test Monster',
    item_name: 'Test Item',
  },
  {
    id: '2',
    dropperid: 1002,
    itemid: 2002,
    minimum_quantity: 1,
    maximum_quantity: 10,
    questid: 100,
    chance: 0.25,
    dropper_name: 'Test Monster 2',
    item_name: 'Test Item 2',
  },
];

export const mockNames = ['Test Monster', 'Test Item', 'Another Monster', 'Another Item'];

export const mockAlternativeIds = [
  { id: 1001, type: 'mob', image_exist: true, drop_exist: true },
  { id: 2001, type: 'item', image_exist: true, drop_exist: false },
];

export const handlers = [
  // Search drops endpoint
  http.get('/api/search_drops', async ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('query');

    await delay(100);

    if (query === 'empty') {
      return HttpResponse.json({ data: [] });
    }

    if (query === 'error') {
      return HttpResponse.json({ detail: 'Search failed' }, { status: 500 });
    }

    return HttpResponse.json({ data: mockDropData });
  }),

  // Names autocomplete endpoint
  http.get('/api/names/all', async () => {
    await delay(50);
    return HttpResponse.json({ names: mockNames });
  }),

  // Existence check endpoint
  http.get('/api/existence-check/:name', async () => {
    await delay(50);
    return HttpResponse.json({ results: mockAlternativeIds });
  }),

  // Chat endpoint with streaming
  http.post('/api/chat', async ({ request }) => {
    const body = (await request.json()) as { prompt?: string };
    const prompt = body.prompt;

    if (!prompt) {
      return HttpResponse.text('Prompt is required', { status: 400 });
    }

    // Simulate streaming response
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        const chunks = ['Hello', ', ', 'this ', 'is ', 'a ', 'test ', 'response.'];
        for (const chunk of chunks) {
          controller.enqueue(encoder.encode(chunk));
          await delay(10);
        }
        controller.close();
      },
    });

    return new HttpResponse(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
      },
    });
  }),

  // Update drop endpoint
  http.put('/api/update_drop/:id', async ({ request, params }) => {
    const id = params.id;
    const body = await request.json();

    await delay(50);

    if (id === 'error') {
      return HttpResponse.json({ detail: 'Update failed' }, { status: 500 });
    }

    return HttpResponse.json({ id, ...body });
  }),
];
