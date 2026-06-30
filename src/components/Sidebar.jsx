const scoreBands = ["Todos", "85+", "70-84", "<70"];
const statuses = ["Todos", "Validado", "Em revisao", "Validacao pendente"];

function FilterGroup({ label, value, onChange, options }) {
  return (
    <label className="filter-group">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

export function Sidebar({
  startups,
  selectedStartupId,
  onSelectStartup,
  segmentFilter,
  onSegmentFilterChange,
  scoreFilter,
  onScoreFilterChange,
  statusFilter,
  onStatusFilterChange,
  cityFilter,
  onCityFilterChange,
  segments,
  cities,
}) {
  return (
    <aside className="sidebar panel">
      <div className="sidebar-section">
        <p className="section-label">Filtros do radar</p>
        <FilterGroup
          label="Segmento"
          value={segmentFilter}
          onChange={onSegmentFilterChange}
          options={segments}
        />
        <FilterGroup
          label="Score AI-native"
          value={scoreFilter}
          onChange={onScoreFilterChange}
          options={scoreBands}
        />
        <FilterGroup
          label="Status de validacao"
          value={statusFilter}
          onChange={onStatusFilterChange}
          options={statuses}
        />
        <FilterGroup
          label="Cidade / mercado"
          value={cityFilter}
          onChange={onCityFilterChange}
          options={cities}
        />
      </div>

      <div className="sidebar-section">
        <div className="section-heading">
          <p className="section-label">Watchlist demo</p>
          <span>{startups.length} startups</span>
        </div>
        <div className="startup-list">
          {startups.map((startup) => (
            <button
              key={startup.id}
              className={`startup-list-item ${
                startup.id === selectedStartupId ? "active" : ""
              }`}
              type="button"
              onClick={() => onSelectStartup(startup.id)}
            >
              <strong>{startup.name}</strong>
              <span>{startup.segment}</span>
              <small>
                {startup.city} · Score {startup.aiScore}
              </small>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
