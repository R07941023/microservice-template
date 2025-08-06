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
      headers['Authorization'] = authorizationHeader; // Add Authorization header if present
    }

    // Forward the request to the internal backend service
    // The backend service name is 'ms-maple-drop-repo' as defined in docker-compose.yml
    // Docker's internal DNS will resolve this hostname to the correct container IP.
    const backendUrl = `http://ms-search-aggregator:8000/api/search/drops-augmented?name=${query}`
    const backendResponse = await fetch(backendUrl, {
      headers: headers, // Pass headers to backend fetch
      cache: 'no-store',
    });

    console.log(backendResponse);

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

