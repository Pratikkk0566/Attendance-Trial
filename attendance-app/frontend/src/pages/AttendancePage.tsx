import { useEffect, useRef, useState } from 'react'
import { useAuthStore } from '../store/auth'
import { API_BASE, authHeaders } from '../config'

export default function AttendancePage() {
	const videoRef = useRef<HTMLVideoElement>(null)
	const canvasRef = useRef<HTMLCanvasElement>(null)
	const { token } = useAuthStore()
	const [status, setStatus] = useState<string>('')
	const [loc, setLoc] = useState<{lat?: number, lon?: number}>({})
	const [busy, setBusy] = useState(false)
	const [history, setHistory] = useState<any[]>([])

	async function startCamera() {
		const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
		if (videoRef.current) {
			videoRef.current.srcObject = stream
			await videoRef.current.play()
		}
	}

	async function loadHistory(){
		const res = await fetch(`${API_BASE}/attendance/me`, { headers: { ...authHeaders(token) } })
		if (res.ok) setHistory(await res.json())
	}
	useEffect(()=>{ loadHistory() }, [])

	async function captureAndSubmit() {
		try {
			setBusy(true)
			setStatus('')
			// location
			const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
				navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 10000 })
			})
			const { latitude, longitude } = pos.coords
			setLoc({ lat: latitude, lon: longitude })
			// capture
			const video = videoRef.current!
			const canvas = canvasRef.current!
			canvas.width = video.videoWidth
			canvas.height = video.videoHeight
			const ctx = canvas.getContext('2d')!
			ctx.drawImage(video, 0, 0)
			const blob: Blob = await new Promise((resolve) => canvas.toBlob(b => resolve(b!), 'image/jpeg', 0.9))

			const form = new FormData()
			form.append('image', blob, 'selfie.jpg')
			form.append('lat', String(latitude))
			form.append('lon', String(longitude))
			const res = await fetch(`${API_BASE}/attendance`, {
				method: 'POST',
				headers: { ...authHeaders(token) },
				body: form,
			})
			if (!res.ok) throw new Error(await res.text())
			const data = await res.json()
			setStatus(`Submitted: ${data.status}${data.score ? ' (score ' + data.score + ')' : ''}`)
			await loadHistory()
		} catch (e: any) {
			setStatus(e.message || 'Failed')
		} finally {
			setBusy(false)
		}
	}

	return (
		<div>
			<h2>Mark Attendance</h2>
			<div style={{ display: 'grid', gap: 8 }}>
				<video ref={videoRef} playsInline style={{ width: '100%', maxWidth: 400, background: '#000' }} />
				<canvas ref={canvasRef} style={{ display: 'none' }} />
				<div style={{ display: 'flex', gap: 8 }}>
					<button onClick={startCamera}>Start Camera</button>
					<button onClick={captureAndSubmit} disabled={busy}>Capture & Submit</button>
				</div>
				<div>Location: {loc.lat?.toFixed(5)}, {loc.lon?.toFixed(5)}</div>
				<div>Status: {status}</div>
			</div>
			<h3>My Recent Attendance</h3>
			<table style={{ width: '100%', maxWidth: 600 }}>
				<thead>
					<tr>
						<th align='left'>Time</th>
						<th align='left'>Status</th>
						<th align='left'>Lat</th>
						<th align='left'>Lon</th>
					</tr>
				</thead>
				<tbody>
					{history.map((h)=> (
						<tr key={h._id}>
							<td>{new Date(h.timestamp).toLocaleString()}</td>
							<td>{h.status}</td>
							<td>{h.location?.lat}</td>
							<td>{h.location?.lon}</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	)
}