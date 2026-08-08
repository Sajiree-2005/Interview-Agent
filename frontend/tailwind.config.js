/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#0B0E13',
          900: '#0B0E13',
          800: '#10141B',
          700: '#161B24',
          600: '#1D242F',
          500: '#262F3D'
        },
        line: '#28313F',
        haze: '#8A93A6',
        paper: '#E9EDF3',
        amber: {
          DEFAULT: '#FFB454',
          soft: 'rgba(255,180,84,0.12)'
        },
        teal: {
          DEFAULT: '#5FE3C4',
          soft: 'rgba(95,227,196,0.12)'
        },
        coral: {
          DEFAULT: '#FF7A6B',
          soft: 'rgba(255,122,107,0.12)'
        }
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"IBM Plex Sans"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace']
      },
      backgroundImage: {
        grid: 'linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)'
      },
      backgroundSize: {
        grid: '32px 32px'
      }
    }
  },
  plugins: []
}
