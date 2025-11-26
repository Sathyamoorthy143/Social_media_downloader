import React, { useState } from 'react';
import Downloader from './components/Downloader';

function App() {
  const [activeTab, setActiveTab] = useState('youtube');

  const tabs = [
    { id: 'youtube', label: 'YouTube' },
    { id: 'instagram', label: 'Instagram' },
    { id: 'pinterest', label: 'Pinterest' },
    { id: 'facebook', label: 'Facebook' },
  ];

  const getThemeColors = () => {
    switch (activeTab) {
      case 'instagram':
        return {
          gradient: 'from-pink-500 via-purple-500 to-orange-500',
          text: 'text-pink-500',
          bg: 'bg-pink-500/10',
          border: 'border-pink-500/20',
          button: 'bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500'
        };
      case 'facebook':
        return {
          gradient: 'from-blue-600 via-blue-500 to-blue-400',
          text: 'text-blue-500',
          bg: 'bg-blue-500/10',
          border: 'border-blue-500/20',
          button: 'bg-gradient-to-r from-blue-700 to-blue-500 hover:from-blue-600 hover:to-blue-400'
        };
      case 'pinterest':
        return {
          gradient: 'from-red-600 via-red-500 to-red-400',
          text: 'text-red-500',
          bg: 'bg-red-500/10',
          border: 'border-red-500/20',
          button: 'bg-gradient-to-r from-red-700 to-red-500 hover:from-red-600 hover:to-red-400'
        };
      case 'youtube':
      default:
        return {
          gradient: 'from-red-600 via-red-500 to-white', // White accent as requested
          text: 'text-white',
          bg: 'bg-white/5',
          border: 'border-white/10',
          button: 'bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400'
        };
    }
  };

  const theme = getThemeColors();

  return (
    <div className={`min-h-screen py-12 px-4 flex flex-col items-center transition-colors duration-700 ${activeTab === 'youtube' ? 'bg-dark-bg' : 'bg-slate-950'}`}>
      {/* Dynamic Background Glow */}
      <div className={`fixed inset-0 pointer-events-none transition-opacity duration-1000 opacity-20 ${theme.bg}`} />

      <header className="text-center mb-12 w-full max-w-4xl relative z-10">
        <h1 className={`text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r ${theme.gradient} mb-6 animate-fade-in tracking-tight drop-shadow-lg transition-all duration-500`}>
          Social Downloader
        </h1>
        <p className="text-slate-400 text-lg animate-fade-in font-light tracking-wide delay-100">
          Download high-quality content from your favorite platforms instantly.
        </p>
      </header>

      <div className="w-full max-w-3xl mx-auto mb-16 relative z-10">
        <div className="flex justify-center mb-12 animate-fade-in delay-200">
          <div className={`tab-container transition-all duration-300 ${theme.border}`}>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-btn ${activeTab === tab.id ? `active ${theme.bg} text-white shadow-lg` : 'hover:text-white'}`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="animate-fade-in delay-300 w-full">
          {activeTab === 'youtube' && (
            <Downloader
              title="YouTube Downloader"
              apiEndpoint="/info"
              placeholder="Paste YouTube URL here..."
              type="youtube"
              description="Download videos and audio from YouTube in high quality. Supports MP4 and MP3 formats."
              theme={theme}
            />
          )}
          {activeTab === 'instagram' && (
            <Downloader
              title="Instagram Downloader"
              apiEndpoint="/api/instagram"
              placeholder="Paste Instagram Post/Reel URL..."
              type="instagram"
              description="Download Instagram Reels, Posts, and Videos directly."
              theme={theme}
            />
          )}
          {activeTab === 'pinterest' && (
            <Downloader
              title="Pinterest Downloader"
              apiEndpoint="/api/pinterest"
              placeholder="Paste Pinterest Pin URL..."
              type="pinterest"
              description="Save Pinterest videos and images effortlessly."
              theme={theme}
            />
          )}
          {activeTab === 'facebook' && (
            <Downloader
              title="Facebook Downloader"
              apiEndpoint="/api/facebook"
              placeholder="Paste Facebook Video URL..."
              type="facebook"
              description="Download Facebook videos in standard or high definition."
              theme={theme}
            />
          )}
        </div>
      </div>

      {/* Services Section */}
      <section className="w-full max-w-4xl mx-auto mb-16 animate-fade-in delay-500 relative z-10">
        <h2 className="text-3xl font-bold text-center mb-8 text-white">Our Services</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { title: 'YouTube', desc: 'Download 4K Videos & MP3 Audio', icon: '📺', color: 'text-red-500' },
            { title: 'Instagram', desc: 'Save Reels, Stories & Posts', icon: '📸', color: 'text-pink-500' },
            { title: 'Pinterest', desc: 'Download Pins & Collections', icon: '📌', color: 'text-red-600' },
            { title: 'Facebook', desc: 'Get HD Videos instantly', icon: 'fb', color: 'text-blue-500' },
          ].map((service, idx) => (
            <div key={idx} className="glass-panel p-6 hover:bg-white/5 transition-colors duration-300 border border-white/5 hover:border-white/10">
              <div className={`text-4xl mb-4 ${service.color}`}>{service.icon === 'fb' ? <span className="font-bold">f</span> : service.icon}</div>
              <h3 className="text-xl font-semibold mb-2 text-white">{service.title}</h3>
              <p className="text-slate-400 text-sm">{service.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Developer Info Section */}
      <footer className="w-full max-w-4xl mx-auto border-t border-white/10 pt-8 mt-8 animate-fade-in delay-700 relative z-10">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-center md:text-left">
            <h3 className="text-lg font-semibold text-white mb-1">Social Downloader</h3>
            <p className="text-slate-500 text-sm">© 2025 All rights reserved.</p>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-slate-400 text-sm">Developed by</p>
              <a
                href="https://github.com/Sathyamoorthy143"
                target="_blank"
                rel="noopener noreferrer"
                className={`transition-colors font-medium ${theme.text}`}
              >
                Sathyamoorthy143
              </a>
            </div>
            <a
              href="https://github.com/Sathyamoorthy143"
              target="_blank"
              rel="noopener noreferrer"
              className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all"
            >
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
              </svg>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
