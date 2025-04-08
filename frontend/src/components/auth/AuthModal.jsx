import React, { useState, useEffect } from 'react';
import { Dialog } from '@headlessui/react';
import Login from './Login';
import Signup from './Signup';
import { X } from 'lucide-react';

const AuthModal = ({ isOpen, onClose, initialView = 'login' }) => {
  const [view, setView] = useState(initialView);

  useEffect(() => {
    setView(initialView);
  }, [initialView]);

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      className="relative z-50"
    >
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
          <div className="flex justify-between items-center mb-4">
            <Dialog.Title className="text-lg font-medium text-gray-900">
              {view === 'login' ? 'Log In' : 'Sign Up'}
            </Dialog.Title>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {view === 'login' ? (
            <Login onClose={onClose} switchView={() => setView('signup')} />
          ) : (
            <Signup onClose={onClose} switchView={() => setView('login')} />
          )}
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};

export default AuthModal;
