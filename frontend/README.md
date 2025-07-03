# YOLO Dataset Manager Frontend

A modern Next.js frontend for managing YOLO datasets with image preview and bounding box visualization.

## Features

- **Dataset Upload**: Drag-and-drop interface for uploading ZIP files containing YOLO datasets
- **Dataset Management**: View all uploaded datasets in a table format
- **Image Gallery**: Browse all images within a dataset
- **Image Preview**: Click on any image to view it with annotated bounding boxes
- **Bounding Box Visualization**: YOLO annotations are converted and displayed as colored overlays
- **Zoom Controls**: Zoom in/out on images for detailed inspection
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Node.js 18.17.0 or higher
- FastAPI backend running on `http://localhost:8000` (or configure `NEXT_PUBLIC_API_URL`)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables (optional):
```bash
# Create .env.local file with:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## API Integration

The frontend expects the following backend endpoints:

- `POST /datasets/upload` - Upload dataset ZIP file
- `GET /datasets/` - List all datasets
- `GET /datasets/{name}/images` - Get images for a specific dataset
- `GET /static/{dataset}/{image}` - Serve image files

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home page with upload and datasets table
│   ├── datasets/          # Dataset detail pages
│   └── api/               # API routes for image proxying
├── components/            # React components
│   ├── UploadZone.tsx    # File upload component
│   ├── DatasetsTable.tsx # Datasets listing table
│   ├── ImageGrid.tsx     # Image gallery component
│   └── ImagePreviewModal.tsx # Image viewer with bounding boxes
├── services/             # API service layer
├── types/                # TypeScript type definitions
└── public/               # Static assets
```

## Usage

1. **Upload a Dataset**: Drag and drop a ZIP file containing YOLO format data onto the upload zone
2. **Browse Datasets**: View all uploaded datasets in the table on the home page
3. **View Images**: Click on a dataset name to see all its images
4. **Preview with Annotations**: Click on any image to view it with bounding box overlays
5. **Zoom and Pan**: Use the zoom controls to inspect images in detail

## YOLO Format Support

The application supports YOLO format annotations where:
- Images are in JPG format
- Annotations are in TXT files with the same name as the image
- Each line in the annotation file represents one object: `class x_center y_center width height`
- Coordinates are normalized (0-1 range)

## Technologies Used

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **React Dropzone** - File upload component
