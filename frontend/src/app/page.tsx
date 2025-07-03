'use client';

import { useState } from 'react';
import UploadZone from '@/components/UploadZone';
import DatasetsTable from '@/components/DatasetsTable';
import { Database, Upload } from 'lucide-react';

export default function HomePage() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    // Trigger refresh of datasets table
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-3">
            <Database className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">YOLO Dataset Manager</h1>
              <p className="text-gray-600">Upload and manage your YOLO datasets</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Upload Section */}
          <section>
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-2">
                <Upload className="h-5 w-5 text-gray-600" />
                <h2 className="text-xl font-semibold text-gray-900">Upload Dataset</h2>
              </div>
            </div>
            
            <UploadZone onUploadSuccess={handleUploadSuccess} />
          </section>

          {/* Datasets Section */}
          <section>
            <DatasetsTable refreshTrigger={refreshTrigger} />
          </section>
        </div>
      </main>
    </div>
  );
}
