import React from 'react';
import { ArrowRight } from 'lucide-react';
import AuthModal from './auth/AuthModal';

function LandingPage({ openLogin, openSignup, showAuthModal, setShowAuthModal, authView }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="container mx-auto px-4 py-12">
        <header className="flex justify-end space-x-4 mb-16">
          <button
            onClick={openLogin}
            className="px-6 py-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            Log In
          </button>
          <button
            onClick={openSignup}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
          >
            Sign Up
          </button>
        </header>

        <main className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Generate Battlecards with AI
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-600 mb-12 leading-relaxed">
            Transform any website into comprehensive battlecards for competitive analysis and sales enablement.
          </p>

          <div className="grid md:grid-cols-3 gap-8 text-left mb-16">
            <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold mb-3">Instant Analysis</h3>
              <p className="text-gray-600">
                Extract key information and competitive insights from any website automatically.
              </p>
            </div>

            <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold mb-3">Smart Categorization</h3>
              <p className="text-gray-600">
                AI-powered identification of problem areas, solutions, and relevant case studies.
              </p>
            </div>

            <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold mb-3">Export Ready</h3>
              <p className="text-gray-600">
                Download battlecards in PDF format for easy sharing and presentation.
              </p>
            </div>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              onClick={openSignup}
              className="inline-flex items-center px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </button>
          </div>
        </main>

        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          initialView={authView}
        />
      </div>
    </div>
  );
}

export default LandingPage;