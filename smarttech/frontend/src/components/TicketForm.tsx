import { useState } from 'react';
import { Send } from 'lucide-react';
import type { Ticket } from '../types';

interface TicketFormProps {
  onSubmit: (ticket: Ticket) => void;
  loading: boolean;
}

const TicketForm = ({ onSubmit, loading }: TicketFormProps) => {
  const [formData, setFormData] = useState<Ticket>({
    ticket_id: `TSD-${Date.now()}`,
    subject: '',
    description: '',
    category: 'General',
    priority: 'Medium',
    user: 'user@smarttech.com',
    created_at: new Date().toISOString(),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.subject && formData.description) {
      onSubmit(formData);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-xl">
          <Send className="w-5 h-5 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
          Submit New Ticket
        </h2>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="label">Ticket ID</label>
          <input
            type="text"
            name="ticket_id"
            value={formData.ticket_id}
            onChange={handleChange}
            className="input-field bg-gray-50"
            readOnly
          />
        </div>

        <div>
          <label className="label">Subject *</label>
          <input
            type="text"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            placeholder="Brief description of the issue"
            className="input-field"
            required
          />
        </div>

        <div>
          <label className="label">Description *</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Detailed explanation of the issue..."
            className="input-field min-h-[100px]"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Category</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="input-field"
            >
              <option value="General">General</option>
              <option value="Email">Email</option>
              <option value="VPN">VPN</option>
              <option value="Hardware">Hardware</option>
              <option value="Software">Software</option>
              <option value="Network">Network</option>
              <option value="Account">Account</option>
              <option value="Security">Security</option>
              <option value="Access">Access</option>
              <option value="Performance">Performance</option>
            </select>
          </div>

          <div>
            <label className="label">Priority</label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              className="input-field"
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
        </div>

        <div>
          <label className="label">User Email</label>
          <input
            type="email"
            name="user"
            value={formData.user}
            onChange={handleChange}
            className="input-field"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !formData.subject || !formData.description}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <Send className="w-4 h-4" />
          {loading ? 'Classifying...' : 'Classify Ticket'}
        </button>
      </form>
    </div>
  );
};

export default TicketForm;
