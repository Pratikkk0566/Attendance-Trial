export const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export function authHeaders(token: string | null) {
	return token ? { 'Authorization': `Bearer ${token}` } : {}
}