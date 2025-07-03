export interface BoundingBox {
  class: number;
  bbox: [number, number, number, number]; // [x, y, width, height] in normalized coordinates
}

export interface ImageData {
  image_name: string;
  labels: BoundingBox[];
}

export interface Dataset {
  _id: string;
  name: string;
  status: string;
  created_at: string;
  total_images: number;
  images?: ImageData[];
}

export interface UploadResponse {
  message: string;
} 