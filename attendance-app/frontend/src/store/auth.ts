import { create } from 'zustand'

type User = { _id: string, username: string, role: 'student'|'company_admin'|'faculty_admin', company_id?: string, full_name?: string }

type AuthState = {
	token: string | null
	user: User | null
	login: (payload: { token: string, user: User }) => void
	logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
	token: localStorage.getItem('token'),
	user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) as User : null,
	login: ({ token, user }) => {
		localStorage.setItem('token', token)
		localStorage.setItem('user', JSON.stringify(user))
		set({ token, user })
	},
	logout: () => {
		localStorage.removeItem('token')
		localStorage.removeItem('user')
		set({ token: null, user: null })
	}
}))