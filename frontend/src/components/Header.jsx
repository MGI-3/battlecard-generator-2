// Header.jsx
import React, { useState } from 'react';
import { Menu, X, User } from 'lucide-react';
import LoginModal from './LoginModal';
import SignupModal from './SignupModal';

const Header = ({ currentPage, setCurrentPage }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [user, setUser] = useState(null);

  // Function to handle navigation
  const navigateTo = (page) => {
    setCurrentPage(page);
    setIsMenuOpen(false);
  };

  return (
    <header className="bg-white shadow-sm sticky top-0 z-10">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 
              onClick={() => navigateTo('generator')}
              className="text-xl font-bold text-blue-600 cursor-pointer"
            >
              Battlecard Generator
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <button
              onClick={() => navigateTo('generator')}
              className={`px-3 py-2 transition-colors ${
                currentPage === 'generator' 
                  ? 'text-blue-600 font-medium' 
                  : 'text-gray-700 hover:text-gray-900'
              }`}
            >
              Generate Battlecards
            </button>

            {user ? (
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">{user.email}</span>
                <button
                  onClick={() => {
                    setUser(null);
                  }}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowLogin(true)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Login
                </button>
                <button
                  onClick={() => setShowSignup(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Sign Up
                </button>
              </div>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 text-gray-700 hover:text-gray-900"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden pb-4">
            <button
              onClick={() => navigateTo('generator')}
              className={`block w-full px-4 py-2 text-left transition-colors ${
                currentPage === 'generator' 
                  ? 'text-blue-600 bg-blue-50' 
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Generate Battlecards
            </button>

            {user ? (
              <div className="space-y-2">
                <span className="block px-4 py-2 text-gray-700">{user.email}</span>
                <button
                  onClick={() => {
                    setUser(null);
                    setIsMenuOpen(false);
                  }}
                  className="block w-full px-4 py-2 text-gray-700 hover:bg-gray-50"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <button
                  onClick={() => {
                    setShowLogin(true);
                    setIsMenuOpen(false);
                  }}
                  className="block w-full px-4 py-2 text-gray-700 hover:bg-gray-50"
                >
                  Login
                </button>
                <button
                  onClick={() => {
                    setShowSignup(true);
                    setIsMenuOpen(false);
                  }}
                  className="block w-full px-4 py-2 bg-blue-600 text-white hover:bg-blue-700"
                >
                  Sign Up
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modals */}
      <LoginModal 
        isOpen={showLogin} 
        onClose={() => setShowLogin(false)} 
        setUser={setUser}
      />
      <SignupModal 
        isOpen={showSignup} 
        onClose={() => setShowSignup(false)}
        setUser={setUser}
      />
    </header>
  );
};

export default Header;