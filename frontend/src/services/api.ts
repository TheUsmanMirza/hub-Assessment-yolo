import { Dataset, ImageData, UploadResponse } from '@/types/dataset';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class DatasetAPI {
  static async uploadDataset(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/datasets/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async getAllDatasets(): Promise<Dataset[]> {
    const response = await fetch(`${API_BASE_URL}/datasets/`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch datasets: ${response.statusText}`);
    }

    return response.json();
  }

  static async getDatasetImages(datasetName: string): Promise<ImageData[]> {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetName}/images`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch images: ${response.statusText}`);
    }

    return response.json();
  }

  static getImageUrl(datasetName: string, imageName: string): string {
    // Use the frontend's image proxy API to avoid CORS issues
    return `/api/images/datasets/${datasetName}/image/${imageName}`;
  }
} 