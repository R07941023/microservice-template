import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('query');
  const authorizationHeader = request.headers.get('Authorization');
  const devModeHeader = request.headers.get('X-Dev-Mode'); // Get X-Dev-Mode header

  if (!query) {
    return NextResponse.json({ detail: `Query parameter 'query' is required.` }, { status: 400 });
  }

  try {
    const headers: HeadersInit = {};
    if (authorizationHeader) {
      headers['Authorization'] = authorizationHeader;
    }

    let backendUrl: string;

    if (devModeHeader === 'true') {
      // If dev mode is on, bypass Kong and hit ms-search-aggregator directly for drops-augmented
      backendUrl = `http://ms-search-aggregator:8000/api/search/drops-augmented?name=${query}`;
      console.log(`[Dev Mode ON] Routing to ms-search-aggregator: ${backendUrl}`);
    } else {
      // Default behavior: forward to Kong
      backendUrl = `http://kong:8000/search/${query}`;
      console.log(`[Dev Mode OFF] Routing to Kong: ${backendUrl}`);
    }
    
    const backendResponse = await fetch(backendUrl, {
      method: 'GET', // Explicitly set GET method
      headers: headers,
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

