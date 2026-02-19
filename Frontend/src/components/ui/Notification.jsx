import React, { useState, useEffect } from 'react';

const Notification = ({ message, type, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300); // Даем время на анимацию
    }, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  if (!isVisible) return null;

  const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
  const icon = type === 'success' ? 'yes' : 'no';

  return (
    <div className={`fixed top-4 right-4 ${bgColor} text-white px-6 py-4 rounded-lg shadow-lg z-50 
                    transform transition-all duration-300 ${isVisible ? 'translate-x-0' : 'translate-x-full'}`}>
      <div className="flex items-center gap-3">
        <span className="text-xl">{icon}</span>
        <span className="font-medium">{message}</span>
        <button onClick={() => setIsVisible(false)} className="ml-4 text-white hover:text-gray-200">
        </button>
      </div>
    </div>
  );
};

export default Notification;