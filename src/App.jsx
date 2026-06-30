import { useMemo, useState } from "react";
import { startups as startupData } from "./data/startups";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { MetricsGrid } from "./components/MetricsGrid";
import { StartupGrid } from "./components/StartupGrid";
import { DetailPanel } from "./components/DetailPanel";
import { RecommendationPanel } from "./components/RecommendationPanel";
import { BriefingPanel } from "./components/BriefingPanel";
import { ChatPanel } from "./components/ChatPanel";

const initialMessages = [
  {
    id: 1,
    role: "assistant",
    text: "Radar ativo. Posso destacar startups com maior aderencia ao ecossistema NVIDIA, sinais de IA generativa e proximos passos recomendados.",
  },
  {
    id: 2,
    role: "user",
    text: "Quais startups tem maior aderencia ao ecossistema NVIDIA?",
  },
  {
    id: 3,
    role: "assistant",
    text: "NeuralCare AI, RetailFlow Vision e AgroVision Labs lideram o fit atual, com uso intensivo de inferencia visual, pipelines de modelos proprietarios e necessidade clara de aceleracao de deploy.",
  },
];

function normalize(text) {
  return text.trim().toLowerCase();
}

function scoreBand(score) {
  if (score >= 85) return "85+";
  if (score >= 70) return "70-84";
  return "<70";
}

function getMockReply(input, selectedStartup) {
  const value = normalize(input);

  if (value.includes("healthtech") || value.includes("generativa")) {
    return "NeuralCare AI e LexMind AI aparecem como melhores candidatas para casos com IA generativa aplicada a contexto regulado, especialmente por conta de NLP clinico, copilotos e camadas de evidencias verificaveis.";
  }

  if (value.includes("produto") || value.includes("nvidia")) {
    return `${selectedStartup.name} combina melhor com ${selectedStartup.recommendations[0].name}, ${selectedStartup.recommendations[1].name} e ${selectedStartup.recommendations[2].name}, principalmente pelo nivel de maturidade tecnica e pelas necessidades de inferencia e escalabilidade identificadas.`;
  }

  if (value.includes("risco") || value.includes("validacao")) {
    return "Os principais riscos recorrentes no radar atual sao dependencia de poucas fontes publicas, necessidade de validacao comercial e pouca clareza sobre stack proprietaria em startups ainda seed.";
  }

  return `Analise resumida para ${selectedStartup.name}: score AI-native em ${selectedStartup.aiScore}, classificacao ${selectedStartup.classification} e status ${selectedStartup.validationStatus.toLowerCase()}. Posso aprofundar em fit NVIDIA, sinais tecnicos ou briefing executivo.`;
}

export default function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [segmentFilter, setSegmentFilter] = useState("Todos");
  const [scoreFilter, setScoreFilter] = useState("Todos");
  const [statusFilter, setStatusFilter] = useState("Todos");
  const [cityFilter, setCityFilter] = useState("Todos");
  const [selectedStartupId, setSelectedStartupId] = useState(startupData[0].id);
  const [chatMessages, setChatMessages] = useState(initialMessages);

  const selectedStartup = useMemo(
    () => startupData.find((startup) => startup.id === selectedStartupId) ?? startupData[0],
    [selectedStartupId],
  );

  const segments = useMemo(
    () => ["Todos", ...new Set(startupData.map((startup) => startup.segment))],
    [],
  );
  const cities = useMemo(
    () => ["Todos", ...new Set(startupData.map((startup) => startup.city))],
    [],
  );

  const filteredStartups = useMemo(() => {
    return startupData.filter((startup) => {
      const matchesSearch =
        searchTerm === "" ||
        normalize(startup.name).includes(normalize(searchTerm)) ||
        normalize(startup.summary).includes(normalize(searchTerm));
      const matchesSegment = segmentFilter === "Todos" || startup.segment === segmentFilter;
      const matchesScore = scoreFilter === "Todos" || scoreBand(startup.aiScore) === scoreFilter;
      const matchesStatus =
        statusFilter === "Todos" || startup.validationStatus === statusFilter;
      const matchesCity = cityFilter === "Todos" || startup.city === cityFilter;

      return matchesSearch && matchesSegment && matchesScore && matchesStatus && matchesCity;
    });
  }, [cityFilter, scoreFilter, searchTerm, segmentFilter, statusFilter]);

  const metrics = useMemo(() => {
    const highFit = startupData.filter((startup) => startup.nvidiaFit >= 85).length;
    const pending = startupData.filter(
      (startup) => startup.validationStatus === "Validacao pendente",
    ).length;
    const exported = startupData.filter((startup) => startup.briefingExported).length;

    return [
      {
        label: "Startups analisadas",
        value: startupData.length,
        detail: "Pipeline demo carregado",
      },
      {
        label: "Alto fit NVIDIA",
        value: highFit,
        detail: "Aderencia >= 85",
      },
      {
        label: "Validacao pendente",
        value: pending,
        detail: "Prioridade para analista",
      },
      {
        label: "Briefings exportados",
        value: exported,
        detail: "Ultimo ciclo de scouting",
      },
    ];
  }, []);

  const handleExport = () => {
    window.alert(`Briefing executivo de ${selectedStartup.name} exportado em PDF ficticio.`);
  };

  const handleCopyBriefing = async () => {
    const briefingText = [
      selectedStartup.executiveBrief.summary,
      ...selectedStartup.executiveBrief.bullets.map(
        (bullet) => `${bullet.label}: ${bullet.text}`,
      ),
    ].join("\n");

    try {
      await navigator.clipboard.writeText(briefingText);
      window.alert("Briefing copiado para a area de transferencia.");
    } catch {
      window.alert("Nao foi possivel copiar o briefing neste navegador.");
    }
  };

  const handleSendMessage = (input) => {
    if (!input.trim()) return;

    const reply = getMockReply(input, selectedStartup);
    setChatMessages((current) => [
      ...current,
      { id: current.length + 1, role: "user", text: input },
      { id: current.length + 2, role: "assistant", text: reply },
    ]);
  };

  return (
    <div className="app-shell">
      <Header
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        onExport={handleExport}
      />
      <div className="dashboard-layout">
        <Sidebar
          startups={startupData}
          selectedStartupId={selectedStartup.id}
          onSelectStartup={setSelectedStartupId}
          segmentFilter={segmentFilter}
          onSegmentFilterChange={setSegmentFilter}
          scoreFilter={scoreFilter}
          onScoreFilterChange={setScoreFilter}
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          cityFilter={cityFilter}
          onCityFilterChange={setCityFilter}
          segments={segments}
          cities={cities}
        />
        <main className="dashboard-main">
          <MetricsGrid metrics={metrics} />
          <StartupGrid
            startups={filteredStartups}
            selectedStartupId={selectedStartup.id}
            onSelectStartup={setSelectedStartupId}
          />
          <section className="content-grid">
            <DetailPanel startup={selectedStartup} />
            <RecommendationPanel startup={selectedStartup} />
          </section>
          <section className="content-grid bottom-grid">
            <BriefingPanel
              startup={selectedStartup}
              onExport={handleExport}
              onCopy={handleCopyBriefing}
            />
            <ChatPanel messages={chatMessages} onSendMessage={handleSendMessage} />
          </section>
        </main>
      </div>
    </div>
  );
}
