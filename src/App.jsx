import { useEffect, useMemo, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { StartupGrid } from "./components/StartupGrid";
import { DetailPanel } from "./components/DetailPanel";
import { RecommendationPanel } from "./components/RecommendationPanel";
import { BriefingPanel } from "./components/BriefingPanel";
import { ChatPanel } from "./components/ChatPanel";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

function normalize(text) {
  return text.trim().toLowerCase();
}

function scoreBand(score) {
  if (score >= 85) return "85+";
  if (score >= 70) return "70-84";
  return "<70";
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Falha ao comunicar com a API.");
  }

  return response.json();
}

function upsertStartup(current, nextStartup) {
  const exists = current.some((startup) => startup.id === nextStartup.id);
  if (!exists) return [nextStartup, ...current];
  return current.map((startup) => (startup.id === nextStartup.id ? nextStartup : startup));
}

export default function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [segmentFilter, setSegmentFilter] = useState("Todos");
  const [scoreFilter, setScoreFilter] = useState("Todos");
  const [statusFilter, setStatusFilter] = useState("Todos");
  const [cityFilter, setCityFilter] = useState("Todos");
  const [selectedStartupId, setSelectedStartupId] = useState(null);
  const [startups, setStartups] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [isLoadingStartups, setIsLoadingStartups] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSendingChat, setIsSendingChat] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const loadStartups = async () => {
      try {
        const data = await apiRequest("/api/startups");
        setStartups(data);
        if (data.length > 0) {
          setSelectedStartupId(data[0].id);
        }
      } catch (error) {
        setErrorMessage(error.message);
      } finally {
        setIsLoadingStartups(false);
      }
    };

    loadStartups();
  }, []);

  const selectedStartup = useMemo(
    () => startups.find((startup) => startup.id === selectedStartupId) ?? null,
    [selectedStartupId, startups],
  );

  const segments = useMemo(
    () => ["Todos", ...new Set(startups.map((startup) => startup.segment))],
    [startups],
  );
  const cities = useMemo(
    () => ["Todos", ...new Set(startups.map((startup) => startup.city))],
    [startups],
  );

  const filteredStartups = useMemo(() => {
    return startups.filter((startup) => {
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
  }, [cityFilter, scoreFilter, searchTerm, segmentFilter, startups, statusFilter]);

  const handleAnalyze = async () => {
    const startupName = searchTerm.trim();
    if (!startupName) {
      window.alert("Digite o nome da startup para iniciar a analise.");
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage("");
    try {
      const result = await apiRequest("/api/startups/analyze", {
        method: "POST",
        body: JSON.stringify({ startup_name: startupName }),
      });
      setStartups((current) => upsertStartup(current, result));
      setSelectedStartupId(result.id);
      setChatMessages([]);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleExport = () => {
    if (!selectedStartup) return;
    window.alert(`Briefing executivo de ${selectedStartup.name} exportado em PDF ficticio.`);
  };

  const handleCopyBriefing = async () => {
    if (!selectedStartup) return;

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

  const handleSendMessage = async (input) => {
    if (!input.trim() || !selectedStartup || isSendingChat) return;

    const userMessage = { id: Date.now(), role: "user", text: input };
    setChatMessages((current) => [...current, userMessage]);
    setIsSendingChat(true);

    try {
      const reply = await apiRequest("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          startup_id: selectedStartup.id,
          startup_name: selectedStartup.name,
          message: input,
        }),
      });
      setChatMessages((current) => [
        ...current,
        { id: Date.now() + 1, role: "assistant", text: reply.answer, sources: reply.sources },
      ]);
    } catch (error) {
      setChatMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: `Nao foi possivel responder agora: ${error.message}`,
        },
      ]);
    } finally {
      setIsSendingChat(false);
    }
  };

  return (
    <div className="app-shell">
      <Header
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        onExport={handleExport}
        onAnalyze={handleAnalyze}
        isAnalyzing={isAnalyzing}
      />
      {errorMessage ? <div className="feedback-banner error">{errorMessage}</div> : null}
      {isLoadingStartups ? (
        <div className="feedback-banner">Carregando analises disponiveis...</div>
      ) : null}
      <div className="dashboard-layout">
        <Sidebar
          startups={startups}
          selectedStartupId={selectedStartup?.id ?? ""}
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
          <StartupGrid
            startups={filteredStartups}
            selectedStartupId={selectedStartup?.id ?? ""}
            onSelectStartup={setSelectedStartupId}
          />
          <DetailPanel startup={selectedStartup} />
          <section className="content-grid bottom-grid">
            <RecommendationPanel startup={selectedStartup} />
            <BriefingPanel
              startup={selectedStartup}
              onExport={handleExport}
              onCopy={handleCopyBriefing}
            />
          </section>
          <ChatPanel
            messages={chatMessages}
            onSendMessage={handleSendMessage}
            isSending={isSendingChat}
            disabled={!selectedStartup}
          />
        </main>
      </div>
    </div>
  );
}
