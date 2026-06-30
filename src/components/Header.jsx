export function Header({ searchTerm, onSearchChange, onExport }) {
  return (
    <header className="topbar panel">
      <div>
        <p className="eyebrow">Entregavel 5 · Dashboard estrategico</p>
        <h1>NVIDIA Startup AI Radar</h1>
        <p className="subtitle">
          Inteligencia de mercado para analisar startups AI-native, sinais tecnicos
          e oportunidades de fit com o ecossistema NVIDIA.
        </p>
      </div>
      <div className="topbar-actions">
        <label className="search-field">
          <span>Buscar startup</span>
          <input
            type="search"
            value={searchTerm}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Ex.: NeuralCare AI"
          />
        </label>
        <div className="action-row">
          <button className="button secondary" type="button" onClick={onExport}>
            Exportar briefing
          </button>
          <button className="button primary" type="button">
            Nova analise
          </button>
        </div>
      </div>
    </header>
  );
}
