import React, { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || '';

const Downloader = ({ title, apiEndpoint, placeholder, type, description, theme }) => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleDownload = async () => {
        if (!url) return;
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            let response;
            // Use /info for all types to get preview first
            const infoRes = await fetch(`${API_BASE}/api/info?url=${encodeURIComponent(url)}`);
            if (!infoRes.ok) throw new Error('Failed to fetch video info');
            const infoData = await infoRes.json();
            setResult({
                title: infoData.title,
                thumbnail: infoData.thumbnail_url,
                duration: infoData.length,
                isYoutube: true, // Treat all as "youtube-like" for download flow
                originalUrl: url
            });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const downloadYoutube = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_BASE}/api/download`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, link: true })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || "Download failed");
            }

            const data = await res.json();
            if (data.download_link) {
                // Create a temporary link and click it to trigger download
                const a = document.createElement('a');
                a.href = data.download_link; // This usually comes back absolute if _external=True in backend, but let's verify
                // In main.py: url_for(..., _external=True) returns absolute URL. So this is fine.
                a.download = '';
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                throw new Error("No download link received");
            }
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className={`glass-panel p-8 max-w-2xl mx-auto animate-fade-in transition-all duration-500 border ${theme?.border || 'border-white/10'}`}>
            <h2 className={`text-3xl font-bold mb-2 text-center bg-clip-text text-transparent bg-gradient-to-r ${theme?.gradient || 'from-indigo-400 to-pink-400'}`}>
                {title}
            </h2>
            <p className="text-center text-gray-400 mb-8 max-w-lg mx-auto text-sm">
                {description}
            </p>

            <div className="flex gap-4 mb-8">
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder={placeholder}
                    className={`input-field flex-1 focus:ring-2 ${theme?.border ? theme.border.replace('border', 'focus:border') : 'focus:border-primary'}`}
                />
                <button
                    onClick={handleDownload}
                    disabled={loading}
                    className={`text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none border-none cursor-pointer ${theme?.button || 'btn-primary'}`}
                >
                    {loading ? 'Processing...' : 'Fetch'}
                </button>
            </div>

            {error && (
                <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 mb-6">
                    {error}
                </div>
            )}

            {result && (
                <div className="animate-fade-in">
                    <div className={`flex gap-6 items-start p-6 rounded-xl border transition-colors duration-300 ${theme?.bg || 'bg-slate-800/50'} ${theme?.border || 'border-white/5'}`}>
                        {result.thumbnail && (
                            <img
                                src={result.thumbnail}
                                alt={result.title}
                                className="w-48 h-32 object-cover rounded-lg shadow-lg"
                            />
                        )}
                        <div className="flex-1">
                            <h3 className="text-xl font-semibold mb-2 text-white">{result.title || 'Video Found'}</h3>
                            {result.duration && <p className="text-gray-400 text-sm mb-4">Duration: {result.duration}</p>}

                            <div className="flex gap-3">
                                {result.isYoutube ? (
                                    <button
                                        onClick={downloadYoutube}
                                        className={`text-white font-semibold py-2 px-6 rounded-lg transition-all duration-300 hover:shadow-lg disabled:opacity-50 ${theme?.button || 'btn-primary'}`}
                                        disabled={loading}
                                    >
                                        {loading ? 'Processing...' : 'Download MP4'}
                                    </button>
                                ) : (
                                    <a
                                        href={
                                            result.is_external
                                                ? result.download_url  // Use external link directly (SavePinMedia)
                                                : result.download_url && result.download_url.startsWith('/')
                                                    ? `${API_BASE}${result.download_url}`
                                                    : `${API_BASE}/api/proxy_download?url=${encodeURIComponent(result.download_url || result.url)}&filename=${encodeURIComponent((result.title || 'video').replace(/[^a-z0-9]/gi, '_') + '.mp4')}`
                                        }
                                        download
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className={`text-white font-semibold py-2 px-6 rounded-lg transition-all duration-300 hover:shadow-lg inline-block text-center ${theme?.button || 'btn-primary'}`}
                                    >
                                        {result.is_external ? 'Download via SavePinMedia' : 'Download Video'}
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )
            }
        </div >
    );
};

export default Downloader;
