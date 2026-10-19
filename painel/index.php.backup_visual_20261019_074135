<!DOCTYPE html>
<html lang="pt-BR" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>VIGIA AI - Central de Segurança</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/core@latest/dist/css/tabler.min.css">
    <style>
        body { background: #10141c; }
        .navbar { background: #171d28; }
        .brand-mark { color: #48d597; }
        .camera-feed {
            display: block; width: 100%; min-height: 260px;
            max-height: 70vh; object-fit: contain; background: #080b10;
            border-radius: 8px;
        }
        .log-list { max-height: 540px; overflow-y: auto; }
        .log-item { padding: 12px 0; border-bottom: 1px solid #2b3442; }
        .log-item:last-child { border-bottom: 0; }
        .log-time { font-size: 12px; color: #9ba8bb; }
        .confidence { color: #ffca72; font-weight: 600; }
        .status-dot {
            display: inline-block; width: 8px; height: 8px;
            border-radius: 50%; margin-right: 7px; background: #f76707;
        }
        .status-dot.online { background: #2fb344; }
        .camera-placeholder {
            min-height: 260px; display: flex; flex-direction: column;
            align-items: center; justify-content: center; color: #9ba8bb;
            text-align: center; gap: 10px;
        }
    </style>
</head>
<body>
<div class="page">
    <header class="navbar">
        <div class="container-xl d-flex justify-content-between align-items-center py-3">
            <h1 class="navbar-brand m-0">
                <span class="brand-mark">VIGIA</span> AI
            </h1>
            <span class="badge bg-azure-lt">Monitoramento acadêmico</span>
        </div>
    </header>

    <div class="page-wrapper">
        <div class="page-header">
            <div class="container-xl">
                <div class="page-pretitle">Segurança inteligente</div>
                <h2 class="page-title">Central de monitoramento</h2>
                <div class="text-secondary mt-1" id="current-time">Carregando horário...</div>
            </div>
        </div>

        <div class="page-body">
            <div class="container-xl">
                <div class="row row-cards mb-3">
                    <div class="col-sm-6 col-lg-4">
                        <div class="card"><div class="card-body">
                            <div class="subheader">Transmissão da câmera</div>
                            <div class="h1 mb-0" id="camera-status">Conectando...</div>
                            <div class="text-secondary mt-2" id="camera-label">CAMERA_01</div>
                        </div></div>
                    </div>
                    <div class="col-sm-6 col-lg-4">
                        <div class="card"><div class="card-body">
                            <div class="subheader">Detecções registradas hoje</div>
                            <div class="h1 mb-0" id="total-events">—</div>
                            <div class="text-secondary mt-2">Eventos salvos no MariaDB</div>
                        </div></div>
                    </div>
                    <div class="col-sm-6 col-lg-4">
                        <div class="card"><div class="card-body">
                            <div class="subheader">Sistema de detecção</div>
                            <div class="h1 mb-0 text-success">YOLO</div>
                            <div class="text-secondary mt-2">Processamento realizado pelo Python</div>
                        </div></div>
                    </div>
                </div>

                <div class="row row-cards">
                    <div class="col-lg-8">
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title">Monitoramento ao vivo</h3>
                                <div class="card-actions">
                                    <span class="badge bg-red-lt">AO VIVO</span>
                                </div>
                            </div>
                            <div class="card-body">
                                <img
                                    id="camera-feed"
                                    class="camera-feed"
                                    src="http://127.0.0.1:8765/stream.mjpg"
                                    alt="Transmissão da câmera do sistema VIGIA AI"
                                >
                                <div id="camera-error" class="camera-placeholder" hidden>
                                    <div class="h3">Transmissão indisponível</div>
                                    <div>Inicie o detector executando tests/test_camera.py.</div>
                                </div>
                            </div>
                            <div class="card-footer text-secondary">
                                A imagem é fornecida pelo detector Python e pode incluir as marcações do YOLO.
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-4">
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title">Log de eventos</h3>
                                <div class="card-actions">
                                    <span class="badge bg-secondary-lt" id="log-status">Atualizando</span>
                                </div>
                            </div>
                            <div class="card-body log-list" id="event-log">
                                <div class="text-secondary">Carregando eventos...</div>
                            </div>
                            <div class="card-footer text-secondary">
                                Atualização automática a cada 2,5 segundos
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="footer footer-transparent">
            <div class="container-xl text-center text-secondary">
                VIGIA AI · Sistema de visão computacional · Projeto acadêmico
            </div>
        </footer>
    </div>
</div>

<script>
(() => {
    const feed = document.getElementById('camera-feed');
    const cameraStatus = document.getElementById('camera-status');
    const cameraError = document.getElementById('camera-error');
    const eventLog = document.getElementById('event-log');
    const logStatus = document.getElementById('log-status');

    function updateClock() {
        document.getElementById('current-time').textContent =
            new Date().toLocaleString('pt-BR');
    }
    updateClock();
    setInterval(updateClock, 1000);

    feed.onload = () => {
        cameraStatus.textContent = 'Online';
        cameraStatus.className = 'h1 mb-0 text-success';
        cameraError.hidden = true;
        feed.hidden = false;
    };

    feed.onerror = () => {
        cameraStatus.textContent = 'Offline';
        cameraStatus.className = 'h1 mb-0 text-danger';
        cameraError.hidden = false;
        feed.hidden = true;
    };

    function addText(parent, tag, text, className = '') {
        const element = document.createElement(tag);
        element.textContent = text ?? '';
        if (className) element.className = className;
        parent.appendChild(element);
        return element;
    }

    async function loadEvents() {
        try {
            const response = await fetch('api/eventos.php', { cache: 'no-store' });
            if (!response.ok) throw new Error('HTTP ' + response.status);
            const data = await response.json();
            if (!data.sucesso) throw new Error('Resposta inválida');

            document.getElementById('total-events').textContent = data.total_hoje;
            eventLog.replaceChildren();

            if (!data.eventos.length) {
                addText(eventLog, 'div', 'Nenhum alerta registrado hoje.', 'text-secondary');
            } else {
                for (const event of data.eventos) {
                    const item = document.createElement('div');
                    item.className = 'log-item';

                    const header = document.createElement('div');
                    header.className = 'd-flex justify-content-between align-items-start gap-2';
                    addText(header, 'strong', event.tipo || 'DETECÇÃO');
                    addText(header, 'span', '#' + event.id, 'text-secondary');
                    item.appendChild(header);

                    addText(item, 'div', 'Câmera: ' + (event.camera || 'Não informada'));
                    addText(item, 'div',
                        'Horário: ' + (event.criado_em || 'Não informado'),
                        'log-time');

                    if (event.confianca !== null) {
                        const confidence = Number(event.confianca) * 100;
                        addText(item, 'div',
                            'Confiança: ' + confidence.toFixed(1) + '%',
                            'confidence');
                    }
                    if (event.track_id !== null) {
                        addText(item, 'div', 'Rastreamento: #' + event.track_id, 'text-secondary');
                    }

                    eventLog.appendChild(item);
                }
            }

            logStatus.textContent = 'Conectado';
            logStatus.className = 'badge bg-success-lt';
        } catch (error) {
            logStatus.textContent = 'Erro de conexão';
            logStatus.className = 'badge bg-danger-lt';
            eventLog.replaceChildren();
            addText(eventLog, 'div',
                'Não foi possível carregar o histórico. Verifique o PHP e o MariaDB.',
                'text-secondary');
            console.error('VIGIA AI:', error);
        }
    }

    loadEvents();
    setInterval(loadEvents, 2500);
})();
</script>
<script src="https://cdn.jsdelivr.net/npm/@tabler/core@latest/dist/js/tabler.min.js"></script>
</body>
</html>
