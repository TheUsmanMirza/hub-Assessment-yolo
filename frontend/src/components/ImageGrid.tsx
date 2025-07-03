'use client';

import { useState } from 'react';
import { ImageData } from '@/types/dataset';
import { DatasetAPI } from '@/services/api';
import { Eye, Tag, ChevronLeft, ChevronRight } from 'lucide-react';
import ImagePreviewModal from './ImagePreviewModal';

interface ImageGridProps {
  images: ImageData[];
  datasetName: string;
}

const IMAGES_PER_PAGE = 10;

export default function ImageGrid({ images, datasetName }: ImageGridProps) {
  const [selectedImage, setSelectedImage] = useState<ImageData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(images.length / IMAGES_PER_PAGE);
  const startIndex = (currentPage - 1) * IMAGES_PER_PAGE;
  const endIndex = startIndex + IMAGES_PER_PAGE;
  const currentImages = images.slice(startIndex, endIndex);

  const handleImageClick = (image: ImageData) => {
    setSelectedImage(image);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedImage(null);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll to top when changing pages
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handlePrevious = () => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      handlePageChange(currentPage + 1);
    }
  };

  // Generate page numbers to show
  const getPageNumbers = () => {
    const delta = 2; // Number of pages to show on each side of current page
    const range = [];
    const rangeWithDots = [];

    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i);
    }

    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...');
    } else {
      rangeWithDots.push(1);
    }

    rangeWithDots.push(...range);

    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages);
    } else if (totalPages > 1) {
      rangeWithDots.push(totalPages);
    }

    return rangeWithDots.filter((item, index, array) => array.indexOf(item) === index);
  };

  if (images.length === 0) {
    return (
      <div className="text-center py-12">
        <Eye className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No images found</h3>
        <p className="text-gray-500">This dataset doesn't contain any images.</p>
      </div>
    );
  }

  return (
    <>
      {/* Pagination Info */}
      <div className="flex items-center justify-between mb-6">
        <div className="text-sm text-gray-600">
          Showing {startIndex + 1}-{Math.min(endIndex, images.length)} of {images.length} images
        </div>
        <div className="text-sm text-gray-600">
          Page {currentPage} of {totalPages}
        </div>
      </div>

      {/* Image Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        {currentImages.map((image, index) => (
          <div
            key={startIndex + index}
            className="group bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => handleImageClick(image)}
          >
            {/* Image Container */}
            <div className="relative aspect-square bg-gray-100">
              {/* Base Image - Always Visible */}
              <img
                src={DatasetAPI.getImageUrl(datasetName, image.image_name)}
                alt={image.image_name}
                className="w-full h-full absolute object-cover group-hover:scale-105 transition-transform duration-200"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  // Try alternative image paths if the first one fails
                  const currentSrc = target.src;
                  if (!currentSrc.includes('placeholder')) {
                    // First fallback: try with .JPG extension
                    const altUrl = DatasetAPI.getImageUrl(datasetName, image.image_name.replace('.jpg', '.JPG'));
                    if (currentSrc !== altUrl) {
                      target.src = altUrl;
                      return;
                    }
                    // Final fallback: placeholder
                    target.src = '/images/placeholder.svg';
                  }
                }}
              />
              
              {/* Hover Overlay - Only visible on hover */}
              <div className="absolute inset-0 bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <Eye className="h-8 w-8 text-white" />
                </div>
              </div>

              {/* Annotation count badge - Always visible */}
              {image.labels.length > 0 && (
                <div className="absolute top-2 right-2 bg-blue-500 text-white text-xs font-medium px-2 py-1 rounded-full flex items-center space-x-1">
                  <Tag className="h-3 w-3" />
                  <span>{image.labels.length}</span>
                </div>
              )}

              {/* Image index badge - Always visible */}
              <div className="absolute top-2 left-2 bg-gray-900 bg-opacity-75 text-white text-xs font-medium px-2 py-1 rounded">
                #{startIndex + index + 1}
              </div>
            </div>

            {/* Image Info */}
            <div className="p-3">
              <h3 className="font-medium text-gray-900 text-sm truncate" title={image.image_name}>
                {image.image_name}
              </h3>
              <p className="text-xs text-gray-500 mt-1">
                {image.labels.length} annotation{image.labels.length !== 1 ? 's' : ''}
              </p>
              
              {/* Class preview */}
              {image.labels.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {Array.from(new Set(image.labels.map(label => label.class)))
                    .slice(0, 3)
                    .map(classId => (
                      <span
                        key={classId}
                        className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded"
                      >
                        Class {classId}
                      </span>
                    ))}
                  {Array.from(new Set(image.labels.map(label => label.class))).length > 3 && (
                    <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                      +{Array.from(new Set(image.labels.map(label => label.class))).length - 3}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="mt-8 flex items-center justify-center space-x-2">
          {/* Previous Button */}
          <button
            onClick={handlePrevious}
            disabled={currentPage === 1}
            className={`
              flex items-center px-3 py-2 text-sm font-medium rounded-md
              ${currentPage === 1 
                ? 'text-gray-400 cursor-not-allowed' 
                : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
              }
            `}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </button>

          {/* Page Numbers */}
          <div className="flex items-center space-x-1">
            {getPageNumbers().map((pageNum, index) => (
              pageNum === '...' ? (
                <span key={index} className="px-3 py-2 text-gray-500">...</span>
              ) : (
                <button
                  key={index}
                  onClick={() => typeof pageNum === 'number' && handlePageChange(pageNum)}
                  className={`
                    px-3 py-2 text-sm font-medium rounded-md
                    ${pageNum === currentPage
                      ? 'bg-blue-500 text-white'
                      : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                    }
                  `}
                >
                  {pageNum}
                </button>
              )
            ))}
          </div>

          {/* Next Button */}
          <button
            onClick={handleNext}
            disabled={currentPage === totalPages}
            className={`
              flex items-center px-3 py-2 text-sm font-medium rounded-md
              ${currentPage === totalPages 
                ? 'text-gray-400 cursor-not-allowed' 
                : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
              }
            `}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </button>
        </div>
      )}

      {/* Pagination Summary */}
      {totalPages > 1 && (
        <div className="mt-4 text-center text-sm text-gray-500">
          {IMAGES_PER_PAGE} images per page • Jump to page:{' '}
          <select
            value={currentPage}
            onChange={(e) => handlePageChange(Number(e.target.value))}
            className="ml-1 border border-gray-300 rounded px-2 py-1 text-sm"
          >
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
              <option key={page} value={page}>
                {page}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Image Preview Modal */}
      <ImagePreviewModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        imageData={selectedImage}
        datasetName={datasetName}
      />
    </>
  );
} 