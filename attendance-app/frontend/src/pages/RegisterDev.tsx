import { useState } from 'react'
import { API_BASE } from '../config'

export default function RegisterDev() {
	const [form, setForm] = useState({ username: '', password: '', role: 'student', company_id: '', full_name: '' })
	const [file, setFile] = useState<File | null>(null)
	const [msg, setMsg] = useState('')
	async function submit(e: React.FormEvent){
		e.preventDefault()
		const fd = new FormData()
		Object.entries(form).forEach(([k,v])=>fd.append(k, v))
		if (file) fd.append('image', file)
		const res = await fetch(`${API_BASE}/auth/register`, { method: 'POST', body: fd })
		setMsg(res.ok ? 'Registered' : await res.text())
	}
	return (
		<div>
			<h3>Dev Register</h3>
			<form onSubmit={submit} style={{ display: 'grid', gap: 8, maxWidth: 400 }}>
				<input placeholder='Username' value={form.username} onChange={e=>setForm(f=>({...f, username:e.target.value}))} />
				<input type='password' placeholder='Password' value={form.password} onChange={e=>setForm(f=>({...f, password:e.target.value}))} />
				<select value={form.role} onChange={e=>setForm(f=>({...f, role:e.target.value}))}>
					<option value='student'>student</option>
					<option value='company_admin'>company_admin</option>
					<option value='faculty_admin'>faculty_admin</option>
				</select>
				<input placeholder='Company ID' value={form.company_id} onChange={e=>setForm(f=>({...f, company_id:e.target.value}))} />
				<input placeholder='Full Name' value={form.full_name} onChange={e=>setForm(f=>({...f, full_name:e.target.value}))} />
				<input type='file' accept='image/*' onChange={e=>setFile(e.target.files?.[0] || null)} />
				<button type='submit'>Create</button>
				<div>{msg}</div>
			</form>
		</div>
	)
}