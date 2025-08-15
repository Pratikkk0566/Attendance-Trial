# 🎯 Attendance Tracking App

A modern, full-stack attendance tracking application with face recognition, location verification, and real-time analytics.

## 🌟 Features

### 🔐 Authentication & Security
- **JWT-based authentication** with role-based access control
- **Three user roles**: Student, Company Admin, Faculty Admin
- **Secure password hashing** with bcrypt
- **Session management** with automatic token refresh

### 👤 Face Recognition
- **Real-time face detection** using OpenCV and face_recognition library
- **Face enrollment** during registration
- **Live face verification** during attendance marking
- **Anti-spoofing** measures to prevent photo/video attacks

### 📍 Location Tracking
- **GPS coordinate capture** using HTML5 Geolocation API
- **Location verification** to ensure on-site attendance
- **Mobile-first design** for seamless smartphone usage

### 📊 Admin Dashboard
- **Real-time attendance analytics**
- **Advanced filtering** by date, company, student, status
- **Excel export** functionality for reports
- **Pagination** for large datasets
- **Company-specific access control**

### 📱 Mobile-Responsive Design
- **Tailwind CSS** for modern, responsive UI
- **Camera integration** for selfie capture
- **Touch-friendly** interface for mobile devices
- **PWA-ready** for app-like experience

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** with Flask framework
- **MongoDB Atlas** for cloud database
- **JWT** for authentication
- **OpenCV & face_recognition** for computer vision
- **pandas & openpyxl** for Excel exports
- **bcrypt** for password security

### Frontend
- **React 18** with modern hooks
- **React Router** for navigation
- **Tailwind CSS** for styling
- **Axios** for API communication
- **React Webcam** for camera access
- **React Toastify** for notifications

## 📋 Prerequisites

Before setting up the project, ensure you have:

1. **Python 3.11 or higher**
2. **Node.js 16 or higher**
3. **MongoDB** (local installation or MongoDB Atlas account)
4. **VS Code** with recommended extensions
5. **Git** for version control

## 🚀 VS Code Setup Guide

### Step 1: Clone or Download the Project

#### Option A: If you have Git
```bash
git clone <repository-url>
cd attendance-app
```

#### Option B: Manual Setup in VS Code
1. Open VS Code
2. Create a new folder called `attendance-app`
3. Copy all the project files into this folder
4. Open the folder in VS Code (`File > Open Folder`)

### Step 2: Install VS Code Extensions

Install these recommended extensions for the best development experience:

1. **Python Extensions:**
   - Python (Microsoft)
   - Python Debugger (Microsoft)
   - Pylance (Microsoft)

2. **React/JavaScript Extensions:**
   - ES7+ React/Redux/React-Native snippets
   - Bracket Pair Colorizer
   - Auto Rename Tag
   - Prettier - Code formatter

3. **General Development:**
   - GitLens
   - Thunder Client (for API testing)
   - MongoDB for VS Code

### Step 3: Backend Setup

#### 3.1 Open Terminal in VS Code
- Press `Ctrl+` ` (backtick) to open integrated terminal
- Navigate to backend directory:
```bash
cd backend
```

#### 3.2 Create Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3.3 Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with `dlib` or `face_recognition`:

**For Windows:**
```bash
pip install cmake
pip install dlib
pip install face_recognition
```

**For macOS:**
```bash
brew install cmake
pip install dlib
pip install face_recognition
```

**For Ubuntu/Linux:**
```bash
sudo apt-get update
sudo apt-get install cmake
sudo apt-get install python3-dev
pip install dlib
pip install face_recognition
```

#### 3.4 Setup Environment Variables
1. Rename `.env` file or create it if it doesn't exist
2. Update the MongoDB connection string:

```env
# For local MongoDB
MONGODB_URI=mongodb://localhost:27017/attendance_app

# For MongoDB Atlas (recommended)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/attendance_app

JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True
```

#### 3.5 Setup Database
```bash
python setup_db.py
```

This will create sample companies and users for testing.

#### 3.6 Run Backend Server
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Step 4: Frontend Setup

#### 4.1 Open New Terminal Tab
- In VS Code, click the `+` icon in terminal to open a new tab
- Navigate to frontend directory:
```bash
cd frontend
```

#### 4.2 Install Node.js Dependencies
```bash
npm install
```

If you encounter any errors, try:
```bash
npm install --legacy-peer-deps
```

#### 4.3 Start React Development Server
```bash
npm start
```

The frontend will run on `http://localhost:3000`

### Step 5: MongoDB Setup

#### Option A: Local MongoDB
1. Install MongoDB Community Server
2. Start MongoDB service
3. Use the local connection string in `.env`

#### Option B: MongoDB Atlas (Recommended)
1. Create free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster
3. Get connection string and update `.env`
4. Whitelist your IP address

