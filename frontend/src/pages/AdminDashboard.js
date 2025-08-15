import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const AdminDashboard = () => {
  const { user } = useAuth();

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        <h1 className="text-2xl font-semibold text-gray-900">
          Admin Dashboard - {user?.role?.replace('_', ' ').toUpperCase()}
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          Manage attendance records and view analytics
        </p>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 mt-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              🚧 Admin Dashboard Coming Soon
            </h3>
            <p className="text-gray-600">
              The admin dashboard with filtering, analytics, and export functionality will be available here.
            </p>
            <div className="mt-6 text-sm text-gray-500">
              <p>Features will include:</p>
              <ul className="mt-2 space-y-1">
                <li>• View all attendance records</li>
                <li>• Filter by date, company, student, status</li>
                <li>• Export to Excel</li>
                <li>• Real-time analytics</li>
                <li>• Attendance verification</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;