import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const AttendancePage = () => {
  const { user } = useAuth();

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        <h1 className="text-2xl font-semibold text-gray-900">Mark Attendance</h1>
        <p className="mt-2 text-sm text-gray-600">
          Use your camera and location to mark today's attendance
        </p>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 mt-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              📷 Camera & Location Attendance
            </h3>
            <p className="text-gray-600 mb-6">
              The attendance marking interface with camera and location capture will be available here.
            </p>
            
            {!user?.has_face_encoding && (
              <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-md">
                <p className="text-amber-800">
                  ⚠️ Please register your face in your profile before marking attendance.
                </p>
              </div>
            )}
            
            <div className="text-sm text-gray-500">
              <p>Features will include:</p>
              <ul className="mt-2 space-y-1">
                <li>• Live camera feed for selfie capture</li>
                <li>• Automatic location detection</li>
                <li>• Face recognition verification</li>
                <li>• Real-time attendance submission</li>
                <li>• Status confirmation</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttendancePage;