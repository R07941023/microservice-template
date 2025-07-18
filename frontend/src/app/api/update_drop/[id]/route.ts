import { NextResponse } from 'next/server';

export async function PUT(request: Request, { params }: { params: { id: string } }) {
  const { id } = params;
  const body = await request.json();

  if (!id) {
    return NextResponse.json({ detail: 'Drop ID is required' }, { status: 400 });
  }

  try {
    // The backend service name is 'ms-maple-drop-repo' as defined in docker-compose.yml
    // Docker's internal DNS will resolve this hostname to the correct container IP.
    const backendUrl = `http://ms-maple-drop-repo:8000/update_drop/${id}`;
    
    const response = await fetch(backendUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json({ detail: errorData.detail || 'Error updating data in backend' }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });

  } catch (error) {
    console.error('Error forwarding request to backend:', error);
    return NextResponse.json({ detail: 'Internal Server Error' }, { status: 500 });
  }
}
