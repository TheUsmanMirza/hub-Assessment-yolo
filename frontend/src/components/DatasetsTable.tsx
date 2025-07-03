'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Dataset } from '@/types/dataset';
import { DatasetAPI } from '@/services/api';
import { Calendar, Image, AlertCircle, Loader2 } from 'lucide-react';

interface DatasetsTableProps {
  refreshTrigger?: number;
}

export default function DatasetsTable({ refreshTrigger }: DatasetsTableProps) {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatasets();
  }, [refreshTrigger]);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await DatasetAPI.getAllDatasets();
      setDatasets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch datasets');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | any) => {
    try {
      let date: Date;
      
      // Handle BSON date format from MongoDB
      if (typeof dateString === 'object' && dateString.$date) {
        date = new Date(dateString.$date);
      } 
      // Handle regular ISO string
      else if (typeof dateString === 'string') {
        date = new Date(dateString);
      }
      // Handle direct date object
      else {
        date = new Date(dateString);
      }
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Invalid Date';
      }
      
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      console.error('Date parsing error:', error, 'Input:', dateString);
      return 'Invalid Date';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Loading datasets...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <AlertCircle className="h-8 w-8 text-red-500" />
        <span className="ml-2 text-red-600">{error}</span>
        <button
          onClick={fetchDatasets}
          className="ml-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  if (datasets.length === 0) {
    return (
      <div className="text-center py-12">
        <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No datasets found</h3>
        <p className="text-gray-500">Upload your first dataset to get started.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">Datasets</h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Dataset Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Images
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created At
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {datasets.map((dataset) => (
              <tr key={dataset._id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <Link 
                    href={`/datasets/${encodeURIComponent(dataset.name)}`}
                    className="text-blue-600 hover:text-blue-800 font-medium hover:underline"
                  >
                    {dataset.name}
                  </Link>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(dataset.status)}`}>
                    {dataset.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div className="flex items-center">
                    <Image className="h-4 w-4 text-gray-400 mr-1" />
                    {dataset.total_images}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                    {formatDate(dataset.created_at)}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 