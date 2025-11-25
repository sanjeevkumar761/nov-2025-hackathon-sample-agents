import { useState, useEffect } from 'react';
import { FileText, Loader } from 'lucide-react';
import { smartTechApi } from '../api';
import type { Ticket } from '../types';

interface MockTicketsPanelProps {
  onSelectTicket: (ticket: Ticket) => void;
  loading: boolean;
}

const MockTicketsPanel = ({ onSelectTicket, loading }: MockTicketsPanelProps) => {
  const [mockTickets, setMockTickets] = useState<Ticket[]>([]);
  const [loadingTickets, setLoadingTickets] = useState(true);

  useEffect(() => {
    loadMockTickets();
  }, []);

  const loadMockTickets = async () => {
    try {
      const response = await smartTechApi.getMockTickets();
      setMockTickets(response.tickets);
    } catch (error) {
      console.error('Failed to load mock tickets:', error);
    } finally {
      setLoadingTickets(false);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl">
          <FileText className="w-5 h-5 text-purple-600" />
        </div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Test with Mock Tickets
        </h2>
      </div>

      {loadingTickets ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="w-8 h-8 text-indigo-600 animate-spin" />
        </div>
      ) : (
        <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
          {mockTickets.map((ticket) => (
            <button
              key={ticket.ticket_id}
              onClick={() => onSelectTicket(ticket)}
              disabled={loading}
              className="w-full text-left p-4 bg-gradient-to-r from-gray-50 to-slate-50 hover:from-indigo-50 hover:to-purple-50 border-2 border-gray-200 hover:border-indigo-300 rounded-xl transition-all duration-200 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02]"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-gray-500 mb-1">{ticket.ticket_id}</div>
                  <div className="font-medium text-gray-900 text-sm truncate">
                    {ticket.subject}
                  </div>
                  <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                    {ticket.description}
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <span className={`badge text-xs ${
                    ticket.priority === 'High' || ticket.priority === 'Critical'
                      ? 'badge-danger'
                      : ticket.priority === 'Medium'
                      ? 'badge-warning'
                      : 'badge-success'
                  }`}>
                    {ticket.priority}
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      <div className="mt-4 text-xs text-gray-600 bg-gray-50 rounded p-2">
        💡 Click any mock ticket to classify it instantly
      </div>
    </div>
  );
};

export default MockTicketsPanel;
