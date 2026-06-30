export function MetricsGrid({ metrics }) {
  return (
    <section className="metrics-grid">
      {metrics.map((metric) => (
        <article className="metric-card panel" key={metric.label}>
          <p>{metric.label}</p>
          <strong>{metric.value}</strong>
          <span>{metric.detail}</span>
        </article>
      ))}
    </section>
  );
}
