'use client';

import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Link as LinkIcon, Loader2 } from 'lucide-react';

interface ContentSubmitProps {
  onContentSubmit: (content: string, type: string, sourceUrl?: string) => void;
  onFileSubmit: (file: File) => void;
  isAnalyzing: boolean;
}

export default function ContentSubmit({
  onContentSubmit,
  onFileSubmit,
  isAnalyzing
}: ContentSubmitProps) {
  const [inputMethod, setInputMethod] = useState<'text' | 'url' | 'file'>('text');
  const [textContent, setTextContent] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [contentType, setContentType] = useState('text');

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0 && !isAnalyzing) {
        onFileSubmit(acceptedFiles[0]);
      }
    },
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/html': ['.html', '.htm']
    },
    maxFiles: 1,
    disabled: isAnalyzing
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (inputMethod === 'text' && textContent.trim()) {
      onContentSubmit(textContent, contentType);
    } else if (inputMethod === 'url' && sourceUrl.trim()) {
      // For URL, we'd fetch content server-side
      // For now, submit URL as metadata
      onContentSubmit(
        `[Content from URL: ${sourceUrl}]`,
        'confluence_page',
        sourceUrl
      );
    }
  };

  return (
    <div className="glass-card rounded-2xl p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Submit Content for Scanning</h2>
        <p className="text-gray-400">
          Upload files, paste text, or provide a Confluence URL to scan for exposed credentials
        </p>
      </div>

      {/* Input Method Selector */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setInputMethod('text')}
          className={`flex-1 py-3 px-4 rounded-lg transition-colors ${
            inputMethod === 'text'
              ? 'bg-purple-600 text-white'
              : 'glass text-gray-300 hover:text-white'
          }`}
        >
          <FileText className="w-5 h-5 inline mr-2" />
          Paste Text
        </button>
        <button
          onClick={() => setInputMethod('url')}
          className={`flex-1 py-3 px-4 rounded-lg transition-colors ${
            inputMethod === 'url'
              ? 'bg-purple-600 text-white'
              : 'glass text-gray-300 hover:text-white'
          }`}
        >
          <LinkIcon className="w-5 h-5 inline mr-2" />
          Confluence URL
        </button>
        <button
          onClick={() => setInputMethod('file')}
          className={`flex-1 py-3 px-4 rounded-lg transition-colors ${
            inputMethod === 'file'
              ? 'bg-purple-600 text-white'
              : 'glass text-gray-300 hover:text-white'
          }`}
        >
          <Upload className="w-5 h-5 inline mr-2" />
          Upload File
        </button>
      </div>

      {/* Input Area */}
      {inputMethod === 'text' && (
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Content Type</label>
            <select
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
              className="w-full glass rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              disabled={isAnalyzing}
            >
              <option value="text">Plain Text</option>
              <option value="confluence_page">Confluence Page</option>
              <option value="code">Code Snippet</option>
              <option value="configuration">Configuration File</option>
            </select>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Content</label>
            <textarea
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              placeholder="Paste your content here..."
              rows={12}
              className="w-full glass rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              disabled={isAnalyzing}
            />
          </div>

          <button
            type="submit"
            disabled={!textContent.trim() || isAnalyzing}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Scan for Credentials
              </>
            )}
          </button>
        </form>
      )}

      {inputMethod === 'url' && (
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Confluence Page URL</label>
            <input
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://your-confluence.com/display/space/page"
              className="w-full glass rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
              disabled={isAnalyzing}
            />
          </div>

          <div className="mb-4 p-4 glass rounded-lg">
            <p className="text-sm text-gray-400">
              <strong>Note:</strong> URL scanning requires Confluence API credentials to be configured in the backend.
              If not configured, you can copy the page content and use the "Paste Text" option instead.
            </p>
          </div>

          <button
            type="submit"
            disabled={!sourceUrl.trim() || isAnalyzing}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <LinkIcon className="w-5 h-5" />
                Scan Confluence Page
              </>
            )}
          </button>
        </form>
      )}

      {inputMethod === 'file' && (
        <div>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-purple-500 bg-purple-500/10'
                : 'border-gray-600 hover:border-purple-500'
            } ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} />
            <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            {isDragActive ? (
              <p className="text-lg">Drop the file here...</p>
            ) : (
              <>
                <p className="text-lg mb-2">
                  Drag and drop a file here, or click to select
                </p>
                <p className="text-sm text-gray-400">
                  Supports: TXT, PDF, DOC, DOCX, HTML
                </p>
              </>
            )}
          </div>

          {isAnalyzing && (
            <div className="mt-4 flex items-center justify-center gap-2 text-purple-400">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Analyzing file...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
