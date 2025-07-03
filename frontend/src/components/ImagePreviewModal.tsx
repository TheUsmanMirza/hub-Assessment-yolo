'use client';

import { useEffect, useState, useRef } from 'react';
import { X } from 'lucide-react';
import { ImageData, BoundingBox } from '@/types/dataset';
import { DatasetAPI } from '@/services/api';

interface ImagePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageData: ImageData | null;
  datasetName: string;
}

// Color palette for different classes
const COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
  '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
];

export default function ImagePreviewModal({ isOpen, onClose, imageData, datasetName }: ImagePreviewModalProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (isOpen) {
      setImageLoaded(false);
    }
  }, [isOpen, imageData]);

  const handleImageLoad = () => {
    if (imageRef.current) {
      setImageDimensions({
        width: imageRef.current.naturalWidth,
        height: imageRef.current.naturalHeight
      });
      setImageLoaded(true);
    }
  };

  const convertYoloToPixel = (bbox: number[], imgWidth: number, imgHeight: number) => {
    const [x_center, y_center, width, height] = bbox;
    
    // Convert from normalized coordinates to pixel coordinates
    const x = (x_center - width / 2) * imgWidth;
    const y = (y_center - height / 2) * imgHeight;
    const w = width * imgWidth;
    const h = height * imgHeight;
    
    return { x, y, width: w, height: h };
  };

  const getColorForClass = (classId: number) => {
    return COLORS[classId % COLORS.length];
  };

  if (!isOpen || !imageData) return null;

  const imageUrl = DatasetAPI.getImageUrl(datasetName, imageData.image_name);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 p-4">
      <div className="relative w-full max-w-6xl h-full max-h-[90vh] bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-gray-50 flex-shrink-0">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">📸</span>
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">{imageData.image_name}</h2>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>{imageData.labels.length} annotation{imageData.labels.length !== 1 ? 's' : ''}</span>
                <span>•</span>
                <span>{imageDimensions.width} × {imageDimensions.height} pixels</span>
              </div>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 rounded-md text-gray-700 hover:text-red-600 hover:bg-red-50 transition-colors"
            title="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Image Container */}
        <div className="flex-1 overflow-auto bg-gradient-to-br from-gray-100 to-gray-200 min-h-0">
          <div className="flex items-center justify-center min-h-full p-4">
            <div className="relative inline-block bg-white rounded-lg shadow-lg p-2">
              {!imageLoaded && (
                <div className="w-96 h-64 bg-gray-200 rounded-lg flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
              )}
              <img
                ref={imageRef}
                src={imageUrl}
                alt={imageData.image_name}
                onLoad={handleImageLoad}
                className={`rounded-lg transition-opacity duration-300 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
                style={{
                  maxWidth: '800px',
                  maxHeight: '600px',
                  width: 'auto',
                  height: 'auto'
                }}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  if (!target.src.includes('placeholder')) {
                    target.src = '/images/placeholder.svg';
                    setImageLoaded(true); // Show placeholder
                  }
                }}
              />
              
              {/* Bounding Box Overlays */}
              {imageLoaded && imageData.labels.map((label: BoundingBox, index: number) => {
                const { x, y, width, height } = convertYoloToPixel(
                  label.bbox,
                  imageDimensions.width,
                  imageDimensions.height
                );
                
                // Calculate scale factor based on displayed image size vs natural size
                const displayedImage = imageRef.current;
                const scaleX = displayedImage ? displayedImage.clientWidth / imageDimensions.width : 1;
                const scaleY = displayedImage ? displayedImage.clientHeight / imageDimensions.height : 1;
                
                const color = getColorForClass(label.class);
                
                return (
                  <div
                    key={index}
                    className="absolute border-3 pointer-events-none rounded-sm"
                    style={{
                      left: `${x * scaleX + 8}px`, // +8 for padding
                      top: `${y * scaleY + 8}px`,   // +8 for padding
                      width: `${width * scaleX}px`,
                      height: `${height * scaleY}px`,
                      borderColor: color,
                      backgroundColor: `${color}15`,
                      boxShadow: `0 0 0 2px ${color}`,
                    }}
                  >
                    {/* Class Label */}
                    <div
                      className="absolute -top-8 left-0 px-3 py-1 text-sm font-bold text-white rounded-md shadow-lg"
                      style={{ 
                        backgroundColor: color,
                      }}
                    >
                      Class {label.class}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer with Enhanced Legend */}
        <div className="p-4 border-t border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50 flex-shrink-0">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-bold text-gray-900 mb-3">Detected Objects</h3>
              <div className="flex flex-wrap gap-2">
                {Array.from(new Set(imageData.labels.map(label => label.class))).map(classId => (
                  <div
                    key={classId}
                    className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-bold text-white shadow-md transform hover:scale-105 transition-transform"
                    style={{ backgroundColor: getColorForClass(classId) }}
                  >
                    <div className="w-3 h-3 rounded-full bg-white bg-opacity-30"></div>
                    <span>Class {classId}</span>
                    <span className="bg-white bg-opacity-20 px-2 py-1 rounded-full text-xs">
                      {imageData.labels.filter(label => label.class === classId).length}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="text-right flex-shrink-0">
              <div className="text-sm text-gray-600 space-y-1">
                <div><strong>Total Objects:</strong> {imageData.labels.length}</div>
                <div><strong>Classes:</strong> {Array.from(new Set(imageData.labels.map(label => label.class))).length}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 