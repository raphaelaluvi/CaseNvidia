function scoreTone(score) {
  if (score >= 90) return "excellent";
  if (score >= 80) return "good";
  return "fair";
}

export function StartupGrid({ startups, selectedStartupId, onSelectStartup }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="section-label">Radar de startups</p>
          <h2>Pipeline priorizado para analise</h2>
        </div>
        <span>{startups.length} resultados</span>
      </div>
      <div className="startup-grid">
        {startups.map((startup) => (
          <article
            key={startup.id}
            className={`startup-card ${selectedStartupId === startup.id ? "selected" : ""}`}
          >
            <div className="card-topline">
              <div>
                <h3>{startup.name}</h3>
                <p>
                  {startup.segment} · {startup.city}
                </p>
              </div>
              <span className={`status-badge ${scoreTone(startup.aiScore)}`}>
                Score {startup.aiScore}
              </span>
            </div>

            <div className="meta-row">
              <span className="status-pill">{startup.validationStatus}</span>
              <span className="fit-pill">Fit NVIDIA {startup.nvidiaFit}</span>
            </div>

            <div className="score-bar">
              <div style={{ width: `${startup.aiScore}%` }} />
            </div>

            <p className="startup-summary">{startup.summary}</p>

            <div className="tag-row">
              {startup.tags.map((tag) => (
                <span key={tag} className="tag">
                  {tag}
                </span>
              ))}
            </div>

            <button className="button tertiary" type="button" onClick={() => onSelectStartup(startup.id)}>
              Ver detalhes
            </button>
          </article>
        ))}
      </div>
      {startups.length === 0 ? (
        <div className="empty-state">
          Nenhuma startup encontrada com os filtros atuais.
        </div>
      ) : null}
    </section>
  );
}
