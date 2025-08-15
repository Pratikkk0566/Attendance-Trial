import { useEffect, useState } from 'react'
import { useAuthStore } from '../store/auth'
import { API_BASE, authHeaders } from '../config'

export default function AdminDashboard() {
	const { token } = useAuthStore()
	const [records, setRecords] = useState<any[]>([])
	const [filters, setFilters] = useState({ company: '', student: '', start: '', end: '' })
	const [loading, setLoading] = useState(false)
	const [total, setTotal] = useState(0)

	async function load() {
		setLoading(true)
		const qs = new URLSearchParams()
		Object.entries(filters).forEach(([k,v])=>{ if (v) qs.set(k, v as string) })
		const res = await fetch(`${API_BASE}/admin/records?${qs.toString()}`, { headers: { ...authHeaders(token) } })
		const payload = await res.json()
		setRecords(payload.data || [])
		setTotal(payload.total || 0)
		setLoading(false)
	}
	useEffect(()=>{ load() }, [])

	async function exportExcel() {
		const qs = new URLSearchParams()
		Object.entries(filters).forEach(([k,v])=>{ if (v) qs.set(k, v as string) })
		const res = await fetch(`${API_BASE}/admin/export?${qs.toString()}`, { headers: { ...authHeaders(token) } })
		const blob = await res.blob()
		const url = URL.createObjectURL(blob)
		const a = document.createElement('a')
		a.href = url
		a.download = 'attendance_export.xlsx'
		a.click()
		URL.revokeObjectURL(url)
	}

	return (
		<div>
			<h2>Admin Dashboard</h2>
			<div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 8, maxWidth: 900 }}>
				<input placeholder="Company" value={filters.company} onChange={e=>setFilters(f=>({...f, company:e.target.value}))} />
				<input placeholder="Student username" value={filters.student} onChange={e=>setFilters(f=>({...f, student:e.target.value}))} />
				<input type="date" value={filters.start} onChange={e=>setFilters(f=>({...f, start:e.target.value}))} />
				<input type="date" value={filters.end} onChange={e=>setFilters(f=>({...f, end:e.target.value}))} />
				<div style={{ display: 'flex', gap: 8 }}>
					<button onClick={load}>Apply</button>
					<button onClick={exportExcel}>Export</button>
				</div>
			</div>
			<div style={{ marginTop: 12 }}>Total: {total}</div>
			<div style={{ marginTop: 12 }}>
				{loading ? 'Loading...' : (
					<table style={{ width: '100%', borderCollapse: 'collapse' }}>
						<thead>
							<tr>
								<th align='left'>Timestamp</th>
								<th align='left'>Company</th>
								<th align='left'>Student</th>
								<th align='left'>Lat</th>
								<th align='left'>Lon</th>
								<th align='left'>Status</th>
							</tr>
						</thead>
						<tbody>
							{records.map(r => (
								<tr key={r._id}>
									<td>{new Date(r.timestamp).toLocaleString()}</td>
									<td>{r.company_id}</td>
									<td>{r.student_full_name || r.student_username}</td>
									<td>{r.location?.lat}</td>
									<td>{r.location?.lon}</td>
									<td>{r.status}</td>
								</tr>
							))}
						</tbody>
					</table>
				)}
			</div>
		</div>
	)
}