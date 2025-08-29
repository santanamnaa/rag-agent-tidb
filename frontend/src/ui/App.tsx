import React, { useMemo, useRef, useState } from 'react'

type Message = {
	role: 'user' | 'assistant'
	content: string
}

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const SESSION_KEY = 'rag_session_id'
function getOrCreateSessionId() {
	let id = localStorage.getItem(SESSION_KEY)
	if (!id) {
		id = crypto.randomUUID().replace(/-/g, '')
		localStorage.setItem(SESSION_KEY, id)
	}
	return id
}

export const App: React.FC = () => {
	const [messages, setMessages] = useState<Message[]>([])
	const [input, setInput] = useState('')
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)
	const listRef = useRef<HTMLDivElement | null>(null)

	const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading])

	async function send() {
		if (!canSend) return
		const q = input.trim()
		setInput('')
		setMessages(m => [...m, { role: 'user', content: q }])
		setLoading(true)
		setError(null)
		try {
			const resp = await fetch(`${API_BASE}/chat`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ query: q, k: 5, session_id: getOrCreateSessionId() }),
			})
			if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
			const data = await resp.json()
			setMessages(m => [...m, { role: 'assistant', content: data.answer }])
		} catch (e: any) {
			setError(e?.message ?? 'Request failed')
		} finally {
			setLoading(false)
			listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
		}
	}

	return (
		<div className="app">
			<header className="header">
				<h1>RAG Agent</h1>
			</header>
			<main className="main">
				<div className="messages" ref={listRef}>
					{messages.map((m, i) => (
						<div key={i} className={`message ${m.role}`}>
							{m.content}
						</div>
					))}
					{loading && <div className="message assistant">Typing…</div>}
				</div>
				{error && <div className="error">{error}</div>}
			</main>
			<footer className="footer">
				<input
					value={input}
					onChange={e => setInput(e.target.value)}
					placeholder="Ask anything…"
					onKeyDown={e => {
						if (e.key === 'Enter') send()
					}}
				/>
				<button disabled={!canSend} onClick={send}>
					Send
				</button>
			</footer>
		</div>
	)
}


