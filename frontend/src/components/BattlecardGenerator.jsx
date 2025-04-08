import React, { useState } from 'react';
import ScraperForm from './ScraperForm';
import BattlecardList from './BattlecardList';
import LoadingSpinner from './LoadingSpinner';
import AuthModal from './auth/AuthModal';
import ProfileSection from './profile/ProfileSection';
import { ChevronDown } from 'lucide-react';

function BattlecardGenerator({ 
  user, 
  handleLogout, 
  showAuthModal, 
  setShowAuthModal, 
  openAuthModal, 
  authView, 
  battlecards, 
  setBattlecards, 
  loading, 
  setLoading, 
  error, 
  setError 
}) {
  const [showProfile, setShowProfile] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-2xl md:text-4xl font-bold text-gray-800">
            {showProfile ? 'Profile Management' : 'Battlecard Generator'}
          </h1>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <button
                onClick={() => setShowProfile(!showProfile)}
                className="inline-flex items-center px-4 py-2 text-gray-700 hover:text-gray-900 
                          transition-colors text-sm font-medium rounded-lg hover:bg-gray-100"
              >
                {user.email}
                <ChevronDown className="h-4 w-4 ml-2" />
              </button>
            ) : (
              <>
                <button
                  onClick={() => openAuthModal('login')}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
                >
                  Log In
                </button>
                <button
                  onClick={() => openAuthModal('signup')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                >
                  Sign Up
                </button>
              </>
            )}
          </div>
        </header>

        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          initialView={authView}
        />

        <main className="max-w-6xl mx-auto">
          {user && showProfile ? (
            <ProfileSection 
              user={user} 
              onBack={() => setShowProfile(false)}
              onLogout={handleLogout}
            />
          ) : (
            <>
              <ScraperForm 
                onScrapedData={(data) => setBattlecards(data.battlecards)}
                setLoading={setLoading}
                setError={setError}
              />

              {error && (
                <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-600 text-sm md:text-base">{error}</p>
                </div>
              )}

              {loading ? (
                <LoadingSpinner />
              ) : (
                <BattlecardList battlecards={battlecards} />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default BattlecardGenerator;
