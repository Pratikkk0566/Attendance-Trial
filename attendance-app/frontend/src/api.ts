import { API_BASE, authHeaders } from './config'
import { useAuthStore } from './store/auth'

export async function fetchMe() {
	const { token } = useAuthStore.getState()
	const res = await fetch(`${API_BASE}/auth/me`, { headers: { ...authHeaders(token) } })
	if (!res.ok) throw new Error(await res.text())
	return res.json()
}