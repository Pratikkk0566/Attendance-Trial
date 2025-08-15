import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const ProfilePage = () => {
  const { user } = useAuth();

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        <h1 className="text-2xl font-semibold text-gray-900">Profile Settings</h1>
        <p className="mt-2 text-sm text-gray-600">
          Manage your profile and face registration
        </p>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 mt-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Profile Information */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Username</label>
                  <p className="mt-1 text-sm text-gray-900">{user?.username}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Role</label>
                  <p className="mt-1 text-sm text-gray-900 capitalize">
                    {user?.role?.replace('_', ' ')}
                  </p>
                </div>
                {user?.company && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Company</label>
                    <p className="mt-1 text-sm text-gray-900">{user.company.name}</p>
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-gray-700">Face Registration</label>
                  <p className="mt-1 text-sm">
                    {user?.has_face_encoding ? (
                      <span className="text-green-600">✅ Face registered</span>
                    ) : (
                      <span className="text-amber-600">⚠️ Face not registered</span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Face Registration */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Face Registration</h3>
              <div className="text-center">
                <div className="text-gray-600 mb-6">
                  <p>Register or update your face for attendance verification.</p>
                </div>
                
                <div className="text-sm text-gray-500">
                  <p>Face registration interface will include:</p>
                  <ul className="mt-2 space-y-1">
                    <li>• Live camera preview</li>
                    <li>• Face detection guidance</li>
                    <li>• Capture and verification</li>
                    <li>• Face encoding storage</li>
                  </ul>
                </div>
                
                <button
                  disabled
                  className="mt-6 bg-primary-600 text-white px-4 py-2 rounded-md opacity-50 cursor-not-allowed"
                >
                  Register Face (Coming Soon)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;