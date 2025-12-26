# 🖥️ PyShell Terminal

A modern, web-based terminal interface built with React and FastAPI. Experience the power of command-line operations through an intuitive, responsive web application.

## Why PyShell Terminal?

### 🎯 **Core Features**
- **Web-Based Terminal**: Access a full terminal experience directly in your browser - no installation required
- **Secure Sandboxed Environment**: Execute commands safely without affecting your local system
- **Real-time System Monitoring**: Monitor CPU, memory, and network usage with live status updates

### 🚀 **Available Commands**

| Category | Commands |
|----------|----------|
| **File & Directory Operations** | `ls`, `cd`, `pwd`, `mkdir`, `rm`, `rmdir`, `touch`, `cat`, `echo`, `mv`, `cp`, `ln`, `chmod`, `chown`, `file`, `stat` |
| **Text Processing** | `head`, `tail`, `grep`, `sed`, `awk`, `sort`, `uniq`, `wc`, `cut` |
| **System Information** | `whoami`, `date`, `uptime`, `uname`, `df`, `du`, `free`, `top`, `ps`, `kill`, `killall`, `jobs`, `bg`, `fg` |
| **Network & Utilities** | `ping`, `curl`, `wget`, `ssh`, `scp`, `tar`, `zip`, `unzip` |
| **Terminal Control** | `clear`, `history`, `alias`, `export`, `env`, `which`, `whereis` |
| **Help & Documentation** | `help`, `man`, `info` |

## 🏗️ Architecture

```
PyShell Terminal/
├── frontend/                 # React TypeScript application
│   ├── src/
│   │   ├── App.tsx          # Main terminal component
│   │   ├── App.css          # Terminal styling
│   │   └── main.tsx         # Application entry point
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── backend/                 # FastAPI Python server
│   ├── main.py              # FastAPI application
│   ├── command_processor.py # Command execution engine
│   ├── commands_list.py     # Available commands
│   └── requirements.txt     # Python dependencies
└── terminal_root/           # Sandboxed terminal environment
    ├── home/               # User home directory
    ├── documents/          # Documents folder
    ├── downloads/          # Downloads folder
    └── projects/           # Projects folder
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/pyshell.git
   cd pyshell
   ```

2. **Start the Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Start the Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the Terminal**
   Open your browser and navigate to `http://localhost:5173`

### 🌐 **Live Demo**
- **Frontend**: Deployed on Vercel
- **Backend API**: Deployed on Vercel

### Production Deployment

The application is configured for deployment on Vercel:

1. **Backend**: Deploy as a serverless function on Vercel
2. **Frontend**: Deploy as a static site on Vercel

## 🛠️ Technology Stack

### Frontend
- **React 18.3.1** - Modern UI framework
- **TypeScript 5.0+** - Type-safe development
- **Vite** - Fast build tool and dev server
- **CSS3** - Custom styling with responsive design

### Backend
- **FastAPI 0.104.1** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **psutil** - System information

### Deployment
- **Vercel** - Full-stack hosting platform
- **Serverless Functions** - Backend API deployment

## 📖 Usage

### Basic Commands
```bash
# List directory contents
ls

# Change directory
cd documents
cd ..  # Go up one level
cd ~   # Go to home directory

# Create files and directories
touch newfile.txt
mkdir newfolder

# View file contents
cat newfile.txt
head newfile.txt  # First 10 lines
tail newfile.txt  # Last 10 lines

# Search in files
grep "pattern" filename.txt

# System information
whoami
date
uptime
df  # Disk usage
free # Memory usage
```

### Getting Help
```bash
help        # Show all available commands
man ls      # Show manual for specific command
info grep   # Show info documentation
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=https://your-vercel-backend-url.vercel.app
```

### Customization
- **Colors**: Modify `frontend/src/App.css` for theme customization
- **Commands**: Add new commands in `backend/commands_list.py`
- **Styling**: Update CSS variables for different color schemes
