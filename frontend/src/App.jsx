import React, { useState, useEffect } from 'react';
import { auth } from './firebase/config';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import BattlecardGenerator from './components/BattlecardGenerator';
import LandingPage from './components/LandingPage';

function App() {
  const [battlecards, setBattlecards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [user, setUser] = useState(null);
  const [scraping, setScraping] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authView, setAuthView] = useState('login');

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
    });
    return unsubscribe;
  }, []);

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const openAuthModal = (view) => {
    setAuthView(view);
    setShowAuthModal(true);
  };

  const openLogin = () => {
    setAuthView('login');
    setShowAuthModal(true);
  };

  const openSignup = () => {
    setAuthView('signup');
    setShowAuthModal(true);
  };

  if (!user) {
    return (
      <LandingPage 
        openLogin={openLogin}
        openSignup={openSignup}
        showAuthModal={showAuthModal}
        setShowAuthModal={setShowAuthModal}
        authView={authView}
      />
    );
  }

  return (
    <BattlecardGenerator 
      user={user}
      handleLogout={handleLogout}
      showAuthModal={showAuthModal}
      setShowAuthModal={setShowAuthModal}
      openAuthModal={openAuthModal}
      authView={authView}
      battlecards={battlecards}
      setBattlecards={setBattlecards}
      loading={loading}
      setLoading={setLoading}
      error={error}
      setError={setError}
    />
  );
}

export default App;