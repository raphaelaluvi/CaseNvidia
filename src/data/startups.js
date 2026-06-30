export const startups = [
  {
    id: "neuralcare-ai",
    name: "NeuralCare AI",
    segment: "healthtech",
    city: "Sao Paulo",
    aiScore: 93,
    nvidiaFit: 94,
    classification: "AI-native avancada",
    validationStatus: "Validado",
    tags: ["LLM clinico", "Visao computacional", "Prontuario"],
    summary:
      "Plataforma de apoio clinico com copiloto medico, triagem automatizada e leitura multimodal de exames.",
    description:
      "A NeuralCare AI opera um stack proprio para triagem clinica, sumarios assistidos e analise de imagem medica, com foco em hospitais de media e alta complexidade.",
    signals: [
      "Arquitetura multimodal para texto clinico e imagem diagnostica",
      "Roadmap de copiloto medico com camada de auditoria",
      "Necessidade explicita de inferencia segura em ambiente regulado",
    ],
    evidence: [
      "Site institucional destaca NLP clinico e leitura de exames",
      "Publicacoes do time mostram contratacao de ML engineers e MLOps",
      "Pitch deck menciona expansao para redes hospitalares",
    ],
    nextSteps: [
      "Validar profundidade do modelo proprietario versus fine-tuning",
      "Mapear potencial para PoC com inferencia acelerada",
      "Conectar com programa NVIDIA Inception para escalonamento",
    ],
    briefingExported: true,
    executiveBrief: {
      summary:
        "NeuralCare AI desponta como ativo prioritario para innovation scouting por combinar stack AI-native maduro, contexto regulado de alto valor e demanda clara por aceleracao de inferencia.",
      bullets: [
        {
          label: "Oportunidade",
          text: "Abrir relacao com healthtech de alto impacto que depende de processamento multimodal confiavel.",
        },
        {
          label: "Maturidade",
          text: "Time tecnico robusto, produto em operacao e sinais concretos de arquitetura propria.",
        },
        {
          label: "Riscos",
          text: "Ciclo de venda enterprise e exigencias regulatarias podem alongar conversao.",
        },
        {
          label: "Recomendacao",
          text: "Priorizar abordagem consultiva com trilha de Inception, NIM e AI Enterprise.",
        },
      ],
    },
    recommendations: [
      {
        name: "NVIDIA NIM",
        reason: "Acelera deploy de modelos clinicos e copilotos com governanca e padronizacao de inferencia.",
        adherence: "Muito alta",
        confidence: "92%",
        nextStep: "Propor arquitetura de inferencia para copiloto medico.",
      },
      {
        name: "NVIDIA AI Enterprise",
        reason: "Adequado para ambientes corporativos sensiveis com requisitos de seguranca e operacao.",
        adherence: "Alta",
        confidence: "89%",
        nextStep: "Explorar stack enterprise para hospitais e parceiros.",
      },
      {
        name: "NVIDIA Inception",
        reason: "Programa com forte aderencia para crescimento, networking e enablement tecnico.",
        adherence: "Alta",
        confidence: "87%",
        nextStep: "Iniciar trilha de relacionamento institucional.",
      },
    ],
  },
  {
    id: "agrovision-labs",
    name: "AgroVision Labs",
    segment: "agtech",
    city: "Campinas",
    aiScore: 88,
    nvidiaFit: 90,
    classification: "AI-native forte",
    validationStatus: "Validacao pendente",
    tags: ["Drone analytics", "Sensoriamento", "Computer vision"],
    summary:
      "Monitora lavouras com visao computacional, deteccao de pragas e previsao operacional para grandes fazendas.",
    description:
      "A AgroVision Labs desenvolve monitoramento agro com analise de imagens de drones e satelite para reduzir perdas e acelerar resposta a anomalias em campo.",
    signals: [
      "Uso intensivo de computer vision em escala territorial",
      "Base de dados proprietaria com imagens anotadas do agro brasileiro",
      "Busca por inferencia mais barata para operacao recorrente",
    ],
    evidence: [
      "Demonstra deteccao automatica de pragas em videos de drone",
      "Blog tecnico menciona pipelines de treinamento recorrente",
      "Apresentacao comercial destaca operacoes em usinas e grupos agro",
    ],
    nextSteps: [
      "Checar volume real de imagens processadas por safra",
      "Entender necessidade de edge inference versus cloud",
      "Priorizar conversa sobre Triton e GPUs para pipeline visual",
    ],
    briefingExported: false,
    executiveBrief: {
      summary:
        "AgroVision Labs apresenta excelente fit com workloads visuais e grande potencial para acelerar inferencia e operacao de modelos em escala no agro.",
      bullets: [
        {
          label: "Oportunidade",
          text: "Posicionar NVIDIA como base de processamento para CV aplicada ao campo.",
        },
        {
          label: "Maturidade",
          text: "Produto bem definido e sinais de base proprietaria relevante.",
        },
        {
          label: "Riscos",
          text: "Dependencia de sazonalidade e necessidade de comprovar escala economica.",
        },
        {
          label: "Recomendacao",
          text: "Abrir conversa tecnica orientada a performance de inferencia visual.",
        },
      ],
    },
    recommendations: [
      {
        name: "NVIDIA Triton Inference Server",
        reason: "Orquestra inferencia de modelos visuais com eficiencia para cargas variaveis.",
        adherence: "Muito alta",
        confidence: "91%",
        nextStep: "Simular throughput para analise de imagens de drone.",
      },
      {
        name: "CUDA / GPUs NVIDIA",
        reason: "Essencial para treinamento e inferencia de visao computacional em escala.",
        adherence: "Muito alta",
        confidence: "94%",
        nextStep: "Mapear stack atual e gargalos de processamento.",
      },
      {
        name: "NVIDIA DGX Cloud",
        reason: "Acelera experimentacao e treino de modelos proprietarios sem CAPEX inicial.",
        adherence: "Alta",
        confidence: "82%",
        nextStep: "Avaliar cenarios de treinamento sazonal intensivo.",
      },
    ],
  },
  {
    id: "fincore-intelligence",
    name: "FinCore Intelligence",
    segment: "fintech",
    city: "Sao Paulo",
    aiScore: 81,
    nvidiaFit: 78,
    classification: "AI-enabled com nucleo forte",
    validationStatus: "Em revisao",
    tags: ["Fraude", "Credito", "Decision intelligence"],
    summary:
      "Motor de decisao para credito e prevencao a fraude com modelos em tempo real para operacoes financeiras.",
    description:
      "A FinCore Intelligence combina score alternativo, deteccao de anomalias e explicabilidade para bancos, fintechs e emissores de credito digital.",
    signals: [
      "Modelos de risco em tempo real com baixa latencia",
      "Narrativa forte de automacao decisoria baseada em dados proprietarios",
      "Demanda crescente por escalabilidade e observabilidade de inferencia",
    ],
    evidence: [
      "Estudos de caso citam reducao de fraude e aumento de aprovacao",
      "Vagas indicam foco em data science aplicada a risco",
      "Materiais institucionais ressaltam APIs de decisao em tempo real",
    ],
    nextSteps: [
      "Validar volume e criticidade da inferencia transacional",
      "Investigar uso de LLMs versus modelos tabulares tradicionais",
      "Propor conversa sobre NIM para copilotos analiticos internos",
    ],
    briefingExported: true,
    executiveBrief: {
      summary:
        "FinCore Intelligence tem boa densidade tecnica e potencial moderado de fit NVIDIA, sobretudo em cenarios de inferencia de baixa latencia e copilotos analiticos.",
      bullets: [
        {
          label: "Oportunidade",
          text: "Atuar em uma fintech com casos claros de escalabilidade e risco em tempo real.",
        },
        {
          label: "Maturidade",
          text: "Modelo de negocio consolidado e stack de dados aparentemente estruturado.",
        },
        {
          label: "Riscos",
          text: "Parte da tese ainda pode depender mais de analytics classico do que de IA-native.",
        },
        {
          label: "Recomendacao",
          text: "Qualificar melhor a camada de modelos proprietarios antes de aprofundar engagement.",
        },
      ],
    },
    recommendations: [
      {
        name: "NVIDIA NIM",
        reason: "Pode habilitar copilotos e servicos de inferencia padronizados para times internos.",
        adherence: "Media",
        confidence: "74%",
        nextStep: "Explorar casos de copiloto para analistas de risco.",
      },
      {
        name: "NVIDIA AI Enterprise",
        reason: "Faz sentido se houver operacao enterprise com exigencia de confiabilidade e suporte.",
        adherence: "Media",
        confidence: "71%",
        nextStep: "Entender maturidade de MLOps e requisitos regulados.",
      },
      {
        name: "CUDA / GPUs NVIDIA",
        reason: "Pode otimizar treinamento de pipelines especificos, embora nao seja o principal driver inicial.",
        adherence: "Moderada",
        confidence: "68%",
        nextStep: "Identificar gargalos de treinamento mais pesados.",
      },
    ],
  },
  {
    id: "lexmind-ai",
    name: "LexMind AI",
    segment: "legaltech",
    city: "Rio de Janeiro",
    aiScore: 86,
    nvidiaFit: 84,
    classification: "AI-native forte",
    validationStatus: "Validado",
    tags: ["Legal copilots", "NLP", "Compliance"],
    summary:
      "Copiloto juridico para analise contratual, pesquisa jurisprudencial e automacao de fluxos de compliance.",
    description:
      "A LexMind AI opera uma camada juridica especializada com busca semantica, assistente generativo e mecanismos de rastreabilidade para uso corporativo.",
    signals: [
      "Uso de NLP verticalizado em dominio regulado",
      "Proposta clara de copiloto generativo para times juridicos",
      "Necessidade de governanca e rastreabilidade de respostas",
    ],
    evidence: [
      "Demonstra workflow de revisao contratual assistida",
      "Conteudos institucionais reforcam uso de IA generativa com citacoes",
      "Indicios de tracao com departamentos juridicos enterprise",
    ],
    nextSteps: [
      "Validar profundidade da camada proprietaria de retrieval",
      "Mapear requisitos de seguranca e deployment",
      "Investigar sinergia com NIM e AI Enterprise para copilotos",
    ],
    briefingExported: false,
    executiveBrief: {
      summary:
        "LexMind AI tem bom potencial de parceria por atuar em copilotos generativos verticais, com demanda por confiabilidade, governanca e operacao corporativa.",
      bullets: [
        {
          label: "Oportunidade",
          text: "Relacionamento com legaltech apta a mostrar valor de IA generativa vertical.",
        },
        {
          label: "Maturidade",
          text: "Tese bem posicionada e sinais consistentes de produto enterprise.",
        },
        {
          label: "Riscos",
          text: "Mercado competitivo e necessidade de comprovar diferenciacao tecnologica.",
        },
        {
          label: "Recomendacao",
          text: "Conduzir descoberta tecnica focada em inferencia, rastreabilidade e go-to-market.",
        },
      ],
    },
    recommendations: [
      {
        name: "NVIDIA NIM",
        reason: "Apoia stack de copilotos juridicos com servicos de inferencia mais padronizados.",
        adherence: "Alta",
        confidence: "88%",
        nextStep: "Explorar deployment de modelos para fluxos juridicos sensiveis.",
      },
      {
        name: "NVIDIA AI Enterprise",
        reason: "Adequado para clientes corporativos com exigencia de confiabilidade e suporte.",
        adherence: "Alta",
        confidence: "84%",
        nextStep: "Discutir arquitetura enterprise e observabilidade.",
      },
      {
        name: "NVIDIA Inception",
        reason: "Acelera conexoes comerciais e visibilidade para uma vertical promissora.",
        adherence: "Media",
        confidence: "76%",
        nextStep: "Avaliar enquadramento no programa.",
      },
    ],
  },
  {
    id: "retailflow-vision",
    name: "RetailFlow Vision",
    segment: "retail tech",
    city: "Belo Horizonte",
    aiScore: 90,
    nvidiaFit: 91,
    classification: "AI-native avancada",
    validationStatus: "Validacao pendente",
    tags: ["Loja autonoma", "Analytics", "Computer vision"],
    summary:
      "Monitora operacao de lojas e comportamento de consumo com visao computacional e insights em tempo real.",
    description:
      "A RetailFlow Vision entrega inteligencia operacional para varejo fisico, com deteccao de ruptura, heatmaps e analise de jornada em ambientes de alto fluxo.",
    signals: [
      "Computer vision em ambientes fisicos complexos",
      "Dependencia de baixa latencia para resposta operacional",
      "Uso potencial de edge e cloud para inferencia distribuida",
    ],
    evidence: [
      "Demos mostram analise de prateleira e fluxo em loja",
      "Discurso comercial reforca ROI operacional por visao computacional",
      "Sinais de integracao com grandes redes varejistas",
    ],
    nextSteps: [
      "Entender arquitetura de cameras, edge e cloud",
      "Quantificar necessidade de throughput e compressao de custos",
      "Discutir stack NVIDIA para operacao de inferencia visual continua",
    ],
    briefingExported: true,
    executiveBrief: {
      summary:
        "RetailFlow Vision representa um dos casos mais visiveis de fit NVIDIA no radar, com carga visual intensiva, tese clara de ROI e caminho direto para discussao tecnica.",
      bullets: [
        {
          label: "Oportunidade",
          text: "Relacionamento com startup que traduz aceleracao computacional em ganho de negocio imediato.",
        },
        {
          label: "Maturidade",
          text: "Produto bem articulado, sinais de clientes enterprise e caso de uso escalavel.",
        },
        {
          label: "Riscos",
          text: "Necessidade de validar economics de deploy em larga escala.",
        },
        {
          label: "Recomendacao",
          text: "Priorizar conversa com foco em visao computacional, edge e inferencia continua.",
        },
      ],
    },
    recommendations: [
      {
        name: "CUDA / GPUs NVIDIA",
        reason: "Base natural para treinar e servir workloads intensivos de visao computacional.",
        adherence: "Muito alta",
        confidence: "95%",
        nextStep: "Mapear frota atual e gargalos de processamento.",
      },
      {
        name: "NVIDIA Triton Inference Server",
        reason: "Suporta inferencia continua de modelos de visao em escala operacional.",
        adherence: "Muito alta",
        confidence: "92%",
        nextStep: "Simular ambiente multi-camera com throughput alvo.",
      },
      {
        name: "NVIDIA DGX Cloud",
        reason: "Pode reduzir friccao em treino e iteracao de novos modelos proprietarios.",
        adherence: "Alta",
        confidence: "81%",
        nextStep: "Avaliar janelas de treino e roadmap de expansao.",
      },
    ],
  },
];
