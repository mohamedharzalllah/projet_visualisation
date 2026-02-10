import React, { useState } from 'react'
import Plot from 'react-plotly.js'

export default function PlotlyChart({ fig }) {
  const [layout, setLayout] = useState(fig.layout || {})
  const [showEditor, setShowEditor] = useState(false)
  const [title, setTitle] = useState(layout.title?.text || 'Graphique')
  const [xLabel, setXLabel] = useState(layout.xaxis?.title?.text || 'X')
  const [yLabel, setYLabel] = useState(layout.yaxis?.title?.text || 'Y')

  const handleUpdateChart = () => {
    const newLayout = {
      ...layout,
      title: { text: title },
      xaxis: { ...layout.xaxis, title: { text: xLabel } },
      yaxis: { ...layout.yaxis, title: { text: yLabel } },
    }
    setLayout(newLayout)
    setShowEditor(false)
  }

  return (
    <div className="chart-wrapper">
      <div className="chart-controls">
        <button 
          className="btn-editor" 
          onClick={() => setShowEditor(!showEditor)}
        >
          {showEditor ? '✕ Fermer' : '✏️ Modifier'}
        </button>
      </div>

      {showEditor && (
        <div className="editor-panel">
          <h4>Paramètres du graphique</h4>
          <div className="editor-group">
            <label>Titre</label>
            <input 
              type="text" 
              value={title} 
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Titre du graphique"
            />
          </div>
          <div className="editor-group">
            <label>Axe X</label>
            <input 
              type="text" 
              value={xLabel} 
              onChange={(e) => setXLabel(e.target.value)}
              placeholder="Label pour l'axe X"
            />
          </div>
          <div className="editor-group">
            <label>Axe Y</label>
            <input 
              type="text" 
              value={yLabel} 
              onChange={(e) => setYLabel(e.target.value)}
              placeholder="Label pour l'axe Y"
            />
          </div>
          <button className="btn-update" onClick={handleUpdateChart}>
            💾 Mettre à jour
          </button>
        </div>
      )}

      <Plot 
        data={fig.data} 
        layout={layout} 
        style={{ width: '100%' }} 
        useResizeHandler={true}
        config={{ responsive: true }}
      />
    </div>
  )
}
