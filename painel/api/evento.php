<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['erro' => 'Use POST']);
    exit;
}

$tokenEsperado = getenv('VIGIA_API_TOKEN') ?: '';

$tokenRecebido = $_SERVER['HTTP_X_VIGIA_TOKEN'] ?? '';

if ($tokenEsperado === '' || !hash_equals($tokenEsperado, $tokenRecebido)) {
    http_response_code(401);
    echo json_encode(['erro' => 'Nao autorizado']);
    exit;
}

$dados = json_decode(file_get_contents('php://input'), true);

if (!is_array($dados)) {
    http_response_code(400);
    echo json_encode(['erro' => 'JSON invalido']);
    exit;
}

$confianca = $dados['confianca'] ?? null;
$camera = $dados['camera'] ?? 'CAMERA_01';
$trackId = $dados['track_id'] ?? null;

if (
    ($confianca !== null &&
        (!is_numeric($confianca) || $confianca < 0 || $confianca > 1)) ||
    !is_string($camera) ||
    strlen($camera) > 100 ||
    ($trackId !== null &&
        (!is_int($trackId) || $trackId < 0))
) {
    http_response_code(400);
    echo json_encode(['erro' => 'Dados invalidos']);
    exit;
}

try {
    require __DIR__ . '/../includes/db.php';

    $stmt = $pdo->prepare(
        'INSERT INTO eventos (tipo, camera, confianca, track_id)
         VALUES (:tipo, :camera, :confianca, :track_id)'
    );

    $stmt->execute([
        'tipo' => 'FACA_DETECTADA',
        'camera' => $camera,
        'confianca' => $confianca,
        'track_id' => $trackId,
    ]);

    http_response_code(201);
    echo json_encode([
        'sucesso' => true,
        'id' => (int) $pdo->lastInsertId(),
    ]);
} catch (Throwable $e) {
    error_log('Falha ao registrar evento VIGIA AI: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['erro' => 'Falha ao registrar evento']);
}
