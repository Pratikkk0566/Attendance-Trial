import { Routes, Route, Navigate, Link } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import AttendancePage from './pages/AttendancePage'
import AdminDashboard from './pages/AdminDashboard'
import RegisterDev from './pages/RegisterDev'
import { useAuthStore } from './store/auth'

function RequireAuth({ children, roles }: { children: JSX.Element, roles?: string[] }) {
	const { user } = useAuthStore()
	if (!user) return <Navigate to="/login" replace />
	if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
	return children
}

export default function App() {
	const { user, logout } = useAuthStore()
	return (
		<div style={{ fontFamily: 'system-ui, Arial', padding: 16 }}>
			<nav style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
				<Link to="/">Home</Link>
				{!user && <Link to="/login">Login</Link>}
				<Link to="/dev/register">Dev Register</Link>
				{user?.role === 'student' && <Link to="/attendance">Mark Attendance</Link>}
				{(user?.role === 'company_admin' || user?.role === 'faculty_admin') && <Link to="/admin">Admin</Link>}
				{user && <button onClick={logout}>Logout</button>}
			</nav>
			<Routes>
				<Route path="/" element={<div>Welcome {user ? user.username : 'Guest'}</div>} />
				<Route path="/login" element={<LoginPage />} />
				<Route path="/dev/register" element={<RegisterDev />} />
				<Route path="/attendance" element={<RequireAuth roles={["student"]}><AttendancePage /></RequireAuth>} />
				<Route path="/admin" element={<RequireAuth roles={["company_admin","faculty_admin"]}><AdminDashboard /></RequireAuth>} />
				<Route path="*" element={<Navigate to="/" replace />} />
			</Routes>
		</div>
	)
}