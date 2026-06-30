export function DetailPanel({ startup }) {
  return (
    <section className="panel detail-panel">
      <div className="section-heading">
        <div>
          <p className="section-label">Detalhes da startup</p>
          <h2>{startup.name}</h2>
        </div>
        <span className="status-pill">{startup.classification}</span>
      </div>

      <p className="detail-description">{startup.description}</p>

      <div className="detail-metrics">
        <div>
          <span>Segmento</span>
          <strong>{startup.segment}</strong>
        </div>
        <div>
          <span>Cidade</span>
          <strong>{startup.city}</strong>
        </div>
        <div>
          <span>Score AI-native</span>
          <strong>{startup.aiScore}</strong>
        </div>
        <div>
          <span>Status</span>
          <strong>{startup.validationStatus}</strong>
        </div>
      </div>

      <div className="detail-columns">
        <div>
          <h3>Sinais identificados</h3>
          <ul>
            {startup.signals.map((signal) => (
              <li key={signal}>{signal}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Fontes e evidencias</h3>
          <ul>
            {startup.evidence.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      <div>
        <h3>Proximos passos</h3>
        <ul>
          {startup.nextSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
