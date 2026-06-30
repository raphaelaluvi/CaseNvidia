export function BriefingPanel({ startup, onExport, onCopy }) {
  return (
    <section className="panel briefing-panel">
      <div className="section-heading">
        <div>
          <p className="section-label">Briefing executivo</p>
          <h2>Resumo pronto para apresentacao</h2>
        </div>
      </div>

      <div className="briefing-summary">
        <p>{startup.executiveBrief.summary}</p>
      </div>

      <div className="briefing-bullets">
        {startup.executiveBrief.bullets.map((bullet) => (
          <article key={bullet.label}>
            <span>{bullet.label}</span>
            <p>{bullet.text}</p>
          </article>
        ))}
      </div>

      <div className="action-row">
        <button className="button secondary" type="button" onClick={onExport}>
          Exportar PDF
        </button>
        <button className="button tertiary" type="button" onClick={onCopy}>
          Copiar briefing
        </button>
      </div>
    </section>
  );
}
