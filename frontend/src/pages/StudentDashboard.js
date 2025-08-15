import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ClipboardDocumentListIcon, CalendarIcon, UserIcon } from '@heroicons/react/24/outline';

const StudentDashboard = () => {
  const { user } = useAuth();

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        <h1 className="text-2xl font-semibold text-gray-900">Welcome back, {user?.username}!</h1>
        <p className="mt-2 text-sm text-gray-600">Manage your attendance and view your records</p>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 mt-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Mark Attendance Card */}
          <Link
            to="/attendance"
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClipboardDocumentListIcon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Mark Attendance
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      Check In Now
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <span className="font-medium text-primary-600">Mark today's attendance →</span>
              </div>
            </div>
          </Link>

          {/* Attendance History Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CalendarIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Attendance History
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      View Records
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <span className="text-gray-600">Check your attendance history</span>
              </div>
            </div>
          </div>

          {/* Profile Card */}
          <Link
            to="/profile"
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Profile Settings
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      Update Profile
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <span className="font-medium text-blue-600">Manage your profile →</span>
              </div>
            </div>
          </Link>
        </div>

        {/* Quick Stats */}
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  {user?.has_face_encoding ? (
                    <span className="text-green-600">✅ Face registered - Ready to mark attendance</span>
                  ) : (
                    <span className="text-amber-600">⚠️ Please register your face in profile to mark attendance</span>
                  )}
                </p>
                {user?.company && (
                  <p className="text-sm text-gray-600 mt-2">
                    Company: <span className="font-medium">{user.company.name}</span>
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;