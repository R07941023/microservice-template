import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('query');
  const authorizationHeader = request.headers.get('Authorization'); // Get Authorization header

  if (!query) {
    return NextResponse.json({ detail: `Query parameter 'query' is required.` }, { status: 400 });
  }

  try {
    const headers: HeadersInit = {};
    if (authorizationHeader) {
      headers['Authorization'] = authorizationHeader;
    }

    // Forward the request to the internal backend service via Kong
    const backendUrl = `http://kong:8000/search/${query}`
    const backendResponse = await fetch(backendUrl, {
      headers: headers, // Pass headers to backend fetch
      cache: 'no-store',
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json();
      return NextResponse.json(errorData, { status: backendResponse.status });
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error forwarding request to backend:', error);
    return NextResponse.json({ detail: 'Internal Server Error' }, { status: 500 });
  }
}

