import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  try {
    // Await params before using them (Next.js 15 requirement)
    const resolvedParams = await params;
    
    // Reconstruct the full path
    const imagePath = resolvedParams.path.join('/');
    
    // Construct the backend URL for the image using the correct endpoint pattern
    const backendUrl = `${API_BASE_URL}/${imagePath}`;
    
    // Fetch the image from the backend
    const response = await fetch(backendUrl);
    
    if (!response.ok) {
      return new NextResponse('Image not found', { status: 404 });
    }
    
    // Get the image data and content type
    const imageBuffer = await response.arrayBuffer();
    const contentType = response.headers.get('content-type') || 'image/jpeg';
    
    // Return the image with appropriate headers
    return new NextResponse(imageBuffer, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    });
  } catch (error) {
    console.error('Error proxying image:', error);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
} 