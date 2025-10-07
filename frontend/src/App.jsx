import React, { useState } from 'react'

// Lee la URL base de la API desde .env (Vite expone variables VITE_ al cliente)
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
export default function App(){
  // Estado de formulario y UI
  const [q,setQ]=useState('Cocina')
  const [n,setN]=useState(6)
  const [model,setModel]=useState('')
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState('')
  const [result,setResult]=useState(null)
 // Submit del formulario: llama a /quiz
  const handleSubmit=async(e)=>{
    e.preventDefault()
    setLoading(true); setError(''); setResult(null)
    try{
      const res = await fetch(`${API_BASE}/quiz`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ q, n:Number(n), ...(model?{model}:{}) })
      })
      if(!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)
      setResult(await res.json())
    }catch(err){ setError(err.message||'Error') } finally { setLoading(false) }
  }

  return (
    <>

    {/* Barra simple con marca */}
    <nav className="nav">
      <div className="brand">
        <span style={{width:10,height:10,borderRadius:999,background:'var(--accent)'}}/>
        Prueba Galilei <span style={{opacity:.8}}></span>
      </div>
      
    </nav>
    {/* Hero con título y subtítulo */}
    <section className="hero">
      <div className="hero-card">
        <div className="hero-top">
          <h1 className="hero-title">Genera preguntas desde la API de Wikilibros</h1>
          <p className="hero-sub">Busca un tema, elige cuántas preguntas y deja que la IA haga el resto.</p>
        </div>

        {/* Contenido principal */}
        <div className="container">

          {/* Formulario de parámetros */}
          <form onSubmit={handleSubmit} className="card" style={{marginTop:-16}}>
            <div className="row">
              <div>
                <label>Tema</label>
                <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Higiene, Deportes, Cocina..." required/>
              </div>
              <div>
                <label>Número de preguntas</label>
                <input type="number" min="1" max="20" value={n} onChange={e=>setN(e.target.value)}/>
              </div>
              <div>
                <label>Modelo</label>
                <select value={model} onChange={e=>setModel(e.target.value)}>
                  <option value="">(Default)</option>
                  <option value="meta-llama/llama-3.3-8b-instruct:free">Llama 3.3 8B (free)</option>
                  <option value="qwen/qwen-2.5-72b-instruct:free">Qwen 2.5 72B (free)</option>
                </select>
                </div>
            </div>
            <div style={{marginTop:16, display:'flex', gap:12}}>
              <button className="btn btn-primary" type="submit" disabled={loading}>
                {loading ? (<><span className="loader"></span> Generando...</>) : 'Generar preguntas'}
              </button>
              <button className="btn btn-secondary" type="button" onClick={()=>setResult(null)} disabled={loading}>Limpiar</button>
            </div>
            {error && <p className="error" style={{marginTop:12}}>{error}</p>}
          </form>


          {/* Resultado si existe*/}

          {result && (
            <div className="card">
              <h2 style={{marginTop:0}}>Resultado</h2>
              {result.title && (
                <p className="meta"><strong>Fuente:</strong> {result.title} — <a href={result.url} target="_blank" rel="noreferrer">{result.url}</a></p>
              )}
              <ol className="questions">
                
                  {(result?.questions || []).slice(0, Number(n)).map((q, idx) => (

                  <li key={idx} className="q">
                    <div style={{fontWeight:700}}>{q.question}</div>
                    <ul className="choices">
                      {q.choices.map((c,i)=>(
                        <li key={i} className={i===q.correctIndex?'correct':''}>
                          <span style={{fontWeight:700, marginRight:6}}>{String.fromCharCode(65+i)}.</span> {c}
                        </li>
                      ))}
                    </ul>
                    <details style={{marginTop:8}}>
                      <summary>Mostrar solución</summary>
                      <p>Respuesta correcta: <strong>{String.fromCharCode(65 + (q.correctIndex ?? 0))}</strong></p>
                    </details>
                  </li>
                ))}
              </ol>
              <div className="footer"><p>Backend: <code>{API_BASE}</code></p></div>
            </div>
          )}
        </div>
      </div>
    </section>
  </>)
}
