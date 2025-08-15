import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

export default function Protected({ children, roles }: { children: JSX.Element, roles?: string[] }){
	const { user } = useAuthStore()
	if (!user) return <Navigate to="/login" replace />
	if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
	return children
}