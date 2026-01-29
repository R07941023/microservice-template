import { NextRequest, NextResponse } from 'next/server';

export async function PUT(request: NextRequest, context: unknown) {
  const ctx = context as { params: { id: string | string[] } };
  const id = Array.isArray(ctx.params.id) ? ctx.params.id[0] : ctx.params.id;

  if (!id) {
    return NextResponse.json({ detail: 'Drop ID is required' }, { status: 400 });
  }

  const body = await request.json();
  const authorizationHeader = request.headers.get('Authorization');

  try {
    const backendUrl = `http://kong:8000/ms-drop-repo/update_drop/${id}`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (authorizationHeader) {
      headers['Authorization'] = authorizationHeader;
    }

    const response = await fetch(backendUrl, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { detail: errorData.detail || 'Error updating data in backend' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('Error forwarding request to backend:', error);
    return NextResponse.json({ detail: 'Internal Server Error' }, { status: 500 });
  }
}
