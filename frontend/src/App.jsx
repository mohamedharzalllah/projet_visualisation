import React, {useState} from 'react'
import PlotlyChart from './components/PlotlyChart'

export default function App(){
  const [file, setFile] = useState(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState(0)

  const handleSubmit = async (e) =>{
    e.preventDefault()
    if(!file || !query) return alert('Fichier et problématique requis')
    setLoading(true)
    const fd = new FormData()
    fd.append('file', file)
    fd.append('query', query)

    try{
      const res = await fetch('http://127.0.0.1:8000/analyze',{
        method:'POST',
        body: fd
      })
      const data = await res.json()
      if(data.error) alert(data.error)
      else {
        setResults(data.results || [])
        setActiveTab(0)
      }
    }catch(err){
      alert('Erreur de connexion au backend: '+err)
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🎨 Dauphine Viz AI</h1>
          <p>Analyse intelligente et visualisation de données</p>
        </div>
      </header>

      <div className="container">
        <div className="form-section">
          <h2>Configuration</h2>
          <form onSubmit={handleSubmit} className="form">
            <div className="form-group">
              <label htmlFor="csv-input">📊 Charger un CSV</label>
              <input id="csv-input" type="file" accept=".csv" onChange={e=>setFile(e.target.files[0])} className="file-input" />
              {file && <p className="file-name">✓ {file.name}</p>}
            </div>
            <div className="form-group">
              <label htmlFor="query-input">❓ Votre problématique</label>
              <textarea id="query-input" placeholder="Ex: Quels sont les tendances de vente par région?" value={query} onChange={e=>setQuery(e.target.value)} className="textarea" />
            </div>
            <button type="submit" disabled={loading} className="btn-submit">
              {loading? '⏳ Analyse en cours...' : '🚀 Lancer l\'analyse'}
            </button>
          </form>
        </div>

        {results.length > 0 && (
          <div className="results-section">
            <div className="tabs">
              {results.map((r, i) => (
                <button
                  key={i}
                  className={`tab ${activeTab === i ? 'active' : ''}`}
                  onClick={() => setActiveTab(i)}
                >
                  {r.titre}
                </button>
              ))}
            </div>
            
            <div className="tab-content">
              {results[activeTab] && (
                <div className="card">
                  <div className="card-header">
                    <h2>{results[activeTab].titre}</h2>
                    <p className="subtitle">{results[activeTab].justification}</p>
                  </div>

                  <div className="chart-container">
                    {results[activeTab].fig ? (
                      <PlotlyChart fig={results[activeTab].fig} />
                    ) : (
                      <div className="no-chart">
                        <pre>{results[activeTab].code}</pre>
                      </div>
                    )}
                  </div>

                  <div className="insights-section">
                    <h3>📈 Insights Stratégiques</h3>
                    <div className="insights-grid">
                      <div className="insight insight-constat">
                        <h4>🧐 Constat</h4>
                        <p>{results[activeTab].insights?.constat || 'N/A'}</p>
                      </div>
                      <div className="insight insight-analyse">
                        <h4>🧠 Analyse</h4>
                        <p>{results[activeTab].insights?.analyse || 'N/A'}</p>
                      </div>
                      <div className="insight insight-action">
                        <h4>🚀 Action</h4>
                        <p>{results[activeTab].insights?.action || 'N/A'}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
