'use client';

import { FileText } from 'lucide-react';

interface ExecutiveReportProps {
  report: string;
}

export default function ExecutiveReport({ report }: ExecutiveReportProps) {
  if (!report || report.trim() === '') {
    return (
      <div className="text-center py-12">
        <FileText className="w-16 h-16 mx-auto mb-4 text-gray-600" />
        <p className="text-gray-400">No executive report available</p>
      </div>
    );
  }

  return (
    <div className="glass rounded-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <FileText className="w-6 h-6 text-purple-400" />
        <h3 className="text-xl font-bold">Executive Summary</h3>
      </div>

      <div className="prose prose-invert max-w-none">
        {report.split('\n\n').map((paragraph, index) => {
          // Check if paragraph is a heading (starts with # or is in ALL CAPS)
          if (paragraph.startsWith('#')) {
            const level = paragraph.match(/^#+/)?.[0].length || 1;
            const text = paragraph.replace(/^#+\s*/, '');
            const Tag = `h${Math.min(level + 2, 6)}` as keyof JSX.IntrinsicElements;
            return (
              <Tag key={index} className="font-bold text-purple-400 mt-6 mb-3">
                {text}
              </Tag>
            );
          } else if (paragraph === paragraph.toUpperCase() && paragraph.length < 50) {
            return (
              <h4 key={index} className="font-bold text-purple-400 mt-6 mb-3">
                {paragraph}
              </h4>
            );
          } else if (paragraph.startsWith('- ') || paragraph.startsWith('• ')) {
            // Bullet list
            const items = paragraph.split('\n').filter(line => line.trim());
            return (
              <ul key={index} className="list-disc list-inside space-y-2 text-gray-300 mb-4">
                {items.map((item, idx) => (
                  <li key={idx}>{item.replace(/^[-•]\s*/, '')}</li>
                ))}
              </ul>
            );
          } else if (paragraph.match(/^\d+\./)) {
            // Numbered list
            const items = paragraph.split('\n').filter(line => line.trim());
            return (
              <ol key={index} className="list-decimal list-inside space-y-2 text-gray-300 mb-4">
                {items.map((item, idx) => (
                  <li key={idx}>{item.replace(/^\d+\.\s*/, '')}</li>
                ))}
              </ol>
            );
          } else {
            // Regular paragraph
            return (
              <p key={index} className="text-gray-300 leading-relaxed mb-4">
                {paragraph}
              </p>
            );
          }
        })}
      </div>
    </div>
  );
}
