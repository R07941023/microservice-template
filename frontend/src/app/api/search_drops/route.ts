import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('query');

  if (!query) {
    return NextResponse.json({ detail: 'Query parameter \'query\' is required.' }, { status: 400 });
  }

  try {
    // Forward the request to the internal backend service
    const backendResponse = await fetch(`http://ms-maple-drop-repo:8000/search_drops?query=${query}`);
    console.log(backendResponse)

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
