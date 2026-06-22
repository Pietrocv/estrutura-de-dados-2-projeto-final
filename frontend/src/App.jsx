import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { FileUp, Loader2, Network, Shuffle, Sparkles } from "lucide-react";
import "./styles.css";

const API_URL = "http://127.0.0.1:8000";

function Logo() {
  return (
    <div className="brand">
      <svg viewBox="0 0 64 64" className="logoMark" aria-hidden="true">
        <rect x="8" y="12" width="48" height="34" rx="12" fill="#ffffff" stroke="#0f172a" strokeWidth="4" />
        <path d="M28 45 L33 56 L43 45" fill="#ffffff" stroke="#0f172a" strokeWidth="4" strokeLinejoin="round" />
        <line x1="21" y1="29" x2="32" y2="22" stroke="#0f766e" strokeWidth="4" />
        <line x1="32" y1="22" x2="44" y2="31" stroke="#0f766e" strokeWidth="4" />
        <line x1="21" y1="29" x2="30" y2="38" stroke="#0f766e" strokeWidth="4" />
        <line x1="30" y1="38" x2="43" y2="39" stroke="#0f766e" strokeWidth="4" />
        <circle cx="21" cy="29" r="5" fill="#14b8a6" stroke="#0f172a" strokeWidth="3" />
        <circle cx="32" cy="22" r="5" fill="#f5b942" stroke="#0f172a" strokeWidth="3" />
        <circle cx="44" cy="31" r="5" fill="#14b8a6" stroke="#0f172a" strokeWidth="3" />
        <circle cx="30" cy="38" r="5" fill="#14b8a6" stroke="#0f172a" strokeWidth="3" />
        <circle cx="43" cy="39" r="5" fill="#14b8a6" stroke="#0f172a" strokeWidth="3" />
      </svg>
      <div>
        <h1>TopicGraph EJ</h1>
        <p>Analise de feedbacks por grafos e comunidades</p>
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function SvgPanel({ title, svg }) {
  if (!svg) return null;
  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>{title}</h2>
      </div>
      <div className="svgBox" dangerouslySetInnerHTML={{ __html: svg }} />
    </section>
  );
}

function App() {
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [quantidade, setQuantidade] = useState(90);
  const metricas = useMemo(() => resultado?.metricas ?? {}, [resultado]);

  async function tratarResposta(response) {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Nao foi possivel analisar os feedbacks.");
    }
    setResultado(data);
  }

  async function gerarAleatorio() {
    setErro("");
    setCarregando(true);
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantidade }),
      });
      await tratarResposta(response);
    } catch (error) {
      setErro(error.message);
    } finally {
      setCarregando(false);
    }
  }

  async function enviarArquivo(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setErro("");
    setCarregando(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });
      await tratarResposta(response);
    } catch (error) {
      setErro(error.message);
    } finally {
      setCarregando(false);
      event.target.value = "";
    }
  }

  return (
    <main className="appShell">
      <header className="topbar">
        <Logo />
        <div className="statusPill">
          <Sparkles size={16} />
          Bonus App
        </div>
      </header>

      <section className="workspace">
        <aside className="controls">
          <div className="controlTitle">
            <Network size={20} />
            <h2>Entrada</h2>
          </div>
          <label className="uploadButton">
            <FileUp size={18} />
            Enviar .txt de feedbacks
            <input type="file" accept=".txt,text/plain" onChange={enviarArquivo} />
          </label>
          <div className="generator">
            <label htmlFor="quantidade">Feedbacks aleatorios</label>
            <input
              id="quantidade"
              type="number"
              min="10"
              max="250"
              value={quantidade}
              onChange={(event) => setQuantidade(Number(event.target.value))}
            />
            <button onClick={gerarAleatorio} disabled={carregando}>
              {carregando ? <Loader2 className="spin" size={18} /> : <Shuffle size={18} />}
              Gerar e analisar
            </button>
          </div>
          {erro && <p className="error">{erro}</p>}
        </aside>

        <section className="results">
          {!resultado && (
            <div className="emptyState">
              <h2>Escolha uma entrada para iniciar</h2>
              <p>O relatorio aparece primeiro. Em seguida, as tres visualizacoes mostram a evolucao do grafo.</p>
            </div>
          )}

          {resultado && (
            <>
              <section className="report">
                <div className="metricsGrid">
                  <Metric label="Feedbacks" value={metricas.feedbacks} />
                  <Metric label="Grau medio" value={metricas.grau_medio} />
                  <Metric label="Densidade" value={metricas.densidade} />
                  <Metric label="Comunidades" value={metricas.comunidades} />
                  <Metric label="Triangulos K3" value={metricas.triangulos} />
                  <Metric label="Outliers" value={metricas.outliers} />
                </div>
                <pre>{resultado.relatorio}</pre>
              </section>

              <SvgPanel title="Fluxo visual completo" svg={resultado.visualizacoes.fluxo_completo} />
              <div className="threePanels">
                <SvgPanel title="Vertices iniciais" svg={resultado.visualizacoes.vertices_iniciais} />
                <SvgPanel title="Grafo filtrado" svg={resultado.visualizacoes.grafo_filtrado} />
                <SvgPanel title="Comunidades nomeadas" svg={resultado.visualizacoes.comunidades} />
              </div>
            </>
          )}
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
