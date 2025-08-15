import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { API_BASE } from '../config'

export default function LoginPage() {
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [error, setError] = useState<string | null>(null)
	const navigate = useNavigate()
	const { login } = useAuthStore()

	async function onSubmit(e: React.FormEvent) {
		e.preventDefault()
		setError(null)
		try {
			const res = await fetch(`${API_BASE}/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			})
			if (!res.ok) throw new Error(await res.text())
			const data = await res.json()
			login({ token: data.access_token, user: data.user })
			navigate('/')
		} catch (err: any) {
			setError(err.message || 'Login failed')
		}
	}

	return (
		<div style={{ maxWidth: 360, margin: '0 auto' }}>
			<h2>Login</h2>
			<form onSubmit={onSubmit}>
				<input placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} style={{ width: '100%', padding: 8, marginBottom: 8 }} />
				<input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} style={{ width: '100%', padding: 8, marginBottom: 8 }} />
				<button type="submit" style={{ width: '100%', padding: 10 }}>Sign In</button>
				{error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
			</form>
		</div>
	)
}