### Step 6: VS Code Workspace Configuration

Create a VS Code workspace file for better project management:

1. Go to `File > Save Workspace As`
2. Save as `attendance-app.code-workspace`
3. Add this configuration:

```json
{
  "folders": [
    {
      "path": "./backend"
    },
    {
      "path": "./frontend"
    }
  ],
  "settings": {
    "python.defaultInterpreterPath": "./backend/venv/Scripts/python",
    "python.terminal.activateEnvironment": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "extensions": {
    "recommendations": [
      "ms-python.python",
      "ms-python.debugpy",
      "ms-python.pylance",
      "bradlc.vscode-tailwindcss",
      "esbenp.prettier-vscode"
    ]
  }
}
```

## 🧪 Testing the Application

### 1. Access the Application
- Open browser and go to `http://localhost:3000`
- You should see the login page

### 2. Test with Demo Accounts

**Faculty Admin:**
- Username: `faculty_admin`
- Password: `admin123`
- Can view all students from all companies

**Company Admin:**
- Username: `tech_admin`
- Password: `admin123`
- Can view students from Tech Corp only

**Student:**
- Username: `john_student`
- Password: `student123`
- Can mark attendance and view personal records

### 3. Test Face Registration
1. Login as a student
2. Go to Profile page
3. Capture your face for registration
4. Try marking attendance

### 4. Test Attendance Marking
1. Login as student
2. Go to Attendance page
3. Allow camera and location permissions
4. Capture selfie and submit

### 5. Test Admin Dashboard
1. Login as admin
2. View attendance records
3. Test filtering by date, company, status
4. Export to Excel

## 🔧 VS Code Development Tips

### 1. Debugging Setup

**Backend Debugging:**
1. Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "program": "backend/app.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "FLASK_ENV": "development"
      }
    }
  ]
}
```

**Frontend Debugging:**
- Use browser developer tools
- React DevTools extension

### 2. Code Formatting
1. Install Prettier extension
2. Set format on save in settings
3. Use consistent code style

### 3. Git Integration
- Use Source Control panel in VS Code
- Commit frequently with descriptive messages
- Use GitLens for advanced Git features

## 📱 Mobile Testing

### Testing on Mobile Device
1. Find your computer's IP address
2. Update React package.json:
```json
"scripts": {
  "start": "react-scripts start --host 0.0.0.0"
}
```
3. Access `http://YOUR_IP:3000` from mobile browser

### PWA Installation
- Visit the site on mobile
- Use "Add to Home Screen" option
- App will work like a native app

## 🔒 Security Considerations

### Development Environment
- Change JWT secret key in production
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs

### Production Deployment
- Use environment variables for secrets
- Enable CORS only for trusted domains
- Implement proper logging
- Use MongoDB Atlas with authentication

## 🐛 Common Issues & Solutions

### Backend Issues

**1. Face Recognition Installation Fails:**
```bash
# Install Visual Studio Build Tools (Windows)
# Install Xcode Command Line Tools (macOS)
# Install build-essential (Linux)
```

**2. MongoDB Connection Fails:**
- Check MongoDB service is running
- Verify connection string
- Check firewall settings

**3. Permission Errors:**
```bash
# Run as administrator (Windows)
sudo pip install -r requirements.txt  # Linux/macOS
```

### Frontend Issues

**1. Node Modules Installation Fails:**
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**2. Camera Access Denied:**
- Use HTTPS in production
- Check browser permissions
- Test on different browsers

**3. Build Failures:**
```bash
npm install --legacy-peer-deps
npm audit fix
```

## 📊 Performance Optimization

### Backend Optimization
- Use MongoDB indexes (already implemented)
- Implement caching with Redis
- Use async processing for face recognition
- Optimize image processing

### Frontend Optimization
- Implement lazy loading
- Use React.memo for expensive components
- Optimize bundle size
- Use service workers for offline support

## 🚢 Production Deployment

### Backend Deployment
1. Use Gunicorn or uWSGI
2. Set up reverse proxy with Nginx
3. Use environment variables
4. Enable logging and monitoring

### Frontend Deployment
1. Build production bundle: `npm run build`
2. Serve with Nginx or CDN
3. Enable gzip compression
4. Set up proper caching headers

## 📞 Support & Contributing

### Getting Help
- Check existing issues in repository
- Create detailed bug reports
- Include error messages and logs

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Congratulations!

You now have a fully functional attendance tracking app running in VS Code! The application includes:

✅ **Face recognition** for secure attendance  
✅ **Location tracking** for on-site verification  
✅ **Role-based access control** for different user types  
✅ **Real-time analytics** and reporting  
✅ **Mobile-responsive design** for smartphone usage  
✅ **Excel export** functionality for data analysis  

Happy coding! 🚀