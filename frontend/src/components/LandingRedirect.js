import { useEffect } from 'react';

const LandingRedirect = () => {
  useEffect(() => {
    // Redirect to the landing page
    window.location.href = '/landing.html';
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Redirecting to OnlyMentors.ai...</p>
      </div>
    </div>
  );
};

export default LandingRedirect;