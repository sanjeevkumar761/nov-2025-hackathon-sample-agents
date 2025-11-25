/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        agile: {
          story: '#3b82f6', // Blue for stories
          sprint: '#10b981', // Green for sprints
          release: '#8b5cf6', // Purple for releases
          epic: '#f59e0b', // Orange for epics
          completed: '#22c55e',
          inprogress: '#f97316',
          blocked: '#ef4444',
          backlog: '#6b7280'
        },
        gitlab: {
          primary: '#FC6D26', // GitLab orange
          secondary: '#E24329'
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
