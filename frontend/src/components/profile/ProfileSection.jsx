import React, { useState, useEffect } from 'react';
import { User, Mail, Building, Key, History } from 'lucide-react';
// import ActivityHistory from './ActivityHistory';

const ProfileSection = ({ user, onBack, onLogout }) => {
  const [profile, setProfile] = useState({
    displayName: user.displayName || '',
    email: user.email || '',
    company: '',
    role: ''
  });
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [activeTab, setActiveTab] = useState('profile'); // 'profile' or 'history'

  useEffect(() => {
    fetchProfileData();
  }, [user.uid]);

  const fetchProfileData = async () => {
    try {
      const response = await fetch(`/api/profile/${user.uid}`);
      if (response.ok) {
        const data = await response.json();
        setProfile(prev => ({
          ...prev,
          ...data
        }));
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await fetch('/api/profile/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          uid: user.uid,
          ...profile
        }),
      });

      if (response.ok) {
        setSuccessMessage('Profile updated successfully');
        setIsEditing(false);
      } else {
        throw new Error('Failed to update profile');
      }
    } catch (err) {
      setError('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 
                      transition-colors font-medium rounded-lg hover:bg-gray-100"
          >
            Back to Generator
          </button>

          {process.env.NODE_ENV !== 'production' && (
              <button
                onClick={async () => {
                  try {
                    const response = await fetch('/api/reset-database', { method: 'POST' });
                    if (response.ok) {
                      alert('Database tables reset successfully. Please refresh the page.');
                    } else {
                      alert('Failed to reset database tables.');
                    }
                  } catch (err) {
                    console.error(err);
                    alert('Error resetting database tables.');
                  }
                }}
                className="mt-4 px-4 py-2 bg-red-100 text-red-700 rounded-lg"
              >
                Reset Database Tables (Testing Only)
              </button>
            )}
        </div>
        <div className="flex items-center space-x-4">
          {isEditing ? (
            <>
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 
                          rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                form="profile-form"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg 
                          hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg 
                          hover:bg-blue-700 transition-colors"
              >
                Edit Profile
              </button>
              <button
                onClick={onLogout}
                className="px-4 py-2 text-red-600 hover:text-red-700 
                          transition-colors font-medium rounded-lg hover:bg-red-50"
              >
                Log Out
              </button>
            </>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-6 py-4 text-sm font-medium ${
                activeTab === 'profile'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <User className="inline-block h-4 w-4 mr-2" />
              Profile
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-6 py-4 text-sm font-medium ${
                activeTab === 'history'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <History className="inline-block h-4 w-4 mr-2" />
              Activity History
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'profile' ? (
            <form id="profile-form" onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                {/* Display Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <span className="flex items-center">
                      <User className="h-4 w-4 mr-2" />
                      Display Name
                    </span>
                  </label>
                  <input
                    type="text"
                    value={profile.displayName}
                    onChange={(e) => setProfile({ ...profile, displayName: e.target.value })}
                    disabled={!isEditing}
                    className={`w-full px-4 py-2 rounded-lg border ${
                      isEditing ? 'border-gray-300' : 'border-gray-200 bg-gray-50'
                    }`}
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <span className="flex items-center">
                      <Mail className="h-4 w-4 mr-2" />
                      Email
                    </span>
                  </label>
                  <input
                    type="email"
                    value={profile.email}
                    disabled
                    className="w-full px-4 py-2 rounded-lg border border-gray-200 bg-gray-50"
                  />
                </div>

                {/* Company */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <span className="flex items-center">
                      <Building className="h-4 w-4 mr-2" />
                      Company
                    </span>
                  </label>
                  <input
                    type="text"
                    value={profile.company}
                    onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                    disabled={!isEditing}
                    className={`w-full px-4 py-2 rounded-lg border ${
                      isEditing ? 'border-gray-300' : 'border-gray-200 bg-gray-50'
                    }`}
                  />
                </div>

                {/* Role */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <span className="flex items-center">
                      <Key className="h-4 w-4 mr-2" />
                      Role
                    </span>
                  </label>
                  <input
                    type="text"
                    value={profile.role}
                    onChange={(e) => setProfile({ ...profile, role: e.target.value })}
                    disabled={!isEditing}
                    className={`w-full px-4 py-2 rounded-lg border ${
                      isEditing ? 'border-gray-300' : 'border-gray-200 bg-gray-50'
                    }`}
                  />
                </div>
              </div>

              {error && (
                <div className="text-red-500 text-sm">{error}</div>
              )}

              {successMessage && (
                <div className="text-green-500 text-sm">{successMessage}</div>
              )}
            </form>
          ) : (
            <ActivityHistory user={user} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileSection;